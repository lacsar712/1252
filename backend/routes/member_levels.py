# -*- coding: utf-8 -*-
"""
会员等级管理路由
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from database import get_db
from models import MemberLevel, User, Order, OrderStatus
from schemas import (
    MemberLevelResponse,
    MemberLevelListResponse,
    MemberLevelCreate,
    MemberLevelUpdate,
    UserMemberLevelInfo,
    UserMemberLevelUpdate,
    UserMemberResponse,
    UserMemberListResponse,
    MemberLevelResponse as MLResponse
)
from auth import get_current_active_user, get_current_admin_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/member-levels", tags=["会员等级管理"])


def _get_user_member_level(db: Session, user: User) -> Optional[MemberLevel]:
    """获取用户的会员等级

    优先使用管理员手动设置的等级，否则根据累计消费自动计算
    """
    if user.manual_level_id:
        manual_level = db.query(MemberLevel).filter(
            MemberLevel.id == user.manual_level_id,
            MemberLevel.is_active == True
        ).first()
        if manual_level:
            return manual_level

    active_levels = db.query(MemberLevel).filter(
        MemberLevel.is_active == True
    ).order_by(MemberLevel.threshold_amount.desc()).all()

    for level in active_levels:
        if user.total_spent >= level.threshold_amount:
            return level

    return None


def _get_next_level(db: Session, current_level: Optional[MemberLevel]) -> Optional[MemberLevel]:
    """获取下一个等级"""
    current_threshold = current_level.threshold_amount if current_level else -1
    next_level = db.query(MemberLevel).filter(
        MemberLevel.is_active == True,
        MemberLevel.threshold_amount > current_threshold
    ).order_by(MemberLevel.threshold_amount.asc()).first()
    return next_level


def _build_user_member_info(db: Session, user: User) -> UserMemberLevelInfo:
    """构建用户会员等级信息"""
    current_level = _get_user_member_level(db, user)
    next_level = _get_next_level(db, current_level)

    manual_level = None
    is_manual = False
    if user.manual_level_id:
        manual_level = db.query(MemberLevel).filter(
            MemberLevel.id == user.manual_level_id
        ).first()
        is_manual = True if manual_level and current_level and manual_level.id == current_level.id else False

    amount_to_next = 0.0
    if next_level and current_level:
        amount_to_next = next_level.threshold_amount - user.total_spent
    elif next_level and not current_level:
        amount_to_next = next_level.threshold_amount

    if amount_to_next < 0:
        amount_to_next = 0.0

    current_resp = MemberLevelResponse.model_validate(current_level) if current_level else None
    next_resp = MemberLevelResponse.model_validate(next_level) if next_level else None
    manual_resp = MemberLevelResponse.model_validate(manual_level) if manual_level else None

    return UserMemberLevelInfo(
        user_id=user.id,
        total_spent=user.total_spent,
        current_level=current_resp,
        next_level=next_resp,
        amount_to_next=amount_to_next,
        manual_level=manual_resp,
        is_manual=is_manual
    )


def _recalculate_user_total_spent(db: Session, user_id: int) -> float:
    """重新计算用户累计有效订单金额"""
    valid_orders = db.query(Order).filter(
        Order.user_id == user_id,
        Order.status.in_([OrderStatus.CONFIRMED, OrderStatus.SHIPPED, OrderStatus.DELIVERED])
    ).all()

    total = sum(order.total_amount for order in valid_orders)
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.total_spent = round(total, 2)
        db.commit()
    return round(total, 2)


# ========== 管理员API ==========
@router.get("/admin/users", response_model=UserMemberListResponse)
def get_admin_users_list(
    search: Optional[str] = Query(None, description="搜索用户名或邮箱"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """获取用户列表（含会员信息，管理员）"""
    query = db.query(User)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                User.username.ilike(search_term),
                User.email.ilike(search_term)
            )
        )

    total = query.count()
    users = query.order_by(User.id.desc()) \
        .offset((page - 1) * page_size).limit(page_size).all()

    items = []
    for user in users:
        user_resp = UserMemberResponse.model_validate(user)
        user_resp.member_level = _build_user_member_info(db, user)
        items.append(user_resp)

    return UserMemberListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=items
    )


@router.get("/admin", response_model=MemberLevelListResponse)
def get_all_member_levels_admin(
    is_active: Optional[bool] = Query(None, description="启用状态筛选"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """获取所有会员等级列表（管理员）"""
    query = db.query(MemberLevel)

    if is_active is not None:
        query = query.filter(MemberLevel.is_active == is_active)

    total = query.count()
    levels = query.order_by(MemberLevel.sort_order.asc(), MemberLevel.threshold_amount.asc()) \
        .offset((page - 1) * page_size).limit(page_size).all()

    return MemberLevelListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[MemberLevelResponse.model_validate(l) for l in levels]
    )


@router.get("/admin/all", response_model=List[MemberLevelResponse])
def get_all_active_levels_admin(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """获取所有启用的会员等级（用于下拉选择）"""
    levels = db.query(MemberLevel).filter(
        MemberLevel.is_active == True
    ).order_by(MemberLevel.sort_order.asc(), MemberLevel.threshold_amount.asc()).all()
    return [MemberLevelResponse.model_validate(l) for l in levels]


@router.get("/admin/{level_id}", response_model=MemberLevelResponse)
def get_member_level_detail_admin(
    level_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """获取会员等级详情（管理员）"""
    level = db.query(MemberLevel).filter(MemberLevel.id == level_id).first()

    if not level:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会员等级不存在"
        )

    return MemberLevelResponse.model_validate(level)


@router.post("", response_model=MemberLevelResponse, status_code=status.HTTP_201_CREATED)
def create_member_level(
    level_create: MemberLevelCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """创建会员等级（管理员）"""
    existing = db.query(MemberLevel).filter(MemberLevel.name == level_create.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"会员等级名称「{level_create.name}」已存在"
        )

    if level_create.discount_rate > 1 or level_create.discount_rate <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="折扣比例必须大于0且小于等于1"
        )

    db_level = MemberLevel(
        name=level_create.name,
        threshold_amount=level_create.threshold_amount,
        discount_rate=level_create.discount_rate,
        benefits=level_create.benefits,
        badge_color=level_create.badge_color,
        icon=level_create.icon,
        sort_order=level_create.sort_order,
        is_active=level_create.is_active
    )

    db.add(db_level)
    db.commit()
    db.refresh(db_level)

    logger.info(f"管理员创建会员等级: {current_user.username}, 等级: {db_level.name}")
    return MemberLevelResponse.model_validate(db_level)


@router.put("/{level_id}", response_model=MemberLevelResponse)
def update_member_level(
    level_id: int,
    level_update: MemberLevelUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """更新会员等级（管理员）"""
    level = db.query(MemberLevel).filter(MemberLevel.id == level_id).first()

    if not level:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会员等级不存在"
        )

    if level_update.name is not None and level_update.name != level.name:
        existing = db.query(MemberLevel).filter(
            MemberLevel.name == level_update.name,
            MemberLevel.id != level_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"会员等级名称「{level_update.name}」已存在"
            )

    discount_rate = level_update.discount_rate if level_update.discount_rate is not None else level.discount_rate
    if discount_rate > 1 or discount_rate <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="折扣比例必须大于0且小于等于1"
        )

    update_data = level_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(level, field, value)

    db.commit()
    db.refresh(level)

    logger.info(f"管理员更新会员等级: {current_user.username}, 等级ID: {level_id}")
    return MemberLevelResponse.model_validate(level)


@router.delete("/{level_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_member_level(
    level_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """删除会员等级（管理员）"""
    level = db.query(MemberLevel).filter(MemberLevel.id == level_id).first()

    if not level:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会员等级不存在"
        )

    users_with_level = db.query(User).filter(User.manual_level_id == level_id).count()
    if users_with_level > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"该等级下还有 {users_with_level} 个用户，无法删除"
        )

    db.delete(level)
    db.commit()

    logger.info(f"管理员删除会员等级: {current_user.username}, 等级ID: {level_id}")


@router.patch("/users/{user_id}/level", response_model=UserMemberLevelInfo)
def update_user_member_level(
    user_id: int,
    update_data: UserMemberLevelUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """手动调整用户会员等级（管理员）"""
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    if update_data.manual_level_id is not None:
        level = db.query(MemberLevel).filter(
            MemberLevel.id == update_data.manual_level_id,
            MemberLevel.is_active == True
        ).first()
        if not level:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="指定的会员等级不存在或已禁用"
            )
        user.manual_level_id = update_data.manual_level_id
        logger.info(f"管理员设置用户等级: {current_user.username}, 用户 {user.username}, 等级 {level.name}")
    else:
        old_manual = user.manual_level_id
        user.manual_level_id = None
        if old_manual:
            logger.info(f"管理员清除用户手动等级: {current_user.username}, 用户 {user.username}")

    db.commit()
    db.refresh(user)

    return _build_user_member_info(db, user)


@router.post("/users/{user_id}/recalculate", response_model=UserMemberLevelInfo)
def recalculate_user_spent(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """重新计算用户累计消费金额（管理员）"""
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    _recalculate_user_total_spent(db, user_id)
    db.refresh(user)

    logger.info(f"管理员重新计算用户累计消费: {current_user.username}, 用户 {user.username}")
    return _build_user_member_info(db, user)


# ========== 用户端API ==========
@router.get("/active", response_model=List[MemberLevelResponse])
def get_active_member_levels(
    db: Session = Depends(get_db)
):
    """获取所有启用的会员等级列表（公开）"""
    levels = db.query(MemberLevel).filter(
        MemberLevel.is_active == True
    ).order_by(MemberLevel.sort_order.asc(), MemberLevel.threshold_amount.asc()).all()
    return [MemberLevelResponse.model_validate(l) for l in levels]


@router.get("/my", response_model=UserMemberLevelInfo)
def get_my_member_level(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取我的会员等级信息"""
    return _build_user_member_info(db, current_user)


@router.get("/my/price/{book_id}")
def get_book_member_price(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取指定图书的会员价"""
    from models import Book

    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="图书不存在"
        )

    level = _get_user_member_level(db, current_user)
    discount_rate = level.discount_rate if level else 1.0
    member_price = round(book.price * discount_rate, 2)

    return {
        "book_id": book.id,
        "price_info": {
            "original_price": book.price,
            "member_price": member_price,
            "discount_rate": discount_rate,
            "level_name": level.name if level else None
        }
    }
