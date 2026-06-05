# -*- coding: utf-8 -*-
"""
消息发送服务
"""
import logging
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from models import (
    Message, MessageRecipient, MessageType, MessageRecipientType,
    User, Order, OrderStatus
)

logger = logging.getLogger(__name__)


def send_message(
    db: Session,
    message_type: str,
    title: str,
    content: str,
    user_ids: Optional[List[int]] = None,
    sender_id: Optional[int] = None,
    order_id: Optional[int] = None,
    recipient_type: str = MessageRecipientType.SPECIFIC_USERS,
    valid_from: Optional[datetime] = None,
    valid_to: Optional[datetime] = None
) -> Message:
    """
    发送消息给指定用户或所有用户
    """
    if recipient_type == MessageRecipientType.ALL_USERS:
        all_users = db.query(User).filter(User.is_active == True).all()
        user_ids = [user.id for user in all_users]
    elif not user_ids:
        raise ValueError("当recipient_type为specific_users时，必须提供user_ids")

    message = Message(
        type=message_type,
        title=title,
        content=content,
        sender_id=sender_id,
        recipient_type=recipient_type,
        order_id=order_id,
        valid_from=valid_from,
        valid_to=valid_to,
        is_active=True
    )
    db.add(message)
    db.flush()

    for user_id in user_ids:
        recipient = MessageRecipient(
            message_id=message.id,
            user_id=user_id,
            is_read=False,
            is_deleted=False
        )
        db.add(recipient)

    db.commit()
    db.refresh(message)
    logger.info(f"消息发送成功: type={message_type}, title={title}, recipient_count={len(user_ids)}")
    return message


def send_order_status_message(
    db: Session,
    order: Order,
    old_status: str,
    new_status: str,
    sender_id: Optional[int] = None
) -> Optional[Message]:
    """
    订单状态变更时发送消息
    """
    status_text = {
        OrderStatus.PENDING: "待确认",
        OrderStatus.CONFIRMED: "已确认",
        OrderStatus.SHIPPED: "已发货",
        OrderStatus.DELIVERED: "已送达",
        OrderStatus.CANCELLED: "已取消"
    }

    old_text = status_text.get(old_status, old_status)
    new_text = status_text.get(new_status, new_status)

    title = f"订单状态变更通知"
    content = f"您的订单 {order.order_no} 状态已从「{old_text}」更新为「{new_text}」。"

    if new_status == OrderStatus.SHIPPED and order.tracking_company and order.tracking_number:
        content += f" 物流公司：{order.tracking_company}，物流单号：{order.tracking_number}。"

    return send_message(
        db=db,
        message_type=MessageType.ORDER_STATUS,
        title=title,
        content=content,
        user_ids=[order.user_id],
        sender_id=sender_id,
        order_id=order.id
    )


def send_delivery_reminder(
    db: Session,
    order: Order,
    sender_id: Optional[int] = None
) -> Message:
    """
    发送到货提醒消息
    """
    title = "您的订单已送达"
    content = f"您的订单 {order.order_no} 已送达，请及时查收。如有问题请及时联系客服。"

    return send_message(
        db=db,
        message_type=MessageType.DELIVERY_REMINDER,
        title=title,
        content=content,
        user_ids=[order.user_id],
        sender_id=sender_id,
        order_id=order.id
    )


def send_account_security_message(
    db: Session,
    user_id: int,
    title: str,
    content: str,
    sender_id: Optional[int] = None
) -> Message:
    """
    发送账号安全类消息
    """
    return send_message(
        db=db,
        message_type=MessageType.ACCOUNT_SECURITY,
        title=title,
        content=content,
        user_ids=[user_id],
        sender_id=sender_id
    )


def send_announcement(
    db: Session,
    title: str,
    content: str,
    recipient_type: str = MessageRecipientType.ALL_USERS,
    user_ids: Optional[List[int]] = None,
    sender_id: Optional[int] = None,
    valid_from: Optional[datetime] = None,
    valid_to: Optional[datetime] = None
) -> Message:
    """
    发送公告类消息
    """
    return send_message(
        db=db,
        message_type=MessageType.ANNOUNCEMENT,
        title=title,
        content=content,
        user_ids=user_ids,
        sender_id=sender_id,
        recipient_type=recipient_type,
        valid_from=valid_from,
        valid_to=valid_to
    )
