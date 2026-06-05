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
from routes.publishers import router as publishers_router
from routes.messages import router as messages_router
from routes.admin_messages import router as admin_messages_router
from routes.dashboard import router as dashboard_router
from routes.book_lists import router as book_lists_router
from routes.member_levels import router as member_levels_router

__all__ = ["auth_router", "books_router", "cart_router", "orders_router", "coupons_router", "authors_router", "publishers_router", "messages_router", "admin_messages_router", "dashboard_router", "book_lists_router", "member_levels_router"]
