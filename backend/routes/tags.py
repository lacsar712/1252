# -*- coding: utf-8 -*-
"""
标签管理路由
"""
import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from database import get_db
from models import Tag, Book, User, book_tag
from schemas import (
    TagCreate, TagUpdate, TagResponse, TagListResponse,
    TagNameCheckResponse, TagBookCheckResponse, BookListResponse
)
from auth import get_current_admin_user, get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/tags", tags=["标签管理"])


@router.get("", response_model=TagListResponse)
def get_tags(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    search: Optional[str] = Query(None, description="搜索关键词（标签名称或说明）"),
    is_active: Optional[bool] = Query(None, description="启用状态筛选"),
    db: Session = Depends(get_db)
):
    """获取标签列表（支持分页、搜索和状态筛选）"""
    query = db.query(Tag)
    
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Tag.name.like(search_pattern),
                Tag.description.like(search_pattern)
            )
        )
    
    if is_active is not None:
        query = query.filter(Tag.is_active == is_active)
    
    total = query.count()
    
    offset = (page - 1) * page_size
    tags = query.order_by(Tag.sort_order.asc(), Tag.created_at.desc()).offset(offset).limit(page_size).all()
    
    return TagListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=tags
    )


@router.get("/active", response_model=list)
def get_active_tags(db: Session = Depends(get_db)):
    """获取所有启用的标签（用于前台筛选和下拉选择）"""
    tags = db.query(Tag).filter(Tag.is_active == True).order_by(Tag.sort_order.asc(), Tag.name.asc()).all()
    return [TagResponse.model_validate(tag) for tag in tags]


@router.get("/all", response_model=list)
def get_all_tags(
    include_inactive: bool = Query(True, description="是否包含已禁用标签"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """获取所有标签（后台管理用，可选包含已禁用）"""
    query = db.query(Tag)
    if not include_inactive:
        query = query.filter(Tag.is_active == True)
    tags = query.order_by(Tag.sort_order.asc(), Tag.name.asc()).all()
    return [TagResponse.model_validate(tag) for tag in tags]


@router.get("/search", response_model=list)
def search_tags(
    keyword: str = Query(..., min_length=1, description="搜索关键词"),
    limit: int = Query(20, ge=1, le=100, description="返回数量限制"),
    include_inactive: bool = Query(False, description="是否包含已禁用的标签"),
    db: Session = Depends(get_db)
):
    """标签搜索（用于下拉选择）"""
    search_pattern = f"%{keyword}%"
    query = db.query(Tag).filter(Tag.name.like(search_pattern))
    
    if not include_inactive:
        query = query.filter(Tag.is_active == True)
    
    tags = query.order_by(Tag.sort_order.asc(), Tag.name.asc()).limit(limit).all()
    
    return [TagResponse.model_validate(tag) for tag in tags]


@router.get("/check-name", response_model=TagNameCheckResponse)
def check_tag_name(
    name: str = Query(..., min_length=1, description="标签名称"),
    exclude_id: Optional[int] = Query(None, description="排除的标签ID（编辑时使用）"),
    db: Session = Depends(get_db)
):
    """校验标签名称唯一性"""
    query = db.query(Tag).filter(Tag.name == name)
    
    if exclude_id is not None:
        query = query.filter(Tag.id != exclude_id)
    
    existing = query.first()
    
    if existing:
        return TagNameCheckResponse(
            available=False,
            message=f"标签名称「{name}」已存在"
        )
    else:
        return TagNameCheckResponse(
            available=True,
            message="名称可用"
        )


@router.get("/{tag_id}", response_model=TagResponse)
def get_tag(tag_id: int, db: Session = Depends(get_db)):
    """获取标签详情"""
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="标签不存在"
        )
    return tag


@router.get("/{tag_id}/books", response_model=BookListResponse)
def get_tag_books(
    tag_id: int,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db)
):
    """查询标签关联的图书列表（前台使用，仅包含启用标签的图书）"""
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="标签不存在"
        )
    
    query = db.query(Book).join(book_tag).filter(book_tag.c.tag_id == tag_id)
    
    total = query.count()
    
    offset = (page - 1) * page_size
    books = query.order_by(Book.created_at.desc()).offset(offset).limit(page_size).all()
    
    return BookListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=books
    )


@router.get("/{tag_id}/check-delete", response_model=TagBookCheckResponse)
def check_tag_delete(
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """删除前检查标签关联图书"""
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="标签不存在"
        )
    
    linked_count = len(tag.books)
    
    if linked_count > 0:
        return TagBookCheckResponse(
            can_delete=False,
            linked_books=linked_count,
            message=f"该标签关联了 {linked_count} 本图书，请先解除关联后再删除"
        )
    else:
        return TagBookCheckResponse(
            can_delete=True,
            linked_books=0,
            message="可以删除该标签"
        )


@router.post("", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
def create_tag(
    tag: TagCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """创建标签（需要管理员权限）"""
    existing = db.query(Tag).filter(Tag.name == tag.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"标签名称「{tag.name}」已存在"
        )
    
    db_tag = Tag(**tag.model_dump())
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    
    logger.info(f"标签创建成功: {tag.name} (by {current_user.username})")
    return db_tag


@router.put("/{tag_id}", response_model=TagResponse)
def update_tag(
    tag_id: int,
    tag_update: TagUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """更新标签（需要管理员权限）"""
    db_tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not db_tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="标签不存在"
        )
    
    if tag_update.name and tag_update.name != db_tag.name:
        existing = db.query(Tag).filter(
            Tag.name == tag_update.name,
            Tag.id != tag_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"标签名称「{tag_update.name}」已存在"
            )
    
    update_data = tag_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_tag, field, value)
    
    db.commit()
    db.refresh(db_tag)
    
    logger.info(f"标签更新成功: {db_tag.name} (by {current_user.username})")
    return db_tag


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """删除标签（需要管理员权限）"""
    db_tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not db_tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="标签不存在"
        )
    
    if len(db_tag.books) > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"该标签关联了 {len(db_tag.books)} 本图书，请先解除关联后再删除"
        )
    
    tag_name = db_tag.name
    db.delete(db_tag)
    db.commit()
    
    logger.info(f"标签删除成功: {tag_name} (by {current_user.username})")
    return None
