# -*- coding: utf-8 -*-
"""
Pydantic 数据模式定义
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

from models import CouponStatus, UserCouponStatus, MessageType, MessageRecipientType


# ========== 作者相关 Schema ==========
class AuthorBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="作者姓名")
    avatar: Optional[str] = Field(None, max_length=500, description="头像URL")
    bio: Optional[str] = Field(None, description="作者简介")
    country: Optional[str] = Field(None, max_length=100, description="国家或地区")
    birth_year: Optional[int] = Field(None, ge=0, le=3000, description="出生年份")
    masterpieces: Optional[str] = Field(None, description="代表作说明")
    is_active: bool = Field(True, description="展示状态")


class AuthorCreate(AuthorBase):
    pass


class AuthorUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="作者姓名")
    avatar: Optional[str] = Field(None, max_length=500, description="头像URL")
    bio: Optional[str] = Field(None, description="作者简介")
    country: Optional[str] = Field(None, max_length=100, description="国家或地区")
    birth_year: Optional[int] = Field(None, ge=0, le=3000, description="出生年份")
    masterpieces: Optional[str] = Field(None, description="代表作说明")
    is_active: Optional[bool] = Field(None, description="展示状态")


class AuthorResponse(AuthorBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AuthorDetailResponse(AuthorResponse):
    book_count: int = Field(0, description="作品数量")
    category_distribution: List[dict] = Field([], description="分类分布")
    books: List["BookResponse"] = Field([], description="关联图书")


class AuthorListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[AuthorResponse]


class AuthorBookCheckResponse(BaseModel):
    can_delete: bool = Field(..., description="是否可以删除")
    linked_books: int = Field(0, description="关联图书数量")
    message: Optional[str] = Field(None, description="提示信息")


# ========== 用户相关 Schema ==========
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100)


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[int] = None


# ========== 图书相关 Schema ==========
class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    author: str = Field(..., min_length=1, max_length=100)
    publisher: Optional[str] = Field(None, max_length=100)
    publisher_id: Optional[int] = Field(None, description="关联出版社ID")
    isbn: Optional[str] = Field(None, max_length=20)
    price: float = Field(..., gt=0)
    stock: int = Field(default=0, ge=0)
    description: Optional[str] = None
    cover_image: Optional[str] = None
    category: Optional[str] = None


class BookCreate(BookBase):
    author_ids: Optional[List[int]] = Field(None, description="关联作者ID列表")


class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    author: Optional[str] = Field(None, min_length=1, max_length=100)
    publisher: Optional[str] = Field(None, max_length=100)
    publisher_id: Optional[int] = Field(None, description="关联出版社ID")
    isbn: Optional[str] = Field(None, max_length=20)
    price: Optional[float] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
    description: Optional[str] = None
    cover_image: Optional[str] = None
    category: Optional[str] = None
    author_ids: Optional[List[int]] = Field(None, description="关联作者ID列表")


class BookResponse(BookBase):
    id: int
    created_at: datetime
    updated_at: datetime
    authors: List[AuthorResponse] = Field([], description="关联作者列表")
    publisher_info: Optional[PublisherResponse] = Field(None, description="关联出版社信息")

    class Config:
        from_attributes = True


class BookListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[BookResponse]


AuthorDetailResponse.model_rebuild()


# ========== 出版社相关 Schema ==========
class PublisherBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="出版社名称")
    logo: Optional[str] = Field(None, max_length=500, description="Logo URL")
    website: Optional[str] = Field(None, max_length=500, description="官网地址")
    location: Optional[str] = Field(None, max_length=200, description="所在地")
    description: Optional[str] = Field(None, description="出版社简介")
    founded_year: Optional[int] = Field(None, ge=0, le=3000, description="成立年份")
    is_active: bool = Field(True, description="启用状态")


class PublisherCreate(PublisherBase):
    pass


class PublisherUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="出版社名称")
    logo: Optional[str] = Field(None, max_length=500, description="Logo URL")
    website: Optional[str] = Field(None, max_length=500, description="官网地址")
    location: Optional[str] = Field(None, max_length=200, description="所在地")
    description: Optional[str] = Field(None, description="出版社简介")
    founded_year: Optional[int] = Field(None, ge=0, le=3000, description="成立年份")
    is_active: Optional[bool] = Field(None, description="启用状态")


class PublisherResponse(PublisherBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PublisherDetailResponse(PublisherResponse):
    book_count: int = Field(0, description="图书数量")
    category_distribution: List[dict] = Field([], description="分类分布")
    recent_books: List["BookResponse"] = Field([], description="最近上架书籍")
    books: List["BookResponse"] = Field([], description="旗下图书")


class PublisherListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[PublisherResponse]


class PublisherSearchResult(BaseModel):
    id: int
    name: str
    location: Optional[str] = None
    logo: Optional[str] = None
    is_active: bool


class PublisherNameCheckResponse(BaseModel):
    available: bool = Field(..., description="名称是否可用")
    message: Optional[str] = Field(None, description="提示信息")


class PublisherBookCheckResponse(BaseModel):
    can_delete: bool = Field(..., description="是否可以删除")
    linked_books: int = Field(0, description="关联图书数量")
    message: Optional[str] = Field(None, description="提示信息")


PublisherDetailResponse.model_rebuild()


# ========== 购物车相关 Schema ==========
class CartItemAdd(BaseModel):
    book_id: int = Field(..., gt=0, description="图书ID")
    quantity: int = Field(1, gt=0, description="数量")


class CartItemUpdate(BaseModel):
    quantity: int = Field(..., gt=0, description="数量")


class CartItemSelectedUpdate(BaseModel):
    selected: bool = Field(..., description="选中状态")


class CartItemBatchDelete(BaseModel):
    cart_item_ids: List[int] = Field(..., description="购物车项ID列表")


class CartItemInfo(BaseModel):
    id: int
    user_id: int
    book_id: int
    quantity: int
    selected: bool
    created_at: datetime
    updated_at: datetime
    book: BookResponse

    class Config:
        from_attributes = True


class CartListResponse(BaseModel):
    items: List[CartItemInfo]
    total_count: int
    selected_count: int
    total_price: float
    selected_price: float
    invalid_items: List[CartItemInfo]
    low_stock_items: List[CartItemInfo]


# ========== 订单相关 Schema ==========
class OrderItemSnapshot(BaseModel):
    book_id: int
    book_title: str
    book_author: str
    book_price: float
    book_cover: Optional[str] = None
    quantity: int
    subtotal: float


class OrderCreate(BaseModel):
    receiver_name: str = Field(..., min_length=1, max_length=50, description="收货人")
    receiver_phone: str = Field(..., min_length=1, max_length=20, description="联系电话")
    receiver_address: str = Field(..., min_length=1, max_length=500, description="收货地址")
    remark: Optional[str] = Field(None, description="备注")
    cart_item_ids: Optional[List[int]] = Field(None, description="购物车项ID列表")


class OrderCancel(BaseModel):
    cancel_reason: str = Field(..., min_length=1, description="取消原因")


class OrderShip(BaseModel):
    tracking_company: str = Field(..., min_length=1, max_length=100, description="物流公司")
    tracking_number: str = Field(..., min_length=1, max_length=100, description="物流单号")
    admin_remark: Optional[str] = Field(None, description="管理员备注")


class OrderAdminUpdate(BaseModel):
    status: Optional[str] = Field(None, description="订单状态")
    admin_remark: Optional[str] = Field(None, description="管理员备注")
    tracking_company: Optional[str] = Field(None, max_length=100, description="物流公司")
    tracking_number: Optional[str] = Field(None, max_length=100, description="物流单号")


class OrderStatusUpdate(BaseModel):
    status: str = Field(..., description="订单状态")


class OrderResponse(BaseModel):
    id: int
    order_no: str
    user_id: int
    total_amount: float
    original_amount: float
    discount_amount: float
    user_coupon_id: Optional[int] = None
    status: str
    receiver_name: str
    receiver_phone: str
    receiver_address: str
    remark: Optional[str] = None
    cancel_reason: Optional[str] = None
    admin_remark: Optional[str] = None
    tracking_company: Optional[str] = None
    tracking_number: Optional[str] = None
    paid_at: Optional[datetime] = None
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    items: List[OrderItemSnapshot]
    used_coupon: Optional["UserCouponResponse"] = None

    class Config:
        from_attributes = True


class OrderListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[OrderResponse]


# ========== 优惠券相关 Schema ==========
class CouponBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="优惠券名称")
    description: Optional[str] = Field(None, max_length=500, description="优惠券说明")
    threshold_amount: float = Field(..., ge=0, description="门槛金额")
    discount_amount: float = Field(..., gt=0, description="优惠金额")
    valid_from: datetime = Field(..., description="有效期开始")
    valid_to: datetime = Field(..., description="有效期结束")
    total_quantity: int = Field(..., ge=0, description="发放数量")
    limit_per_user: int = Field(..., ge=1, description="每人限领次数")
    applicable_categories: Optional[str] = Field(None, max_length=500, description="适用分类，多个用逗号分隔")
    status: str = Field(CouponStatus.ACTIVE, description="启用状态")


class CouponCreate(CouponBase):
    pass


class CouponUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="优惠券名称")
    description: Optional[str] = Field(None, max_length=500, description="优惠券说明")
    threshold_amount: Optional[float] = Field(None, ge=0, description="门槛金额")
    discount_amount: Optional[float] = Field(None, gt=0, description="优惠金额")
    valid_from: Optional[datetime] = Field(None, description="有效期开始")
    valid_to: Optional[datetime] = Field(None, description="有效期结束")
    total_quantity: Optional[int] = Field(None, ge=0, description="发放数量")
    limit_per_user: Optional[int] = Field(None, ge=1, description="每人限领次数")
    applicable_categories: Optional[str] = Field(None, max_length=500, description="适用分类")
    status: Optional[str] = Field(None, description="启用状态")


class CouponResponse(CouponBase):
    id: int
    claimed_quantity: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CouponListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[CouponResponse]


class UserCouponResponse(BaseModel):
    id: int
    coupon_id: int
    user_id: int
    status: str
    order_id: Optional[int]
    used_at: Optional[datetime]
    claimed_at: datetime
    coupon: CouponResponse
    unavailable_reason: Optional[str] = None
    is_available: bool = True

    class Config:
        from_attributes = True


class UserCouponListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[UserCouponResponse]


class CouponClaimResponse(BaseModel):
    message: str
    user_coupon: UserCouponResponse


class OrderCouponValidateRequest(BaseModel):
    cart_item_ids: List[int] = Field(..., description="购物车项ID列表")


class AvailableCouponResponse(BaseModel):
    available: List[UserCouponResponse]
    unavailable: List[UserCouponResponse]


class OrderCreateWithCoupon(OrderCreate):
    user_coupon_id: Optional[int] = Field(None, description="用户优惠券ID")


OrderResponse.model_rebuild()


# ========== 消息相关 Schema ==========
class MessageBase(BaseModel):
    type: str = Field(..., description="消息类型")
    title: str = Field(..., min_length=1, max_length=200, description="消息标题")
    content: str = Field(..., min_length=1, description="消息正文")


class MessageCreate(MessageBase):
    recipient_type: str = Field(MessageRecipientType.SPECIFIC_USERS, description="接收者类型")
    user_ids: Optional[List[int]] = Field(None, description="指定用户ID列表")
    order_id: Optional[int] = Field(None, description="关联订单ID")
    valid_from: Optional[datetime] = Field(None, description="有效期开始")
    valid_to: Optional[datetime] = Field(None, description="有效期结束")


class AnnouncementCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="公告标题")
    content: str = Field(..., min_length=1, description="公告正文")
    recipient_type: str = Field(MessageRecipientType.ALL_USERS, description="接收者类型")
    user_ids: Optional[List[int]] = Field(None, description="指定用户ID列表（当recipient_type为specific_users时需要）")
    valid_from: Optional[datetime] = Field(None, description="有效期开始")
    valid_to: Optional[datetime] = Field(None, description="有效期结束")


class MessageResponse(BaseModel):
    id: int
    type: str
    title: str
    content: str
    sender_id: Optional[int]
    sender_name: Optional[str] = None
    recipient_type: str
    order_id: Optional[int]
    order_no: Optional[str] = None
    valid_from: Optional[datetime]
    valid_to: Optional[datetime]
    is_active: bool
    created_at: datetime
    is_read: bool = False
    read_at: Optional[datetime] = None
    is_deleted: bool = False

    class Config:
        from_attributes = True


class MessageListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[MessageResponse]


class UnreadCountResponse(BaseModel):
    total_unread: int = Field(0, description="总未读数量")
    order_status_unread: int = Field(0, description="订单状态未读数量")
    delivery_reminder_unread: int = Field(0, description="到货提醒未读数量")
    announcement_unread: int = Field(0, description="公告未读数量")
    account_security_unread: int = Field(0, description="账号安全未读数量")


class MessageMarkReadRequest(BaseModel):
    message_id: int = Field(..., description="消息ID")


class MessageBatchDeleteRequest(BaseModel):
    message_ids: List[int] = Field(..., description="消息ID列表")
