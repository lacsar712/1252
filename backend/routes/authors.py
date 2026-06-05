# -*- coding: utf-8 -*-
"""
作者管理路由
"""
import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from collections import Counter

from database import get_db
from models import Author, Book, User
from schemas import (
    AuthorCreate, AuthorUpdate, AuthorResponse, AuthorListResponse,
    AuthorDetailResponse, AuthorBookCheckResponse, BookListResponse
)
from auth import get_current_admin_user, get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/authors", tags=["作者管理"])


@router.get("", response_model=AuthorListResponse)
def get_authors(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    search: Optional[str] = Query(None, description="搜索关键词（作者姓名或国家）"),
    is_active: Optional[bool] = Query(None, description="展示状态筛选"),
    db: Session = Depends(get_db)
):
    """获取作者列表（支持分页和搜索）"""
    query = db.query(Author)
    
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Author.name.like(search_pattern),
                Author.country.like(search_pattern),
                Author.bio.like(search_pattern)
            )
        )
    
    if is_active is not None:
        query = query.filter(Author.is_active == is_active)
    
    total = query.count()
    
    offset = (page - 1) * page_size
    authors = query.order_by(Author.created_at.desc()).offset(offset).limit(page_size).all()
    
    return AuthorListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=authors
    )


@router.get("/search", response_model=list)
def search_authors(
    keyword: str = Query(..., min_length=1, description="搜索关键词"),
    limit: int = Query(20, ge=1, le=100, description="返回数量限制"),
    db: Session = Depends(get_db)
):
    """作者搜索（用于下拉选择）"""
    search_pattern = f"%{keyword}%"
    authors = db.query(Author).filter(
        or_(
            Author.name.like(search_pattern),
            Author.country.like(search_pattern)
        )
    ).filter(Author.is_active == True).order_by(Author.name).limit(limit).all()
    
    return [
        {
            "id": author.id,
            "name": author.name,
            "country": author.country,
            "avatar": author.avatar
        }
        for author in authors
    ]


@router.get("/{author_id}", response_model=AuthorDetailResponse)
def get_author(author_id: int, db: Session = Depends(get_db)):
    """获取作者详情（包含关联图书、作品数量和分类分布）"""
    author = db.query(Author).filter(Author.id == author_id).first()
    if not author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="作者不存在"
        )
    
    books = author.books
    book_count = len(books)
    
    categories = [book.category for book in books if book.category]
    category_counter = Counter(categories)
    category_distribution = [
        {"category": cat, "count": count}
        for cat, count in category_counter.most_common()
    ]
    
    return AuthorDetailResponse(
        id=author.id,
        name=author.name,
        avatar=author.avatar,
        bio=author.bio,
        country=author.country,
        birth_year=author.birth_year,
        masterpieces=author.masterpieces,
        is_active=author.is_active,
        created_at=author.created_at,
        updated_at=author.updated_at,
        book_count=book_count,
        category_distribution=category_distribution,
        books=books
    )


@router.get("/{author_id}/books", response_model=BookListResponse)
def get_author_books(
    author_id: int,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db)
):
    """查询作者关联的图书列表"""
    author = db.query(Author).filter(Author.id == author_id).first()
    if not author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="作者不存在"
        )
    
    query = db.query(Book).join(Book.authors).filter(Author.id == author_id)
    
    total = query.count()
    
    offset = (page - 1) * page_size
    books = query.order_by(Book.created_at.desc()).offset(offset).limit(page_size).all()
    
    return BookListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=books
    )


@router.get("/{author_id}/check-delete", response_model=AuthorBookCheckResponse)
def check_author_delete(
    author_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """删除前检查作者关联图书"""
    author = db.query(Author).filter(Author.id == author_id).first()
    if not author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="作者不存在"
        )
    
    linked_count = len(author.books)
    
    if linked_count > 0:
        return AuthorBookCheckResponse(
            can_delete=False,
            linked_books=linked_count,
            message=f"该作者关联了 {linked_count} 本图书，请先解除关联后再删除"
        )
    else:
        return AuthorBookCheckResponse(
            can_delete=True,
            linked_books=0,
            message="可以删除该作者"
        )


@router.post("", response_model=AuthorResponse, status_code=status.HTTP_201_CREATED)
def create_author(
    author: AuthorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """创建作者（需要管理员权限）"""
    db_author = Author(**author.model_dump())
    db.add(db_author)
    db.commit()
    db.refresh(db_author)
    
    logger.info(f"作者创建成功: {author.name} (by {current_user.username})")
    return db_author


@router.put("/{author_id}", response_model=AuthorResponse)
def update_author(
    author_id: int,
    author_update: AuthorUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """更新作者（需要管理员权限）"""
    db_author = db.query(Author).filter(Author.id == author_id).first()
    if not db_author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="作者不存在"
        )
    
    update_data = author_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_author, field, value)
    
    db.commit()
    db.refresh(db_author)
    
    logger.info(f"作者更新成功: {db_author.name} (by {current_user.username})")
    return db_author


@router.delete("/{author_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_author(
    author_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """删除作者（需要管理员权限）"""
    db_author = db.query(Author).filter(Author.id == author_id).first()
    if not db_author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="作者不存在"
        )
    
    if len(db_author.books) > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"该作者关联了 {len(db_author.books)} 本图书，请先解除关联后再删除"
        )
    
    author_name = db_author.name
    db.delete(db_author)
    db.commit()
    
    logger.info(f"作者删除成功: {author_name} (by {current_user.username})")
    return None
