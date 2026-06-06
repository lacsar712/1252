# -*- coding: utf-8 -*-
"""
购物车管理路由
"""
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import CartItem, Book, User
from schemas import (
    CartItemAdd,
    CartItemUpdate,
    CartItemSelectedUpdate,
    CartItemBatchDelete,
    CartItemInfo,
    CartListResponse
)
from auth import get_current_active_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/cart", tags=["购物车"])


def _get_cart_item_with_book(db: Session, cart_item: CartItem) -> CartItemInfo:
    """获取带图书信息的购物车项"""
    book = db.query(Book).filter(Book.id == cart_item.book_id).first()
    return CartItemInfo(
        id=cart_item.id,
        user_id=cart_item.user_id,
        book_id=cart_item.book_id,
        quantity=cart_item.quantity,
        selected=cart_item.selected,
        created_at=cart_item.created_at,
        updated_at=cart_item.updated_at,
        book=book
    )


def _validate_cart_items(db: Session, user_id: int):
    """校验用户购物车所有商品状态，返回分类结果，库存不足时自动调整数量"""
    cart_items = db.query(CartItem).filter(CartItem.user_id == user_id).order_by(CartItem.created_at.desc()).all()
    
    valid_items = []
    invalid_items = []
    low_stock_items = []
    adjusted_items = []
    total_count = 0
    selected_count = 0
    total_price = 0.0
    selected_price = 0.0
    
    for cart_item in cart_items:
        book = db.query(Book).filter(Book.id == cart_item.book_id).first()
        
        if not book or book.stock <= 0:
            item_info = CartItemInfo(
                id=cart_item.id,
                user_id=cart_item.user_id,
                book_id=cart_item.book_id,
                quantity=cart_item.quantity,
                selected=cart_item.selected,
                created_at=cart_item.created_at,
                updated_at=cart_item.updated_at,
                book=book
            )
            invalid_items.append(item_info)
        else:
            adjusted_quantity = False
            if cart_item.quantity > book.stock:
                cart_item.quantity = book.stock
                db.commit()
                db.refresh(cart_item)
                adjusted_quantity = True
            
            item_info = CartItemInfo(
                id=cart_item.id,
                user_id=cart_item.user_id,
                book_id=cart_item.book_id,
                quantity=cart_item.quantity,
                selected=cart_item.selected,
                created_at=cart_item.created_at,
                updated_at=cart_item.updated_at,
                book=book
            )
            
            if adjusted_quantity:
                adjusted_items.append(item_info)
            
            if cart_item.quantity <= 3:
                low_stock_items.append(item_info)
            
            valid_items.append(item_info)
            total_count += cart_item.quantity
            total_price += cart_item.quantity * book.price
            
            if cart_item.selected:
                selected_count += cart_item.quantity
                selected_price += cart_item.quantity * book.price
    
    return CartListResponse(
        items=valid_items,
        total_count=total_count,
        selected_count=selected_count,
        total_price=round(total_price, 2),
        selected_price=round(selected_price, 2),
        invalid_items=invalid_items,
        low_stock_items=low_stock_items,
        adjusted_items=adjusted_items
    )


@router.get("", response_model=CartListResponse)
def get_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取当前用户购物车列表"""
    return _validate_cart_items(db, current_user.id)


@router.get("/count", response_model=int)
def get_cart_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取当前用户购物车商品总数"""
    cart_items = db.query(CartItem).filter(
        CartItem.user_id == current_user.id
    ).all()
    
    total = 0
    for cart_item in cart_items:
        book = db.query(Book).filter(Book.id == cart_item.book_id).first()
        if book and book.stock > 0:
            total += cart_item.quantity
    
    return total


@router.post("", response_model=CartListResponse, status_code=status.HTTP_201_CREATED)
def add_to_cart(
    cart_add: CartItemAdd,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """添加商品到购物车，已存在则合并数量"""
    book = db.query(Book).filter(Book.id == cart_add.book_id).first()
    
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="图书不存在"
        )
    
    if book.stock <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="图书已缺货，无法加入购物车"
        )
    
    existing_item = db.query(CartItem).filter(
        CartItem.user_id == current_user.id,
        CartItem.book_id == cart_add.book_id
    ).first()
    
    if existing_item:
        new_quantity = existing_item.quantity + cart_add.quantity
        if new_quantity > book.stock:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"库存不足，购物车已有 {existing_item.quantity} 本，当前库存 {book.stock} 本"
            )
        existing_item.quantity = new_quantity
        existing_item.selected = True
        logger.info(f"购物车商品数量更新: 用户 {current_user.username}, 图书 {book.title}, 数量 {new_quantity}")
    else:
        if cart_add.quantity > book.stock:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"库存不足，当前库存 {book.stock} 本"
            )
        db_cart_item = CartItem(
            user_id=current_user.id,
            book_id=cart_add.book_id,
            quantity=cart_add.quantity,
            selected=True
        )
        db.add(db_cart_item)
        logger.info(f"商品加入购物车: 用户 {current_user.username}, 图书 {book.title}, 数量 {cart_add.quantity}")
    
    db.commit()
    return _validate_cart_items(db, current_user.id)


@router.put("/{cart_item_id}", response_model=CartListResponse)
def update_cart_item_quantity(
    cart_item_id: int,
    cart_update: CartItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新购物车商品数量"""
    cart_item = db.query(CartItem).filter(
        CartItem.id == cart_item_id,
        CartItem.user_id == current_user.id
    ).first()
    
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="购物车项不存在"
        )
    
    book = db.query(Book).filter(Book.id == cart_item.book_id).first()
    
    if not book:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="图书已失效，请删除该商品"
        )
    
    if book.stock <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="图书已缺货"
        )
    
    if cart_update.quantity > book.stock:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"库存不足，当前库存 {book.stock} 本"
        )
    
    cart_item.quantity = cart_update.quantity
    db.commit()
    
    logger.info(f"购物车商品数量更新: 用户 {current_user.username}, 购物车项ID {cart_item_id}, 数量 {cart_update.quantity}")
    return _validate_cart_items(db, current_user.id)


@router.patch("/{cart_item_id}/selected", response_model=CartListResponse)
def update_cart_item_selected(
    cart_item_id: int,
    selected_update: CartItemSelectedUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新购物车商品选中状态"""
    cart_item = db.query(CartItem).filter(
        CartItem.id == cart_item_id,
        CartItem.user_id == current_user.id
    ).first()
    
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="购物车项不存在"
        )
    
    cart_item.selected = selected_update.selected
    db.commit()
    
    return _validate_cart_items(db, current_user.id)


@router.patch("/selected/all", response_model=CartListResponse)
def update_all_cart_items_selected(
    selected_update: CartItemSelectedUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """全选/取消全选购物车商品"""
    cart_items = db.query(CartItem).filter(
        CartItem.user_id == current_user.id
    ).all()
    
    for cart_item in cart_items:
        book = db.query(Book).filter(Book.id == cart_item.book_id).first()
        if book and book.stock > 0:
            cart_item.selected = selected_update.selected
    
    db.commit()
    return _validate_cart_items(db, current_user.id)


@router.delete("/{cart_item_id}", response_model=CartListResponse)
def delete_cart_item(
    cart_item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除购物车单个商品"""
    cart_item = db.query(CartItem).filter(
        CartItem.id == cart_item_id,
        CartItem.user_id == current_user.id
    ).first()
    
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="购物车项不存在"
        )
    
    book = db.query(Book).filter(Book.id == cart_item.book_id).first()
    book_title = book.title if book else "未知图书"
    
    db.delete(cart_item)
    db.commit()
    
    logger.info(f"购物车商品删除: 用户 {current_user.username}, 图书 {book_title}")
    return _validate_cart_items(db, current_user.id)


@router.post("/batch-delete", response_model=CartListResponse)
def batch_delete_cart_items(
    batch_delete: CartItemBatchDelete,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """批量删除购物车商品"""
    cart_items = db.query(CartItem).filter(
        CartItem.id.in_(batch_delete.cart_item_ids),
        CartItem.user_id == current_user.id
    ).all()
    
    for cart_item in cart_items:
        db.delete(cart_item)
    
    db.commit()
    
    logger.info(f"购物车批量删除: 用户 {current_user.username}, 删除 {len(cart_items)} 项")
    return _validate_cart_items(db, current_user.id)


@router.delete("/clear/invalid", response_model=CartListResponse)
def clear_invalid_items(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """清空失效购物车商品"""
    cart_items = db.query(CartItem).filter(
        CartItem.user_id == current_user.id
    ).all()
    
    deleted_count = 0
    for cart_item in cart_items:
        book = db.query(Book).filter(Book.id == cart_item.book_id).first()
        if not book or book.stock <= 0:
            db.delete(cart_item)
            deleted_count += 1
    
    db.commit()
    
    logger.info(f"清空失效购物车商品: 用户 {current_user.username}, 清理 {deleted_count} 项")
    return _validate_cart_items(db, current_user.id)


@router.delete("", response_model=CartListResponse)
def clear_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """清空购物车"""
    cart_items = db.query(CartItem).filter(
        CartItem.user_id == current_user.id
    ).all()
    
    for cart_item in cart_items:
        db.delete(cart_item)
    
    db.commit()
    
    logger.info(f"清空购物车: 用户 {current_user.username}, 删除 {len(cart_items)} 项")
    return _validate_cart_items(db, current_user.id)
