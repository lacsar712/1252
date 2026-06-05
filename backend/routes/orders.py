# -*- coding: utf-8 -*-
"""
订单管理路由
"""
import logging
import random
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from database import get_db
from models import (
    Order, OrderItem, CartItem, Book, User, OrderStatus,
    UserCoupon, UserCouponStatus, Coupon, CouponStatus
)
from schemas import (
    OrderResponse,
    OrderListResponse,
    OrderCreate,
    OrderCancel,
    OrderShip,
    OrderAdminUpdate,
    OrderItemSnapshot,
    OrderCreateWithCoupon,
    UserCouponResponse,
    CouponResponse
)
from auth import get_current_active_user, get_current_admin_user
from message_service import send_order_status_message, send_delivery_reminder

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/orders", tags=["订单管理"])


def _generate_order_no() -> str:
    """生成订单编号：ORD + 时间戳(YYYYMMDDHHMMSS) + 6位随机数"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_num = str(random.randint(100000, 999999))
    return f"ORD{timestamp}{random_num}"


def _get_order_items_snapshot(db: Session, order_id: int) -> List[OrderItemSnapshot]:
    """获取订单项快照列表"""
    order_items = db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
    return [
        OrderItemSnapshot(
            book_id=item.book_id,
            book_title=item.book_title,
            book_author=item.book_author,
            book_price=item.book_price,
            book_cover=item.book_cover,
            quantity=item.quantity,
            subtotal=item.subtotal
        )
        for item in order_items
    ]


def _get_order_response(db: Session, order: Order) -> OrderResponse:
    """获取订单响应对象"""
    items = _get_order_items_snapshot(db, order.id)

    used_coupon = None
    if order.user_coupon_id:
        user_coupon = db.query(UserCoupon).filter(UserCoupon.id == order.user_coupon_id).first()
        if user_coupon:
            used_coupon = UserCouponResponse(
                id=user_coupon.id,
                coupon_id=user_coupon.coupon_id,
                user_id=user_coupon.user_id,
                status=user_coupon.status,
                order_id=user_coupon.order_id,
                used_at=user_coupon.used_at,
                claimed_at=user_coupon.claimed_at,
                coupon=CouponResponse.model_validate(user_coupon.coupon)
            )

    return OrderResponse(
        id=order.id,
        order_no=order.order_no,
        user_id=order.user_id,
        total_amount=order.total_amount,
        original_amount=order.original_amount,
        discount_amount=order.discount_amount,
        user_coupon_id=order.user_coupon_id,
        status=order.status,
        receiver_name=order.receiver_name,
        receiver_phone=order.receiver_phone,
        receiver_address=order.receiver_address,
        remark=order.remark,
        cancel_reason=order.cancel_reason,
        admin_remark=order.admin_remark,
        tracking_company=order.tracking_company,
        tracking_number=order.tracking_number,
        paid_at=order.paid_at,
        shipped_at=order.shipped_at,
        delivered_at=order.delivered_at,
        created_at=order.created_at,
        updated_at=order.updated_at,
        items=items,
        used_coupon=used_coupon
    )


def _validate_and_calculate_coupon(
    db: Session,
    user_coupon_id: int,
    current_user: User,
    cart_items: List[CartItem],
    total_amount: float
) -> tuple[UserCoupon, float]:
    """验证优惠券并计算优惠金额

    Returns:
        (user_coupon, discount_amount)
    """
    user_coupon = db.query(UserCoupon).filter(
        UserCoupon.id == user_coupon_id,
        UserCoupon.user_id == current_user.id
    ).with_for_update().first()

    if not user_coupon:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="优惠券不存在"
        )

    if user_coupon.status != UserCouponStatus.UNUSED:
        if user_coupon.status == UserCouponStatus.USED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="优惠券已使用"
            )
        elif user_coupon.status == UserCouponStatus.EXPIRED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="优惠券已过期"
            )
        elif user_coupon.status == UserCouponStatus.LOCKED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="优惠券已被其他订单占用"
            )

    coupon = user_coupon.coupon

    if coupon.status != CouponStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="优惠券已下架"
        )

    now = datetime.utcnow()
    if now < coupon.valid_from:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="优惠券尚未生效"
        )
    if now > coupon.valid_to:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="优惠券已过期"
        )

    if total_amount < coupon.threshold_amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"订单金额不足 ¥{coupon.threshold_amount:.2f}，无法使用该优惠券"
        )

    applicable_categories = []
    if coupon.applicable_categories:
        applicable_categories = [cat.strip() for cat in coupon.applicable_categories.split(",") if cat.strip()]

    if applicable_categories:
        book_categories = []
        for cart_item in cart_items:
            book = db.query(Book).filter(Book.id == cart_item.book_id).first()
            if book and book.category and book.category not in book_categories:
                book_categories.append(book.category)

        if not any(cat in applicable_categories for cat in book_categories):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="订单中没有符合该优惠券适用分类的商品"
            )

    discount_amount = coupon.discount_amount
    if discount_amount > total_amount:
        discount_amount = total_amount

    return user_coupon, discount_amount


# ========== 用户端API ==========
@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    order_create: OrderCreateWithCoupon,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建订单（从购物车勾选商品，支持优惠券抵扣）"""
    try:
        if order_create.cart_item_ids:
            cart_items = db.query(CartItem).filter(
                CartItem.user_id == current_user.id,
                CartItem.id.in_(order_create.cart_item_ids),
                CartItem.selected == True
            ).with_for_update().all()
        else:
            cart_items = db.query(CartItem).filter(
                CartItem.user_id == current_user.id,
                CartItem.selected == True
            ).with_for_update().all()

        if not cart_items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="请先选择要购买的商品"
            )

        for cart_item in cart_items:
            book = db.query(Book).filter(Book.id == cart_item.book_id).with_for_update().first()
            if not book:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"图书ID {cart_item.book_id} 不存在"
                )
            if book.stock < cart_item.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"图书《{book.title}》库存不足，当前库存 {book.stock} 本"
                )

        original_amount = 0.0
        for cart_item in cart_items:
            book = db.query(Book).filter(Book.id == cart_item.book_id).first()
            original_amount += book.price * cart_item.quantity
        original_amount = round(original_amount, 2)

        discount_amount = 0.0
        user_coupon = None
        if order_create.user_coupon_id:
            user_coupon, discount_amount = _validate_and_calculate_coupon(
                db, order_create.user_coupon_id, current_user, cart_items, original_amount
            )

        total_amount = round(original_amount - discount_amount, 2)
        if total_amount < 0:
            total_amount = 0.0

        order_no = _generate_order_no()

        db_order = Order(
            order_no=order_no,
            user_id=current_user.id,
            total_amount=total_amount,
            original_amount=original_amount,
            discount_amount=discount_amount,
            user_coupon_id=order_create.user_coupon_id,
            status=OrderStatus.PENDING,
            receiver_name=order_create.receiver_name,
            receiver_phone=order_create.receiver_phone,
            receiver_address=order_create.receiver_address,
            remark=order_create.remark
        )
        db.add(db_order)
        db.flush()

        for cart_item in cart_items:
            book = db.query(Book).filter(Book.id == cart_item.book_id).first()
            book.stock -= cart_item.quantity

            subtotal = round(book.price * cart_item.quantity, 2)

            db_order_item = OrderItem(
                order_id=db_order.id,
                book_id=book.id,
                book_title=book.title,
                book_author=book.author,
                book_price=book.price,
                book_cover=book.cover_image,
                quantity=cart_item.quantity,
                subtotal=subtotal
            )
            db.add(db_order_item)

            db.delete(cart_item)

        if user_coupon:
            user_coupon.status = UserCouponStatus.USED
            user_coupon.order_id = db_order.id
            user_coupon.used_at = datetime.utcnow()

        db.commit()
        db.refresh(db_order)

        if discount_amount > 0:
            logger.info(f"订单创建成功: 用户 {current_user.username}, 订单号 {order_no}, 原价 {original_amount:.2f}, 优惠 {discount_amount:.2f}, 实付 {total_amount:.2f}")
        else:
            logger.info(f"订单创建成功: 用户 {current_user.username}, 订单号 {order_no}, 金额 {total_amount:.2f}")
        return _get_order_response(db, db_order)

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"创建订单失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建订单失败，请稍后重试"
        )


@router.get("/my", response_model=OrderListResponse)
def get_my_orders(
    status: Optional[str] = Query(None, description="订单状态筛选"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取我的订单列表，支持按状态筛选"""
    query = db.query(Order).filter(Order.user_id == current_user.id)

    if status:
        valid_statuses = [OrderStatus.PENDING, OrderStatus.CONFIRMED, OrderStatus.SHIPPED, OrderStatus.DELIVERED, OrderStatus.CANCELLED]
        if status not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的订单状态，有效值为: {', '.join(valid_statuses)}"
            )
        query = query.filter(Order.status == status)

    total = query.count()
    orders = query.order_by(Order.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    items = [_get_order_response(db, order) for order in orders]

    return OrderListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=items
    )


@router.get("/{order_id}", response_model=OrderResponse)
def get_order_detail(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取订单详情"""
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id
    ).first()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )

    return _get_order_response(db, order)


@router.post("/{order_id}/cancel", response_model=OrderResponse)
def cancel_order(
    order_id: int,
    cancel_data: OrderCancel,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """取消未处理订单"""
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id
    ).first()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )

    if order.status != OrderStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只能取消待处理状态的订单"
        )

    try:
        order_items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()

        for item in order_items:
            book = db.query(Book).filter(Book.id == item.book_id).with_for_update().first()
            if book:
                book.stock += item.quantity

        if order.user_coupon_id:
            user_coupon = db.query(UserCoupon).filter(
                UserCoupon.id == order.user_coupon_id,
                UserCoupon.status == UserCouponStatus.USED
            ).first()
            if user_coupon:
                user_coupon.status = UserCouponStatus.UNUSED
                user_coupon.order_id = None
                user_coupon.used_at = None
                logger.info(f"优惠券已退回: 用户 {current_user.username}, 用户优惠券ID {user_coupon.id}")

        old_status = order.status
        order.status = OrderStatus.CANCELLED
        order.cancel_reason = cancel_data.cancel_reason

        db.commit()
        db.refresh(order)

        send_order_status_message(
            db=db,
            order=order,
            old_status=old_status,
            new_status=order.status
        )

        logger.info(f"订单取消成功: 用户 {current_user.username}, 订单号 {order.order_no}, 原因: {cancel_data.cancel_reason}")
        return _get_order_response(db, order)

    except Exception as e:
        db.rollback()
        logger.error(f"取消订单失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="取消订单失败，请稍后重试"
        )


# ========== 管理端API ==========
@router.get("", response_model=OrderListResponse)
def get_all_orders(
    status: Optional[str] = Query(None, description="订单状态筛选"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """获取全部订单列表，支持按状态筛选（管理员）"""
    query = db.query(Order)

    if status:
        valid_statuses = [OrderStatus.PENDING, OrderStatus.CONFIRMED, OrderStatus.SHIPPED, OrderStatus.DELIVERED, OrderStatus.CANCELLED]
        if status not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的订单状态，有效值为: {', '.join(valid_statuses)}"
            )
        query = query.filter(Order.status == status)

    total = query.count()
    orders = query.order_by(Order.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    items = [_get_order_response(db, order) for order in orders]

    return OrderListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=items
    )


@router.patch("/{order_id}/admin", response_model=OrderResponse)
def update_order_admin(
    order_id: int,
    update_data: OrderAdminUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """更新订单状态、管理员备注、发货信息（管理员）"""
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )

    valid_transitions = {
        OrderStatus.PENDING: [OrderStatus.CONFIRMED, OrderStatus.CANCELLED],
        OrderStatus.CONFIRMED: [OrderStatus.SHIPPED],
        OrderStatus.SHIPPED: [OrderStatus.DELIVERED],
        OrderStatus.DELIVERED: [],
        OrderStatus.CANCELLED: []
    }

    old_status = order.status
    status_changed = False

    if update_data.status:
        valid_statuses = [OrderStatus.PENDING, OrderStatus.CONFIRMED, OrderStatus.SHIPPED, OrderStatus.DELIVERED, OrderStatus.CANCELLED]
        if update_data.status not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的订单状态，有效值为: {', '.join(valid_statuses)}"
            )

        if update_data.status != order.status:
            if update_data.status not in valid_transitions.get(order.status, []):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"无法从 {order.status} 状态变更为 {update_data.status} 状态"
                )

            if update_data.status == OrderStatus.SHIPPED:
                if not (update_data.tracking_company or order.tracking_company) or not (update_data.tracking_number or order.tracking_number):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="发货状态需要填写物流公司和物流单号"
                    )

            order.status = update_data.status
            status_changed = True
            now = datetime.utcnow()

            if update_data.status == OrderStatus.CONFIRMED:
                order.paid_at = now
            elif update_data.status == OrderStatus.SHIPPED:
                order.shipped_at = now
            elif update_data.status == OrderStatus.DELIVERED:
                order.delivered_at = now

    if update_data.admin_remark is not None:
        order.admin_remark = update_data.admin_remark

    if update_data.tracking_company is not None:
        order.tracking_company = update_data.tracking_company

    if update_data.tracking_number is not None:
        order.tracking_number = update_data.tracking_number

    db.commit()
    db.refresh(order)

    if status_changed:
        send_order_status_message(
            db=db,
            order=order,
            old_status=old_status,
            new_status=order.status,
            sender_id=current_user.id
        )

        if order.status == OrderStatus.DELIVERED:
            send_delivery_reminder(
                db=db,
                order=order,
                sender_id=current_user.id
            )

    logger.info(f"管理员更新订单: 管理员 {current_user.username}, 订单号 {order.order_no}, 新状态 {order.status}")
    return _get_order_response(db, order)


@router.post("/{order_id}/ship", response_model=OrderResponse)
def ship_order(
    order_id: int,
    ship_data: OrderShip,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """订单发货（管理员）"""
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )

    if order.status != OrderStatus.CONFIRMED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只能对已确认状态的订单进行发货操作"
        )

    try:
        old_status = order.status
        order.status = OrderStatus.SHIPPED
        order.tracking_company = ship_data.tracking_company
        order.tracking_number = ship_data.tracking_number
        if ship_data.admin_remark:
            order.admin_remark = ship_data.admin_remark
        order.shipped_at = datetime.utcnow()

        db.commit()
        db.refresh(order)

        send_order_status_message(
            db=db,
            order=order,
            old_status=old_status,
            new_status=order.status,
            sender_id=current_user.id
        )

        logger.info(f"订单发货成功: 管理员 {current_user.username}, 订单号 {order.order_no}, 物流公司 {ship_data.tracking_company}, 单号 {ship_data.tracking_number}")
        return _get_order_response(db, order)

    except Exception as e:
        db.rollback()
        logger.error(f"订单发货失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="订单发货失败，请稍后重试"
        )
