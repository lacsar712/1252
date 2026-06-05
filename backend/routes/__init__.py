# -*- coding: utf-8 -*-
"""
路由模块
"""
from routes.auth import router as auth_router
from routes.books import router as books_router
from routes.cart import router as cart_router
from routes.orders import router as orders_router
from routes.coupons import router as coupons_router
from routes.authors import router as authors_router

__all__ = ["auth_router", "books_router", "cart_router", "orders_router", "coupons_router", "authors_router"]
