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
from models import Order, OrderItem, CartItem, Book, User, OrderStatus
from schemas import (
    OrderResponse,
    OrderListResponse,
    OrderCreate,
    OrderCancel,
    OrderShip,
    OrderAdminUpdate,
    OrderItemSnapshot
)
from auth import get_current_active_user, get_current_admin_user

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
    return OrderResponse(
        id=order.id,
        order_no=order.order_no,
        user_id=order.user_id,
        total_amount=order.total_amount,
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
        items=items
    )


# ========== 用户端API ==========
@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    order_create: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建订单（从购物车勾选商品）"""
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

        total_amount = 0.0
        order_no = _generate_order_no()

        db_order = Order(
            order_no=order_no,
            user_id=current_user.id,
            total_amount=0.0,
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
            total_amount += subtotal

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

        db_order.total_amount = round(total_amount, 2)

        db.commit()
        db.refresh(db_order)

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

        order.status = OrderStatus.CANCELLED
        order.cancel_reason = cancel_data.cancel_reason

        db.commit()
        db.refresh(order)

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
        order.status = OrderStatus.SHIPPED
        order.tracking_company = ship_data.tracking_company
        order.tracking_number = ship_data.tracking_number
        if ship_data.admin_remark:
            order.admin_remark = ship_data.admin_remark
        order.shipped_at = datetime.utcnow()

        db.commit()
        db.refresh(order)

        logger.info(f"订单发货成功: 管理员 {current_user.username}, 订单号 {order.order_no}, 物流公司 {ship_data.tracking_company}, 单号 {ship_data.tracking_number}")
        return _get_order_response(db, order)

    except Exception as e:
        db.rollback()
        logger.error(f"订单发货失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="订单发货失败，请稍后重试"
        )
