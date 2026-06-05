# -*- coding: utf-8 -*-
"""
管理员消息管理路由
"""
import logging
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from database import get_db
from models import (
    Message, MessageRecipient, MessageType, MessageRecipientType,
    User, Order
)
from schemas import (
    MessageResponse,
    MessageListResponse,
    AnnouncementCreate,
    User as UserSchema
)
from auth import get_current_admin_user
from message_service import send_announcement

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/admin/messages", tags=["管理员消息管理"])


def _get_admin_message_response(db: Session, message: Message) -> MessageResponse:
    """构建管理员消息响应对象"""
    sender_name = None
    if message.sender_id:
        sender = db.query(User).filter(User.id == message.sender_id).first()
        if sender:
            sender_name = sender.username

    order_no = None
    if message.order_id:
        order = db.query(Order).filter(Order.id == message.order_id).first()
        if order:
            order_no = order.order_no

    recipient_count = db.query(MessageRecipient).filter(
        MessageRecipient.message_id == message.id
    ).count()

    read_count = db.query(MessageRecipient).filter(
        MessageRecipient.message_id == message.id,
        MessageRecipient.is_read == True
    ).count()

    return MessageResponse(
        id=message.id,
        type=message.type,
        title=message.title,
        content=message.content,
        sender_id=message.sender_id,
        sender_name=sender_name,
        recipient_type=message.recipient_type,
        order_id=message.order_id,
        order_no=order_no,
        valid_from=message.valid_from,
        valid_to=message.valid_to,
        is_active=message.is_active,
        created_at=message.created_at
    )


@router.get("/users", response_model=List[UserSchema])
def get_users_for_selection(
    search: Optional[str] = Query(None, description="搜索用户名或邮箱"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """获取用户列表（用于选择发送对象）"""
    query = db.query(User).filter(User.is_active == True)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                User.username.ilike(search_term),
                User.email.ilike(search_term)
            )
        )

    users = query.order_by(User.username).all()
    return [UserSchema.model_validate(user) for user in users]


@router.get("", response_model=MessageListResponse)
def get_admin_messages(
    type: Optional[str] = Query(None, description="筛选消息类型"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """管理员获取所有消息列表"""
    query = db.query(Message).filter(Message.type == MessageType.ANNOUNCEMENT)

    if type:
        query = query.filter(Message.type == type)

    query = query.order_by(Message.created_at.desc())

    total = query.count()
    messages = query.offset((page - 1) * page_size).limit(page_size).all()

    items = [_get_admin_message_response(db, m) for m in messages]

    return MessageListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=items
    )


@router.post("/announcement", response_model=MessageResponse)
def create_announcement(
    announcement: AnnouncementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    管理员发布公告
    - 可以选择发送给所有用户或指定用户
    - 可以设置有效期
    """
    if announcement.recipient_type == MessageRecipientType.SPECIFIC_USERS:
        if not announcement.user_ids or len(announcement.user_ids) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="当选择发送给指定用户时，必须提供用户ID列表"
            )

        valid_users = db.query(User).filter(
            User.id.in_(announcement.user_ids),
            User.is_active == True
        ).all()
        valid_user_ids = [u.id for u in valid_users]

        if len(valid_user_ids) != len(announcement.user_ids):
            invalid_ids = set(announcement.user_ids) - set(valid_user_ids)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"以下用户ID无效: {invalid_ids}"
            )

    try:
        message = send_announcement(
            db=db,
            title=announcement.title,
            content=announcement.content,
            recipient_type=announcement.recipient_type,
            user_ids=announcement.user_ids,
            sender_id=current_user.id,
            valid_from=announcement.valid_from,
            valid_to=announcement.valid_to
        )

        return _get_admin_message_response(db, message)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{message_id}/toggle-active")
def toggle_message_active(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """启用/禁用消息"""
    message = db.query(Message).filter(
        Message.id == message_id,
        Message.type == MessageType.ANNOUNCEMENT
    ).first()

    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="消息不存在"
        )

    message.is_active = not message.is_active
    db.commit()

    return {
        "message": f"消息已{'启用' if message.is_active else '禁用'}",
        "is_active": message.is_active
    }


@router.delete("/{message_id}")
def delete_announcement(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """删除公告（硬删除，同时删除所有接收者记录）"""
    message = db.query(Message).filter(
        Message.id == message_id,
        Message.type == MessageType.ANNOUNCEMENT
    ).first()

    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="消息不存在"
        )

    db.delete(message)
    db.commit()

    return {"message": "删除成功"}


@router.get("/stats")
def get_message_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """获取消息统计数据"""
    now = datetime.utcnow()

    total_messages = db.query(Message).filter(
        Message.type == MessageType.ANNOUNCEMENT
    ).count()

    active_messages = db.query(Message).filter(
        Message.type == MessageType.ANNOUNCEMENT,
        Message.is_active == True,
        or_(Message.valid_to.is_(None), Message.valid_to >= now)
    ).count()

    total_recipients = db.query(MessageRecipient).join(Message).filter(
        Message.type == MessageType.ANNOUNCEMENT
    ).count()

    read_recipients = db.query(MessageRecipient).join(Message).filter(
        Message.type == MessageType.ANNOUNCEMENT,
        MessageRecipient.is_read == True
    ).count()

    return {
        "total_messages": total_messages,
        "active_messages": active_messages,
        "total_recipients": total_recipients,
        "read_recipients": read_recipients,
        "read_rate": (read_recipients / total_recipients * 100) if total_recipients > 0 else 0
    }
