# -*- coding: utf-8 -*-
"""
仪表盘管理路由
"""
import logging
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, and_
from sqlalchemy.orm import Session

from database import get_db
from models import (
    Book, User, Order, OrderItem, OrderStatus
)
from schemas import (
    DashboardResponse, DashboardStats, RecentBook, RecentOrder,
    CategoryStock, SalesTrendItem
)
from auth import get_current_admin_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/admin/dashboard", tags=["仪表盘"])

LOW_STOCK_THRESHOLD = 10


def _get_date_range(days: int) -> datetime:
    """获取指定天数前的日期"""
    return datetime.utcnow() - timedelta(days=days)


def _format_date(dt: datetime) -> str:
    """格式化日期为字符串"""
    return dt.strftime("%Y-%m-%d")


@router.get("/stats", response_model=DashboardResponse, summary="获取仪表盘统计数据")
def get_dashboard_stats(
    days: int = Query(7, ge=1, le=365, description="统计天数"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """
    获取仪表盘统计数据
    - **days**: 统计时间范围天数，支持7、30、90天
    """
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    date_from = _get_date_range(days)

    total_books = db.query(func.count(Book.id)).scalar() or 0
    total_users = db.query(func.count(User.id)).scalar() or 0
    total_orders = db.query(func.count(Order.id)).scalar() or 0

    low_stock_count = db.query(func.count(Book.id)).filter(
        Book.stock < LOW_STOCK_THRESHOLD
    ).scalar() or 0

    total_inventory_value = db.query(
        func.sum(Book.price * Book.stock)
    ).scalar() or 0.0

    pending_orders = db.query(func.count(Order.id)).filter(
        Order.status.in_([OrderStatus.PENDING, OrderStatus.CONFIRMED])
    ).scalar() or 0

    today_orders = db.query(func.count(Order.id)).filter(
        Order.created_at >= today_start
    ).scalar() or 0

    today_revenue = db.query(
        func.sum(Order.total_amount)
    ).filter(
        and_(
            Order.created_at >= today_start,
            Order.status != OrderStatus.CANCELLED
        )
    ).scalar() or 0.0

    stats = DashboardStats(
        total_books=total_books,
        total_users=total_users,
        total_orders=total_orders,
        low_stock_count=low_stock_count,
        total_inventory_value=float(total_inventory_value),
        pending_orders=pending_orders,
        today_orders=today_orders,
        today_revenue=float(today_revenue)
    )

    recent_books_query = db.query(Book).order_by(
        Book.created_at.desc()
    ).limit(10).all()

    recent_books: List[RecentBook] = [
        RecentBook(
            id=book.id,
            title=book.title,
            cover_image=book.cover_image,
            price=book.price,
            stock=book.stock,
            category=book.category,
            created_at=book.created_at
        )
        for book in recent_books_query
    ]

    recent_orders_query = db.query(Order).order_by(
        Order.created_at.desc()
    ).limit(10).all()

    recent_orders: List[RecentOrder] = [
        RecentOrder(
            id=order.id,
            order_no=order.order_no,
            receiver_name=order.receiver_name,
            total_amount=order.total_amount,
            status=order.status,
            created_at=order.created_at
        )
        for order in recent_orders_query
    ]

    category_stock_query = db.query(
        func.coalesce(Book.category, '未分类').label('category'),
        func.count(Book.id).label('count'),
        func.sum(Book.price * Book.stock).label('value')
    ).group_by(Book.category).all()

    total_value = sum(float(row.value or 0) for row in category_stock_query)

    category_stock: List[CategoryStock] = []
    for row in category_stock_query:
        value = float(row.value or 0)
        percentage = (value / total_value * 100) if total_value > 0 else 0
        category_stock.append(CategoryStock(
            category=row.category,
            count=row.count,
            value=value,
            percentage=round(percentage, 2)
        ))

    category_stock.sort(key=lambda x: x.value, reverse=True)

    sales_trend: List[SalesTrendItem] = []
    for i in range(days):
        day_start = date_from + timedelta(days=i)
        day_end = day_start + timedelta(days=1)

        day_orders = db.query(Order).filter(
            and_(
                Order.created_at >= day_start,
                Order.created_at < day_end,
                Order.status != OrderStatus.CANCELLED
            )
        ).all()

        order_count = len(day_orders)
        revenue = sum(float(order.total_amount) for order in day_orders)

        book_count = 0
        if day_orders:
            order_ids = [order.id for order in day_orders]
            book_count = db.query(
                func.sum(OrderItem.quantity)
            ).filter(
                OrderItem.order_id.in_(order_ids)
            ).scalar() or 0

        sales_trend.append(SalesTrendItem(
            date=_format_date(day_start),
            order_count=order_count,
            revenue=round(revenue, 2),
            book_count=book_count
        ))

    return DashboardResponse(
        stats=stats,
        recent_books=recent_books,
        recent_orders=recent_orders,
        category_stock=category_stock,
        sales_trend=sales_trend
    )
