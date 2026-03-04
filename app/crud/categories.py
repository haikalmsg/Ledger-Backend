from uuid import UUID
from sqlalchemy.orm import Session
from pwdlib import PasswordHash

from app.models.categories import Category
from app.schemas.categories import CategoryCreate, CategoryUpdate

def get_category_paginated(db: Session, user_id: UUID, skip: int, limit: int) -> list[Category]:
    return db.query(Category).filter(Category.user_id == user_id).offset(skip).limit(limit).all()
def get_category(db: Session, category_id: UUID, user_id: UUID) -> Category | None:
    return db.query(Category).filter(Category.id == category_id, Category.user_id == user_id).first()
def get_category_count(db: Session, user_id: UUID) -> int:
    return db.query(Category).filter(Category.user_id == user_id).count()
def create_category(db: Session, category_in: CategoryCreate, user_id: UUID) -> Category:
    new_category = Category(
        name=category_in.name,
        is_active=category_in.is_active,
        user_id=user_id
    )
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category

def update_category(db: Session, category_id: UUID, user_id: UUID, category_in: CategoryUpdate) -> Category | None:
    category = get_category(db, category_id, user_id)
    if not category:
        return None
    if category_in.name is not None:
        category.name = category_in.name
    if category_in.is_active is not None:
        category.is_active = category_in.is_active
    db.commit()
    db.refresh(category)
    return category