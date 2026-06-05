# -*- coding: utf-8 -*-
"""
优惠券管理路由
"""
import logging
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from database import get_db
from models import (
    Coupon, UserCoupon, User, CouponStatus, UserCouponStatus,
    CartItem, Book
)
from schemas import (
    CouponResponse, CouponListResponse, CouponCreate, CouponUpdate,
    UserCouponResponse, UserCouponListResponse, CouponClaimResponse,
    AvailableCouponResponse, OrderCouponValidateRequest
)
from auth import get_current_active_user, get_current_admin_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/coupons", tags=["优惠券管理"])


def _parse_categories(categories_str: Optional[str]) -> List[str]:
    """解析分类字符串为列表"""
    if not categories_str:
        return []
    return [cat.strip() for cat in categories_str.split(",") if cat.strip()]


def _check_coupon_availability(
    user_coupon: UserCoupon,
    total_amount: float,
    book_categories: List[str],
    now: datetime
) -> tuple[bool, Optional[str]]:
    """检查用户优惠券是否可用

    Returns:
        (is_available, unavailable_reason)
    """
    coupon = user_coupon.coupon

    if user_coupon.status != UserCouponStatus.UNUSED:
        if user_coupon.status == UserCouponStatus.USED:
            return False, "优惠券已使用"
        elif user_coupon.status == UserCouponStatus.EXPIRED:
            return False, "优惠券已过期"
        elif user_coupon.status == UserCouponStatus.LOCKED:
            return False, "优惠券已被其他订单占用"

    if coupon.status != CouponStatus.ACTIVE:
        return False, "优惠券已下架"

    if now < coupon.valid_from:
        return False, "优惠券尚未生效"

    if now > coupon.valid_to:
        return False, "优惠券已过期"

    if total_amount < coupon.threshold_amount:
        return False, f"订单金额不足 ¥{coupon.threshold_amount:.2f}"

    applicable_categories = _parse_categories(coupon.applicable_categories)
    if applicable_categories:
        if not any(cat in applicable_categories for cat in book_categories):
            return False, "订单中没有符合分类的商品"

    return True, None


def _get_user_coupon_response(
    db: Session,
    user_coupon: UserCoupon,
    total_amount: Optional[float] = None,
    book_categories: Optional[List[str]] = None
) -> UserCouponResponse:
    """获取用户优惠券响应对象，包含可用性判断"""
    now = datetime.utcnow()

    if user_coupon.status == UserCouponStatus.UNUSED:
        coupon = user_coupon.coupon
        if now > coupon.valid_to:
            user_coupon.status = UserCouponStatus.EXPIRED
            db.commit()

    is_available = True
    unavailable_reason = None

    if total_amount is not None and book_categories is not None:
        is_available, unavailable_reason = _check_coupon_availability(
            user_coupon, total_amount, book_categories, now
        )

    return UserCouponResponse(
        id=user_coupon.id,
        coupon_id=user_coupon.coupon_id,
        user_id=user_coupon.user_id,
        status=user_coupon.status,
        order_id=user_coupon.order_id,
        used_at=user_coupon.used_at,
        claimed_at=user_coupon.claimed_at,
        coupon=CouponResponse.model_validate(user_coupon.coupon),
        is_available=is_available,
        unavailable_reason=unavailable_reason
    )


# ========== 管理员API ==========
@router.get("/admin", response_model=CouponListResponse)
def get_all_coupons_admin(
    status: Optional[str] = Query(None, description="优惠券状态筛选"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """获取所有优惠券列表（管理员）"""
    query = db.query(Coupon)

    if status:
        valid_statuses = [CouponStatus.ACTIVE, CouponStatus.INACTIVE, CouponStatus.EXPIRED, CouponStatus.SOLD_OUT]
        if status not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的优惠券状态，有效值为: {', '.join(valid_statuses)}"
            )
        query = query.filter(Coupon.status == status)

    total = query.count()
    coupons = query.order_by(Coupon.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    now = datetime.utcnow()
    for coupon in coupons:
        if coupon.status == CouponStatus.ACTIVE and now > coupon.valid_to:
            coupon.status = CouponStatus.EXPIRED
        if coupon.status == CouponStatus.ACTIVE and coupon.claimed_quantity >= coupon.total_quantity:
            coupon.status = CouponStatus.SOLD_OUT
    db.commit()

    return CouponListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[CouponResponse.model_validate(c) for c in coupons]
    )


@router.get("/admin/{coupon_id}", response_model=CouponResponse)
def get_coupon_detail_admin(
    coupon_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """获取优惠券详情（管理员）"""
    coupon = db.query(Coupon).filter(Coupon.id == coupon_id).first()

    if not coupon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="优惠券不存在"
        )

    return CouponResponse.model_validate(coupon)


@router.post("", response_model=CouponResponse, status_code=status.HTTP_201_CREATED)
def create_coupon(
    coupon_create: CouponCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """创建优惠券（管理员）"""
    if coupon_create.valid_from >= coupon_create.valid_to:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="有效期开始时间必须早于结束时间"
        )

    if coupon_create.discount_amount > coupon_create.threshold_amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="优惠金额不能大于门槛金额"
        )

    db_coupon = Coupon(
        name=coupon_create.name,
        description=coupon_create.description,
        threshold_amount=coupon_create.threshold_amount,
        discount_amount=coupon_create.discount_amount,
        valid_from=coupon_create.valid_from,
        valid_to=coupon_create.valid_to,
        total_quantity=coupon_create.total_quantity,
        claimed_quantity=0,
        limit_per_user=coupon_create.limit_per_user,
        applicable_categories=coupon_create.applicable_categories,
        status=coupon_create.status
    )

    db.add(db_coupon)
    db.commit()
    db.refresh(db_coupon)

    logger.info(f"管理员创建优惠券: {current_user.username}, 优惠券: {db_coupon.name}")
    return CouponResponse.model_validate(db_coupon)


@router.put("/{coupon_id}", response_model=CouponResponse)
def update_coupon(
    coupon_id: int,
    coupon_update: CouponUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """更新优惠券（管理员）"""
    coupon = db.query(Coupon).filter(Coupon.id == coupon_id).first()

    if not coupon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="优惠券不存在"
        )

    valid_from = coupon_update.valid_from if coupon_update.valid_from is not None else coupon.valid_from
    valid_to = coupon_update.valid_to if coupon_update.valid_to is not None else coupon.valid_to

    if valid_from >= valid_to:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="有效期开始时间必须早于结束时间"
        )

    discount_amount = coupon_update.discount_amount if coupon_update.discount_amount is not None else coupon.discount_amount
    threshold_amount = coupon_update.threshold_amount if coupon_update.threshold_amount is not None else coupon.threshold_amount

    if discount_amount > threshold_amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="优惠金额不能大于门槛金额"
        )

    update_data = coupon_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(coupon, field, value)

    db.commit()
    db.refresh(coupon)

    logger.info(f"管理员更新优惠券: {current_user.username}, 优惠券ID: {coupon_id}")
    return CouponResponse.model_validate(coupon)


@router.delete("/{coupon_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_coupon(
    coupon_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """删除优惠券（管理员）"""
    coupon = db.query(Coupon).filter(Coupon.id == coupon_id).first()

    if not coupon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="优惠券不存在"
        )

    if coupon.claimed_quantity > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="已有用户领取的优惠券无法删除，请先停用"
        )

    db.delete(coupon)
    db.commit()

    logger.info(f"管理员删除优惠券: {current_user.username}, 优惠券ID: {coupon_id}")


# ========== 用户端API ==========
@router.get("/available", response_model=CouponListResponse)
def get_available_coupons(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取可领取的优惠券列表"""
    now = datetime.utcnow()

    query = db.query(Coupon).filter(
        Coupon.status == CouponStatus.ACTIVE,
        Coupon.valid_from <= now,
        Coupon.valid_to >= now,
        Coupon.claimed_quantity < Coupon.total_quantity
    )

    total = query.count()
    coupons = query.order_by(Coupon.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    for coupon in coupons:
        if coupon.claimed_quantity >= coupon.total_quantity:
            coupon.status = CouponStatus.SOLD_OUT
    db.commit()

    return CouponListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[CouponResponse.model_validate(c) for c in coupons]
    )


@router.post("/{coupon_id}/claim", response_model=CouponClaimResponse)
def claim_coupon(
    coupon_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """领取优惠券"""
    coupon = db.query(Coupon).filter(Coupon.id == coupon_id).with_for_update().first()

    if not coupon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="优惠券不存在"
        )

    now = datetime.utcnow()

    if coupon.status != CouponStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="优惠券已下架"
        )

    if now < coupon.valid_from or now > coupon.valid_to:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="优惠券不在有效期内"
        )

    if coupon.claimed_quantity >= coupon.total_quantity:
        coupon.status = CouponStatus.SOLD_OUT
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="优惠券已被领完"
        )

    user_claimed_count = db.query(UserCoupon).filter(
        UserCoupon.coupon_id == coupon_id,
        UserCoupon.user_id == current_user.id
    ).count()

    if user_claimed_count >= coupon.limit_per_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"您已达到领取上限（每人限领{coupon.limit_per_user}张）"
        )

    user_coupon = UserCoupon(
        coupon_id=coupon_id,
        user_id=current_user.id,
        status=UserCouponStatus.UNUSED
    )

    db.add(user_coupon)
    coupon.claimed_quantity += 1

    if coupon.claimed_quantity >= coupon.total_quantity:
        coupon.status = CouponStatus.SOLD_OUT

    db.commit()
    db.refresh(user_coupon)

    logger.info(f"用户领取优惠券: {current_user.username}, 优惠券: {coupon.name}")

    return CouponClaimResponse(
        message="领取成功",
        user_coupon=_get_user_coupon_response(db, user_coupon)
    )


@router.get("/my", response_model=UserCouponListResponse)
def get_my_coupons(
    status: Optional[str] = Query(None, description="优惠券状态: unused/used/expired"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取我的优惠券列表"""
    query = db.query(UserCoupon).filter(UserCoupon.user_id == current_user.id)

    now = datetime.utcnow()
    all_user_coupons = query.all()
    for uc in all_user_coupons:
        if uc.status == UserCouponStatus.UNUSED and now > uc.coupon.valid_to:
            uc.status = UserCouponStatus.EXPIRED
    db.commit()

    if status:
        valid_statuses = [UserCouponStatus.UNUSED, UserCouponStatus.USED, UserCouponStatus.EXPIRED]
        if status not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的状态，有效值为: {', '.join(valid_statuses)}"
            )
        query = query.filter(UserCoupon.status == status)

    query = query.order_by(UserCoupon.claimed_at.desc())

    total = query.count()
    user_coupons = query.offset((page - 1) * page_size).limit(page_size).all()

    items = [_get_user_coupon_response(db, uc) for uc in user_coupons]

    return UserCouponListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=items
    )


@router.post("/validate-for-order", response_model=AvailableCouponResponse)
def validate_coupons_for_order(
    request: OrderCouponValidateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取当前订单可用的优惠券列表"""
    cart_items = db.query(CartItem).filter(
        CartItem.user_id == current_user.id,
        CartItem.id.in_(request.cart_item_ids),
        CartItem.selected == True
    ).all()

    if not cart_items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请先选择要购买的商品"
        )

    total_amount = 0.0
    book_categories: List[str] = []

    for cart_item in cart_items:
        book = db.query(Book).filter(Book.id == cart_item.book_id).first()
        if not book:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"图书ID {cart_item.book_id} 不存在"
            )
        total_amount += book.price * cart_item.quantity
        if book.category and book.category not in book_categories:
            book_categories.append(book.category)

    total_amount = round(total_amount, 2)

    user_coupons = db.query(UserCoupon).filter(
        UserCoupon.user_id == current_user.id,
        UserCoupon.status.in_([UserCouponStatus.UNUSED, UserCouponStatus.LOCKED])
    ).order_by(UserCoupon.claimed_at.desc()).all()

    available: List[UserCouponResponse] = []
    unavailable: List[UserCouponResponse] = []

    for uc in user_coupons:
        resp = _get_user_coupon_response(db, uc, total_amount, book_categories)
        if resp.is_available:
            available.append(resp)
        else:
            unavailable.append(resp)

    available.sort(key=lambda x: x.coupon.discount_amount, reverse=True)

    return AvailableCouponResponse(
        available=available,
        unavailable=unavailable
    )
