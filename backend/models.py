# -*- coding: utf-8 -*-
"""
数据库模型定义
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


book_author = Table(
    'book_author',
    Base.metadata,
    Column('book_id', Integer, ForeignKey('books.id'), primary_key=True),
    Column('author_id', Integer, ForeignKey('authors.id'), primary_key=True)
)


class Publisher(Base):
    """出版社模型"""
    __tablename__ = "publishers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False, index=True, unique=True)
    logo = Column(String(500), nullable=True)
    website = Column(String(500), nullable=True)
    location = Column(String(200), nullable=True)
    description = Column(Text, nullable=True)
    founded_year = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    books = relationship("Book", back_populates="publisher")


class Author(Base):
    """作者模型"""
    __tablename__ = "authors"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False, index=True)
    avatar = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    country = Column(String(100), nullable=True)
    birth_year = Column(Integer, nullable=True)
    masterpieces = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    books = relationship("Book", secondary=book_author, back_populates="authors")


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
    publisher_id = Column(Integer, ForeignKey("publishers.id"), nullable=True, index=True)
    isbn = Column(String(20), unique=True, nullable=True)
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    description = Column(Text, nullable=True)
    cover_image = Column(String(500), nullable=True)
    category = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    authors = relationship("Author", secondary=book_author, back_populates="books")
    publisher_rel = relationship("Publisher", back_populates="books")
    book_lists = relationship("BookList", secondary=book_list_book, back_populates="books")


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


class MessageType:
    """消息类型枚举"""
    ORDER_STATUS = "order_status"
    DELIVERY_REMINDER = "delivery_reminder"
    ANNOUNCEMENT = "announcement"
    ACCOUNT_SECURITY = "account_security"


class MessageRecipientType:
    """消息接收者类型枚举"""
    ALL_USERS = "all_users"
    SPECIFIC_USERS = "specific_users"


class Message(Base):
    """消息主体模型"""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    type = Column(String(50), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    recipient_type = Column(String(20), default=MessageRecipientType.SPECIFIC_USERS, nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    valid_from = Column(DateTime, nullable=True)
    valid_to = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    sender = relationship("User", foreign_keys=[sender_id])
    order = relationship("Order")
    recipients = relationship("MessageRecipient", back_populates="message", cascade="all, delete-orphan")


class MessageRecipient(Base):
    """消息接收者模型（维护阅读状态和删除状态）"""
    __tablename__ = "message_recipients"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    is_read = Column(Boolean, default=False, nullable=False, index=True)
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)
    read_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    message = relationship("Message", back_populates="recipients")
    user = relationship("User")


book_list_book = Table(
    'book_list_book',
    Base.metadata,
    Column('book_list_id', Integer, ForeignKey('book_lists.id'), primary_key=True),
    Column('book_id', Integer, ForeignKey('books.id'), primary_key=True),
    Column('sort_order', Integer, default=0, nullable=False),
    Column('recommendation', Text, nullable=True),
    Column('created_at', DateTime, default=datetime.utcnow)
)


class BookList(Base):
    """主题书单模型"""
    __tablename__ = "book_lists"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    cover_image = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    sort_weight = Column(Integer, default=0, nullable=False, index=True)
    category = Column(String(100), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    books = relationship("Book", secondary=book_list_book, back_populates="book_lists", order_by="book_list_book.c.sort_order")


class BookListBookAssociation(Base):
    """书单图书关联模型（用于操作排序和推荐语）"""
    __table__ = book_list_book

    book_list = relationship("BookList", backref="book_associations")
    book = relationship("Book", backref="list_associations")
