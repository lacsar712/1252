# -*- coding: utf-8 -*-
"""
主题书单管理路由
"""
import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func, text

from database import get_db
from models import BookList, Book, User, book_list_book
from schemas import (
    BookListCreate, BookListUpdate, ThemeBookListResponse, BookListListResponse,
    BookListDetailResponse, BookListAddBooksRequest, BookListUpdateBookRequest,
    BookListBookResponse, BookListReorderRequest
)
from auth import get_current_admin_user, get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/book-lists", tags=["主题书单"])


@router.get("", response_model=BookListListResponse)
def get_book_lists(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    search: Optional[str] = Query(None, description="搜索关键词（书单标题或简介）"),
    is_active: Optional[bool] = Query(None, description="展示状态筛选"),
    category: Optional[str] = Query(None, description="分类筛选"),
    db: Session = Depends(get_db)
):
    """获取书单列表（支持分页、搜索和筛选）"""
    query = db.query(BookList)
    
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                BookList.title.like(search_pattern),
                BookList.description.like(search_pattern)
            )
        )
    
    if is_active is not None:
        query = query.filter(BookList.is_active == is_active)
    
    if category:
        query = query.filter(BookList.category == category)
    
    total = query.count()
    
    offset = (page - 1) * page_size
    book_lists = query.order_by(BookList.sort_weight.desc(), BookList.created_at.desc()).offset(offset).limit(page_size).all()
    
    return BookListListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=book_lists
    )


@router.get("/categories", response_model=list)
def get_book_list_categories(db: Session = Depends(get_db)):
    """获取所有书单分类"""
    categories = db.query(BookList.category).filter(
        BookList.category.isnot(None),
        BookList.category != ''
    ).distinct().all()
    return [cat[0] for cat in categories if cat[0]]


@router.get("/{book_list_id}", response_model=BookListDetailResponse)
def get_book_list(
    book_list_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """获取书单详情（包含关联图书、推荐语和排序）"""
    book_list = db.query(BookList).filter(BookList.id == book_list_id).first()
    if not book_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="书单不存在"
        )
    
    if not book_list.is_active:
        is_admin = current_user and current_user.is_admin
        if not is_admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="书单不存在"
            )
    
    stmt = text("""
        SELECT b.id, b.title, b.author, b.cover_image, b.price, b.category,
               blb.sort_order, blb.recommendation
        FROM books b
        JOIN book_list_book blb ON b.id = blb.book_id
        WHERE blb.book_list_id = :list_id
        ORDER BY blb.sort_order ASC
    """)
    
    result = db.execute(stmt, {"list_id": book_list_id}).fetchall()
    
    books = [
        BookListBookResponse(
            id=row.id,
            title=row.title,
            author=row.author,
            cover_image=row.cover_image,
            price=row.price,
            category=row.category,
            sort_order=row.sort_order,
            recommendation=row.recommendation
        )
        for row in result
    ]
    
    categories = list(set([book.category for book in books if book.category]))
    
    return BookListDetailResponse(
        id=book_list.id,
        title=book_list.title,
        description=book_list.description,
        cover_image=book_list.cover_image,
        is_active=book_list.is_active,
        sort_weight=book_list.sort_weight,
        category=book_list.category,
        created_at=book_list.created_at,
        updated_at=book_list.updated_at,
        book_count=len(books),
        books=books,
        categories=categories
    )


@router.post("", response_model=ThemeBookListResponse, status_code=status.HTTP_201_CREATED)
def create_book_list(
    book_list_data: BookListCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """创建书单（需要管理员权限）"""
    db_book_list = BookList(
        title=book_list_data.title,
        description=book_list_data.description,
        cover_image=book_list_data.cover_image,
        is_active=book_list_data.is_active,
        sort_weight=book_list_data.sort_weight,
        category=book_list_data.category
    )
    db.add(db_book_list)
    db.flush()
    
    if book_list_data.books:
        for book_item in book_list_data.books:
            book = db.query(Book).filter(Book.id == book_item.book_id).first()
            if book:
                check_stmt = text("""
                    SELECT COUNT(*) as count FROM book_list_book
                    WHERE book_list_id = :list_id AND book_id = :book_id
                """)
                result = db.execute(check_stmt, {"list_id": db_book_list.id, "book_id": book_item.book_id}).fetchone()
                
                if result.count > 0:
                    stmt = text("""
                        UPDATE book_list_book
                        SET sort_order = :sort_order, recommendation = :recommendation
                        WHERE book_list_id = :list_id AND book_id = :book_id
                    """)
                else:
                    stmt = text("""
                        INSERT INTO book_list_book (book_list_id, book_id, sort_order, recommendation, created_at)
                        VALUES (:list_id, :book_id, :sort_order, :recommendation, datetime('now'))
                    """)
                
                db.execute(stmt, {
                    "list_id": db_book_list.id,
                    "book_id": book_item.book_id,
                    "sort_order": book_item.sort_order,
                    "recommendation": book_item.recommendation
                })
    
    db.commit()
    db.refresh(db_book_list)
    
    logger.info(f"书单创建成功: {book_list_data.title} (by {current_user.username})")
    return db_book_list


@router.put("/{book_list_id}", response_model=ThemeBookListResponse)
def update_book_list(
    book_list_id: int,
    book_list_update: BookListUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """更新书单基本信息（需要管理员权限）"""
    db_book_list = db.query(BookList).filter(BookList.id == book_list_id).first()
    if not db_book_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="书单不存在"
        )
    
    update_data = book_list_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_book_list, field, value)
    
    db.commit()
    db.refresh(db_book_list)
    
    logger.info(f"书单更新成功: {db_book_list.title} (by {current_user.username})")
    return db_book_list


@router.delete("/{book_list_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book_list(
    book_list_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """删除书单（需要管理员权限）"""
    db_book_list = db.query(BookList).filter(BookList.id == book_list_id).first()
    if not db_book_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="书单不存在"
        )
    
    stmt = text("DELETE FROM book_list_book WHERE book_list_id = :list_id")
    db.execute(stmt, {"list_id": book_list_id})
    
    list_title = db_book_list.title
    db.delete(db_book_list)
    db.commit()
    
    logger.info(f"书单删除成功: {list_title} (by {current_user.username})")
    return None


@router.post("/{book_list_id}/books", response_model=BookListDetailResponse)
def add_books_to_list(
    book_list_id: int,
    request: BookListAddBooksRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """批量添加图书到书单（需要管理员权限）"""
    db_book_list = db.query(BookList).filter(BookList.id == book_list_id).first()
    if not db_book_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="书单不存在"
        )
    
    for book_item in request.books:
        book = db.query(Book).filter(Book.id == book_item.book_id).first()
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"图书ID {book_item.book_id} 不存在"
            )
        
        check_stmt = text("""
            SELECT COUNT(*) as count FROM book_list_book
            WHERE book_list_id = :list_id AND book_id = :book_id
        """)
        result = db.execute(check_stmt, {"list_id": book_list_id, "book_id": book_item.book_id}).fetchone()
        
        if result.count > 0:
            stmt = text("""
                UPDATE book_list_book
                SET sort_order = :sort_order, recommendation = :recommendation
                WHERE book_list_id = :list_id AND book_id = :book_id
            """)
        else:
            stmt = text("""
                INSERT INTO book_list_book (book_list_id, book_id, sort_order, recommendation, created_at)
                VALUES (:list_id, :book_id, :sort_order, :recommendation, datetime('now'))
            """)
        
        db.execute(stmt, {
            "list_id": book_list_id,
            "book_id": book_item.book_id,
            "sort_order": book_item.sort_order,
            "recommendation": book_item.recommendation
        })
    
    db.commit()
    return get_book_list(book_list_id, db)


@router.put("/{book_list_id}/books/{book_id}", response_model=BookListDetailResponse)
def update_book_in_list(
    book_list_id: int,
    book_id: int,
    request: BookListUpdateBookRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """更新书单中图书的排序和推荐语（需要管理员权限）"""
    db_book_list = db.query(BookList).filter(BookList.id == book_list_id).first()
    if not db_book_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="书单不存在"
        )
    
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="图书不存在"
        )
    
    check_stmt = text("""
        SELECT COUNT(*) as count FROM book_list_book
        WHERE book_list_id = :list_id AND book_id = :book_id
    """)
    result = db.execute(check_stmt, {"list_id": book_list_id, "book_id": book_id}).fetchone()
    if result.count == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该图书不在书单中"
        )
    
    update_fields = []
    params = {"list_id": book_list_id, "book_id": book_id}
    
    if request.sort_order is not None:
        update_fields.append("sort_order = :sort_order")
        params["sort_order"] = request.sort_order
    
    if request.recommendation is not None:
        update_fields.append("recommendation = :recommendation")
        params["recommendation"] = request.recommendation
    
    if update_fields:
        stmt = text(f"""
            UPDATE book_list_book
            SET {', '.join(update_fields)}
            WHERE book_list_id = :list_id AND book_id = :book_id
        """)
        db.execute(stmt, params)
        db.commit()
    
    return get_book_list(book_list_id, db)


@router.delete("/{book_list_id}/books/{book_id}", response_model=BookListDetailResponse)
def remove_book_from_list(
    book_list_id: int,
    book_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """从书单中移除图书（需要管理员权限）"""
    db_book_list = db.query(BookList).filter(BookList.id == book_list_id).first()
    if not db_book_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="书单不存在"
        )
    
    stmt = text("""
        DELETE FROM book_list_book
        WHERE book_list_id = :list_id AND book_id = :book_id
    """)
    db.execute(stmt, {"list_id": book_list_id, "book_id": book_id})
    db.commit()
    
    return get_book_list(book_list_id, db)


@router.put("/{book_list_id}/books/reorder", response_model=BookListDetailResponse)
def reorder_books_in_list(
    book_list_id: int,
    request: BookListReorderRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """调整书单中图书顺序（需要管理员权限）"""
    db_book_list = db.query(BookList).filter(BookList.id == book_list_id).first()
    if not db_book_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="书单不存在"
        )
    
    for index, book_id in enumerate(request.book_ids):
        stmt = text("""
            UPDATE book_list_book
            SET sort_order = :sort_order
            WHERE book_list_id = :list_id AND book_id = :book_id
        """)
        db.execute(stmt, {
            "list_id": book_list_id,
            "book_id": book_id,
            "sort_order": index
        })
    
    db.commit()
    return get_book_list(book_list_id, db)
