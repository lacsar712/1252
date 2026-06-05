# -*- coding: utf-8 -*-
"""
Pydantic 数据模式定义
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


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

    class Config:
        from_attributes = True


class OrderListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[OrderResponse]
