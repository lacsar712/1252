# -*- coding: utf-8 -*-
"""
数据库模型定义
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class User(Base):
    """用户模型"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Book(Base):
    """图书模型"""
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(200), nullable=False, index=True)
    author = Column(String(100), nullable=False, index=True)
    publisher = Column(String(100), nullable=True)
    isbn = Column(String(20), unique=True, nullable=True)
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    description = Column(Text, nullable=True)
    cover_image = Column(String(500), nullable=True)
    category = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CartItem(Base):
    """购物车项模型"""
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    book_id = Column(Integer, nullable=False, index=True)
    quantity = Column(Integer, nullable=False, default=1)
    selected = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class OrderStatus:
    """订单状态枚举"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class Order(Base):
    """订单模型"""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_no = Column(String(50), unique=True, index=True, nullable=False)
    user_id = Column(Integer, nullable=False, index=True)
    total_amount = Column(Float, nullable=False)
    original_amount = Column(Float, nullable=False, default=0.0)
    discount_amount = Column(Float, nullable=False, default=0.0)
    user_coupon_id = Column(Integer, nullable=True, index=True)
    status = Column(String(20), default=OrderStatus.PENDING, nullable=False)
    receiver_name = Column(String(50), nullable=False)
    receiver_phone = Column(String(20), nullable=False)
    receiver_address = Column(String(500), nullable=False)
    remark = Column(Text, nullable=True)
    cancel_reason = Column(Text, nullable=True)
    admin_remark = Column(Text, nullable=True)
    tracking_company = Column(String(100), nullable=True)
    tracking_number = Column(String(100), nullable=True)
    paid_at = Column(DateTime, nullable=True)
    shipped_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    """订单项模型"""
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    book_id = Column(Integer, nullable=False)
    book_title = Column(String(200), nullable=False)
    book_author = Column(String(100), nullable=False)
    book_price = Column(Float, nullable=False)
    book_cover = Column(String(500), nullable=True)
    quantity = Column(Integer, nullable=False)
    subtotal = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    order = relationship("Order", back_populates="items")


class CouponStatus:
    """优惠券状态枚举"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"
    SOLD_OUT = "sold_out"


class UserCouponStatus:
    """用户优惠券状态枚举"""
    UNUSED = "unused"
    USED = "used"
    EXPIRED = "expired"
    LOCKED = "locked"


class Coupon(Base):
    """优惠券模板模型"""
    __tablename__ = "coupons"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(String(500), nullable=True)
    threshold_amount = Column(Float, nullable=False, default=0.0)
    discount_amount = Column(Float, nullable=False)
    valid_from = Column(DateTime, nullable=False)
    valid_to = Column(DateTime, nullable=False)
    total_quantity = Column(Integer, nullable=False, default=0)
    claimed_quantity = Column(Integer, nullable=False, default=0)
    limit_per_user = Column(Integer, nullable=False, default=1)
    applicable_categories = Column(String(500), nullable=True)
    status = Column(String(20), default=CouponStatus.ACTIVE, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user_coupons = relationship("UserCoupon", back_populates="coupon", cascade="all, delete-orphan")


class UserCoupon(Base):
    """用户优惠券模型"""
    __tablename__ = "user_coupons"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    coupon_id = Column(Integer, ForeignKey("coupons.id"), nullable=False, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    status = Column(String(20), default=UserCouponStatus.UNUSED, nullable=False)
    order_id = Column(Integer, nullable=True, index=True)
    used_at = Column(DateTime, nullable=True)
    locked_at = Column(DateTime, nullable=True)
    locked_order_id = Column(Integer, nullable=True)
    claimed_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    coupon = relationship("Coupon", back_populates="user_coupons")
