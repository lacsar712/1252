# -*- coding: utf-8 -*-
"""
图书管理路由
"""
import logging
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from database import get_db
from models import Book, User, Author, Publisher, Tag, book_tag
from schemas import BookCreate, BookUpdate, BookResponse, BookListResponse, PublisherResponse, BookTagsUpdateRequest
from auth import get_current_admin_user, get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/books", tags=["图书管理"])


def _build_book_response(book: Book, db: Session) -> BookResponse:
    """构建包含出版社、作者和标签信息的图书响应"""
    publisher_info = None
    if book.publisher_id:
        publisher = db.query(Publisher).filter(Publisher.id == book.publisher_id).first()
        if publisher:
            publisher_info = PublisherResponse.model_validate(publisher)
    
    book_dict = {c.name: getattr(book, c.name) for c in book.__table__.columns}
    book_dict['authors'] = book.authors
    book_dict['publisher_info'] = publisher_info
    book_dict['tags'] = book.tags
    
    return BookResponse(**book_dict)


@router.get("", response_model=BookListResponse)
def get_books(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    search: Optional[str] = Query(None, description="搜索关键词（书名或作者）"),
    category: Optional[str] = Query(None, description="分类筛选"),
    tag_id: Optional[int] = Query(None, description="标签ID筛选"),
    low_stock: Optional[bool] = Query(None, description="只显示低库存图书（库存<10）"),
    db: Session = Depends(get_db)
):
    """获取图书列表（支持分页、搜索、分类、标签和低库存筛选）"""
    query = db.query(Book)
    
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Book.title.like(search_pattern),
                Book.author.like(search_pattern),
                Book.publisher.like(search_pattern)
            )
        )
    
    if category:
        query = query.filter(Book.category == category)
    
    if tag_id:
        query = query.join(book_tag).filter(book_tag.c.tag_id == tag_id)

    if low_stock:
        query = query.filter(Book.stock < 10)
    
    total = query.count()
    
    offset = (page - 1) * page_size
    books = query.order_by(Book.created_at.desc()).offset(offset).limit(page_size).all()
    
    book_responses = [_build_book_response(book, db) for book in books]
    
    return BookListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=book_responses
    )


@router.get("/categories/list", response_model=list)
def get_categories(db: Session = Depends(get_db)):
    """获取所有分类"""
    categories = db.query(Book.category).distinct().filter(Book.category.isnot(None)).all()
    return [cat[0] for cat in categories if cat[0]]


@router.get("/{book_id}", response_model=BookResponse)
def get_book(book_id: int, db: Session = Depends(get_db)):
    """获取图书详情"""
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="图书不存在"
        )
    return _build_book_response(book, db)


@router.post("", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(
    book: BookCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """创建图书（需要管理员权限）"""
    if book.isbn:
        existing_book = db.query(Book).filter(Book.isbn == book.isbn).first()
        if existing_book:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ISBN已存在"
            )
    
    book_data = book.model_dump()
    author_ids = book_data.pop('author_ids', None)
    publisher_id = book_data.pop('publisher_id', None)
    tag_ids = book_data.pop('tag_ids', None)
    
    db_book = Book(**book_data)
    
    if publisher_id:
        publisher = db.query(Publisher).filter(Publisher.id == publisher_id).first()
        if not publisher:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="出版社不存在"
            )
        if not publisher.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"出版社「{publisher.name}」已被禁用，无法关联"
            )
        db_book.publisher_id = publisher_id
        db_book.publisher = publisher.name
    
    if author_ids:
        authors = db.query(Author).filter(Author.id.in_(author_ids)).all()
        if len(authors) != len(author_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="部分作者不存在"
            )
        db_book.authors = authors
    
    if tag_ids:
        tags = db.query(Tag).filter(Tag.id.in_(tag_ids)).all()
        if len(tags) != len(tag_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="部分标签不存在"
            )
        inactive_tags = [t for t in tags if not t.is_active]
        if inactive_tags:
            inactive_names = "、".join([t.name for t in inactive_tags])
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"标签「{inactive_names}」已被禁用，无法关联"
            )
        db_book.tags = tags
    
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    
    logger.info(f"图书创建成功: {book.title} (by {current_user.username})")
    return _build_book_response(db_book, db)


@router.put("/{book_id}", response_model=BookResponse)
def update_book(
    book_id: int,
    book_update: BookUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """更新图书（需要管理员权限）"""
    db_book = db.query(Book).filter(Book.id == book_id).first()
    if not db_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="图书不存在"
        )
    
    update_data = book_update.model_dump(exclude_unset=True)
    author_ids = update_data.pop('author_ids', None)
    tag_ids = update_data.pop('tag_ids', None)
    
    has_publisher_id = 'publisher_id' in update_data
    publisher_id = update_data.pop('publisher_id', None)
    
    for field, value in update_data.items():
        setattr(db_book, field, value)
    
    if has_publisher_id:
        if publisher_id is None or publisher_id == 0:
            db_book.publisher_id = None
            db_book.publisher = None
        else:
            publisher = db.query(Publisher).filter(Publisher.id == publisher_id).first()
            if not publisher:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="出版社不存在"
                )
            if not publisher.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"出版社「{publisher.name}」已被禁用，无法关联"
                )
            db_book.publisher_id = publisher_id
            db_book.publisher = publisher.name
    
    if author_ids is not None:
        if len(author_ids) > 0:
            authors = db.query(Author).filter(Author.id.in_(author_ids)).all()
            if len(authors) != len(author_ids):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="部分作者不存在"
                )
            db_book.authors = authors
        else:
            db_book.authors = []
    
    if tag_ids is not None:
        if len(tag_ids) > 0:
            tags = db.query(Tag).filter(Tag.id.in_(tag_ids)).all()
            if len(tags) != len(tag_ids):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="部分标签不存在"
                )
            inactive_tags = [t for t in tags if not t.is_active]
            if inactive_tags:
                inactive_names = "、".join([t.name for t in inactive_tags])
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"标签「{inactive_names}」已被禁用，无法关联"
                )
            db_book.tags = tags
        else:
            db_book.tags = []
    
    db.commit()
    db.refresh(db_book)
    
    logger.info(f"图书更新成功: {db_book.title} (by {current_user.username})")
    return _build_book_response(db_book, db)


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """删除图书（需要管理员权限）"""
    db_book = db.query(Book).filter(Book.id == book_id).first()
    if not db_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="图书不存在"
        )
    
    book_title = db_book.title
    db.delete(db_book)
    db.commit()
    
    logger.info(f"图书删除成功: {book_title} (by {current_user.username})")
    return None
