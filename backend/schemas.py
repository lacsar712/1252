# -*- coding: utf-8 -*-
"""
Pydantic 数据模式定义
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

from models import CouponStatus, UserCouponStatus


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
    isbn: Optional[str] = Field(None, max_length=20)
    price: float = Field(..., gt=0)
    stock: int = Field(default=0, ge=0)
    description: Optional[str] = None
    cover_image: Optional[str] = None
    category: Optional[str] = None


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    author: Optional[str] = Field(None, min_length=1, max_length=100)
    publisher: Optional[str] = Field(None, max_length=100)
    isbn: Optional[str] = Field(None, max_length=20)
    price: Optional[float] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
    description: Optional[str] = None
    cover_image: Optional[str] = None
    category: Optional[str] = None


class BookResponse(BookBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BookListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[BookResponse]


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
    used_coupon: Optional[UserCouponResponse] = None

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
