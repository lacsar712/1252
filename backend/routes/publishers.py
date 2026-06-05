# -*- coding: utf-8 -*-
"""
出版社管理路由
"""
import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func, desc
from collections import Counter

from database import get_db
from models import Publisher, Book, User
from schemas import (
    PublisherCreate, PublisherUpdate, PublisherResponse, PublisherListResponse,
    PublisherDetailResponse, PublisherSearchResult, PublisherNameCheckResponse,
    PublisherBookCheckResponse, BookListResponse
)
from auth import get_current_admin_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/publishers", tags=["出版社管理"])


@router.get("", response_model=PublisherListResponse)
def get_publishers(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    search: Optional[str] = Query(None, description="搜索关键词（名称或所在地）"),
    is_active: Optional[bool] = Query(None, description="启用状态筛选"),
    db: Session = Depends(get_db)
):
    """获取出版社列表（支持分页、搜索和状态筛选）"""
    query = db.query(Publisher)
    
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Publisher.name.like(search_pattern),
                Publisher.location.like(search_pattern),
                Publisher.description.like(search_pattern)
            )
        )
    
    if is_active is not None:
        query = query.filter(Publisher.is_active == is_active)
    
    total = query.count()
    
    offset = (page - 1) * page_size
    publishers = query.order_by(Publisher.created_at.desc()).offset(offset).limit(page_size).all()
    
    return PublisherListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=publishers
    )


@router.get("/search", response_model=list)
def search_publishers(
    keyword: str = Query(..., min_length=1, description="搜索关键词"),
    limit: int = Query(20, ge=1, le=100, description="返回数量限制"),
    include_inactive: bool = Query(False, description="是否包含已禁用的出版社"),
    db: Session = Depends(get_db)
):
    """出版社搜索（用于下拉选择）"""
    search_pattern = f"%{keyword}%"
    query = db.query(Publisher).filter(
        or_(
            Publisher.name.like(search_pattern),
            Publisher.location.like(search_pattern)
        )
    )
    
    if not include_inactive:
        query = query.filter(Publisher.is_active == True)
    
    publishers = query.order_by(Publisher.name).limit(limit).all()
    
    return [
        PublisherSearchResult(
            id=p.id,
            name=p.name,
            location=p.location,
            logo=p.logo,
            is_active=p.is_active
        )
        for p in publishers
    ]


@router.get("/check-name", response_model=PublisherNameCheckResponse)
def check_publisher_name(
    name: str = Query(..., min_length=1, description="出版社名称"),
    exclude_id: Optional[int] = Query(None, description="排除的出版社ID（编辑时使用）"),
    db: Session = Depends(get_db)
):
    """校验出版社名称唯一性"""
    query = db.query(Publisher).filter(Publisher.name == name)
    
    if exclude_id is not None:
        query = query.filter(Publisher.id != exclude_id)
    
    existing = query.first()
    
    if existing:
        return PublisherNameCheckResponse(
            available=False,
            message=f"出版社名称「{name}」已存在"
        )
    else:
        return PublisherNameCheckResponse(
            available=True,
            message="名称可用"
        )


@router.get("/{publisher_id}", response_model=PublisherDetailResponse)
def get_publisher(publisher_id: int, db: Session = Depends(get_db)):
    """获取出版社详情（包含旗下图书、分类分布和最近上架书籍）"""
    publisher = db.query(Publisher).filter(Publisher.id == publisher_id).first()
    if not publisher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="出版社不存在"
        )
    
    books = publisher.books
    book_count = len(books)
    
    categories = [book.category for book in books if book.category]
    category_counter = Counter(categories)
    category_distribution = [
        {"category": cat, "count": count}
        for cat, count in category_counter.most_common()
    ]
    
    recent_books = sorted(books, key=lambda b: b.created_at, reverse=True)[:5]
    
    return PublisherDetailResponse(
        id=publisher.id,
        name=publisher.name,
        logo=publisher.logo,
        website=publisher.website,
        location=publisher.location,
        description=publisher.description,
        founded_year=publisher.founded_year,
        is_active=publisher.is_active,
        created_at=publisher.created_at,
        updated_at=publisher.updated_at,
        book_count=book_count,
        category_distribution=category_distribution,
        recent_books=recent_books,
        books=books
    )


@router.get("/{publisher_id}/books", response_model=BookListResponse)
def get_publisher_books(
    publisher_id: int,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db)
):
    """查询出版社关联的图书列表"""
    publisher = db.query(Publisher).filter(Publisher.id == publisher_id).first()
    if not publisher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="出版社不存在"
        )
    
    query = db.query(Book).filter(Book.publisher_id == publisher_id)
    
    total = query.count()
    
    offset = (page - 1) * page_size
    books = query.order_by(Book.created_at.desc()).offset(offset).limit(page_size).all()
    
    return BookListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=books
    )


@router.get("/{publisher_id}/check-delete", response_model=PublisherBookCheckResponse)
def check_publisher_delete(
    publisher_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """删除前检查出版社关联图书"""
    publisher = db.query(Publisher).filter(Publisher.id == publisher_id).first()
    if not publisher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="出版社不存在"
        )
    
    linked_count = len(publisher.books)
    
    if linked_count > 0:
        return PublisherBookCheckResponse(
            can_delete=False,
            linked_books=linked_count,
            message=f"该出版社关联了 {linked_count} 本图书，请先解除关联后再删除"
        )
    else:
        return PublisherBookCheckResponse(
            can_delete=True,
            linked_books=0,
            message="可以删除该出版社"
        )


@router.post("", response_model=PublisherResponse, status_code=status.HTTP_201_CREATED)
def create_publisher(
    publisher: PublisherCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """创建出版社（需要管理员权限）"""
    existing = db.query(Publisher).filter(Publisher.name == publisher.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"出版社名称「{publisher.name}」已存在"
        )
    
    db_publisher = Publisher(**publisher.model_dump())
    db.add(db_publisher)
    db.commit()
    db.refresh(db_publisher)
    
    logger.info(f"出版社创建成功: {publisher.name} (by {current_user.username})")
    return db_publisher


@router.put("/{publisher_id}", response_model=PublisherResponse)
def update_publisher(
    publisher_id: int,
    publisher_update: PublisherUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """更新出版社（需要管理员权限）"""
    db_publisher = db.query(Publisher).filter(Publisher.id == publisher_id).first()
    if not db_publisher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="出版社不存在"
        )
    
    if publisher_update.name and publisher_update.name != db_publisher.name:
        existing = db.query(Publisher).filter(
            Publisher.name == publisher_update.name,
            Publisher.id != publisher_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"出版社名称「{publisher_update.name}」已存在"
            )
    
    update_data = publisher_update.model_dump(exclude_unset=True)
    
    if 'is_active' in update_data and update_data['is_active'] is False:
        linked_books = len(db_publisher.books)
        if linked_books > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"该出版社关联了 {linked_books} 本图书，无法禁用。请先解除图书关联后再禁用。"
            )
    
    for field, value in update_data.items():
        setattr(db_publisher, field, value)
    
    db.commit()
    db.refresh(db_publisher)
    
    logger.info(f"出版社更新成功: {db_publisher.name} (by {current_user.username})")
    return db_publisher


@router.delete("/{publisher_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_publisher(
    publisher_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """删除出版社（需要管理员权限）"""
    db_publisher = db.query(Publisher).filter(Publisher.id == publisher_id).first()
    if not db_publisher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="出版社不存在"
        )
    
    if len(db_publisher.books) > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"该出版社关联了 {len(db_publisher.books)} 本图书，请先解除关联后再删除"
        )
    
    publisher_name = db_publisher.name
    db.delete(db_publisher)
    db.commit()
    
    logger.info(f"出版社删除成功: {publisher_name} (by {current_user.username})")
    return None
