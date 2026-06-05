# -*- coding: utf-8 -*-
"""
用户消息管理路由
"""
import logging
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from database import get_db
from models import (
    Message, MessageRecipient, MessageType, MessageRecipientType,
    User, Order
)
from schemas import (
    MessageResponse,
    MessageListResponse,
    UnreadCountResponse,
    MessageMarkReadRequest,
    MessageBatchDeleteRequest
)
from auth import get_current_active_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/messages", tags=["消息管理"])


def _get_message_response(db: Session, recipient: MessageRecipient) -> MessageResponse:
    """构建消息响应对象"""
    message = recipient.message

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
        created_at=message.created_at,
        is_read=recipient.is_read,
        read_at=recipient.read_at,
        is_deleted=recipient.is_deleted
    )


@router.get("/unread-count", response_model=UnreadCountResponse)
def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取当前用户的未读消息数量"""
    query = db.query(MessageRecipient).filter(
        MessageRecipient.user_id == current_user.id,
        MessageRecipient.is_read == False,
        MessageRecipient.is_deleted == False
    ).join(Message).filter(Message.is_active == True)

    now = datetime.utcnow()
    query = query.filter(
        or_(
            Message.valid_from.is_(None),
            Message.valid_from <= now
        ),
        or_(
            Message.valid_to.is_(None),
            Message.valid_to >= now
        )
    )

    all_unread = query.all()

    result = UnreadCountResponse()
    for recipient in all_unread:
        result.total_unread += 1
        msg_type = recipient.message.type
        if msg_type == MessageType.ORDER_STATUS:
            result.order_status_unread += 1
        elif msg_type == MessageType.DELIVERY_REMINDER:
            result.delivery_reminder_unread += 1
        elif msg_type == MessageType.ANNOUNCEMENT:
            result.announcement_unread += 1
        elif msg_type == MessageType.ACCOUNT_SECURITY:
            result.account_security_unread += 1

    return result


@router.get("", response_model=MessageListResponse)
def get_messages(
    status: Optional[str] = Query(None, description="筛选状态: all, unread, read"),
    type: Optional[str] = Query(None, description="筛选消息类型: order_status, delivery_reminder, announcement, account_security"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取当前用户的消息列表
    - 支持按状态筛选（全部、未读、已读）
    - 支持按类型筛选
    - 支持分页
    """
    query = db.query(MessageRecipient).filter(
        MessageRecipient.user_id == current_user.id,
        MessageRecipient.is_deleted == False
    ).join(Message).filter(Message.is_active == True)

    if status == "unread":
        query = query.filter(MessageRecipient.is_read == False)
    elif status == "read":
        query = query.filter(MessageRecipient.is_read == True)

    if type:
        query = query.filter(Message.type == type)

    now = datetime.utcnow()
    query = query.filter(
        or_(
            Message.valid_from.is_(None),
            Message.valid_from <= now
        ),
        or_(
            Message.valid_to.is_(None),
            Message.valid_to >= now
        )
    )

    query = query.order_by(Message.created_at.desc())

    total = query.count()
    recipients = query.offset((page - 1) * page_size).limit(page_size).all()

    items = [_get_message_response(db, r) for r in recipients]

    return MessageListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=items
    )


@router.get("/{message_id}", response_model=MessageResponse)
def get_message_detail(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取消息详情（自动标记为已读）"""
    recipient = db.query(MessageRecipient).filter(
        MessageRecipient.message_id == message_id,
        MessageRecipient.user_id == current_user.id,
        MessageRecipient.is_deleted == False
    ).first()

    if not recipient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="消息不存在"
        )

    if not recipient.is_read:
        recipient.is_read = True
        recipient.read_at = datetime.utcnow()
        db.commit()

    return _get_message_response(db, recipient)


@router.post("/{message_id}/read")
def mark_message_read(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """标记单条消息为已读"""
    recipient = db.query(MessageRecipient).filter(
        MessageRecipient.message_id == message_id,
        MessageRecipient.user_id == current_user.id,
        MessageRecipient.is_deleted == False
    ).first()

    if not recipient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="消息不存在"
        )

    if not recipient.is_read:
        recipient.is_read = True
        recipient.read_at = datetime.utcnow()
        db.commit()

    return {"message": "标记已读成功"}


@router.post("/read-all")
def mark_all_messages_read(
    type: Optional[str] = Query(None, description="按类型标记已读，不填则标记全部"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """标记全部消息为已读"""
    query = db.query(MessageRecipient).filter(
        MessageRecipient.user_id == current_user.id,
        MessageRecipient.is_read == False,
        MessageRecipient.is_deleted == False
    ).join(Message).filter(Message.is_active == True)

    if type:
        query = query.filter(Message.type == type)

    recipients = query.all()
    now = datetime.utcnow()
    for recipient in recipients:
        recipient.is_read = True
        recipient.read_at = now

    db.commit()

    return {"message": f"已标记 {len(recipients)} 条消息为已读"}


@router.delete("/{message_id}")
def delete_message(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除单条消息（软删除）"""
    recipient = db.query(MessageRecipient).filter(
        MessageRecipient.message_id == message_id,
        MessageRecipient.user_id == current_user.id,
        MessageRecipient.is_deleted == False
    ).first()

    if not recipient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="消息不存在"
        )

    recipient.is_deleted = True
    db.commit()

    return {"message": "删除成功"}


@router.post("/batch-delete")
def batch_delete_messages(
    request: MessageBatchDeleteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """批量删除消息（软删除）"""
    recipients = db.query(MessageRecipient).filter(
        MessageRecipient.message_id.in_(request.message_ids),
        MessageRecipient.user_id == current_user.id,
        MessageRecipient.is_deleted == False
    ).all()

    for recipient in recipients:
        recipient.is_deleted = True

    db.commit()

    return {"message": f"已删除 {len(recipients)} 条消息"}
