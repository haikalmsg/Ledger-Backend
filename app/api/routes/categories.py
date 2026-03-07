from math import ceil
import token
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from typing import List

from app.core.database import get_db
from app.schemas.categories import CategoryCreate, CategoryOut, CategoryUpdate, CategoryListResponse, CategoryListRequest
from app.core import security
from app.crud import categories as crud_categories
from app.crud import users as crud_users


router = APIRouter(prefix="/categories", tags=["categories"])
bearer_scheme = HTTPBearer()
@router.post("/", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
def create_category(
    category_in: CategoryCreate,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    token_decrypt = security.decode_token(token)
    if token_decrypt is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    user_id = token_decrypt.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    if not crud_users.get_user(db, user_id=UUID(user_id)):
        raise HTTPException(status_code=401, detail="Invalid token")
    try : 
        return crud_categories.create_category(db, category_in, user_id=UUID(user_id))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
@router.get("/", response_model=CategoryListResponse)
def read_categories(
    category_list: CategoryListRequest = Depends(),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    token_decrypt = security.decode_token(token)
    if token_decrypt is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    user_id = token_decrypt.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    if not crud_users.get_user(db, user_id=UUID(user_id)):
        raise HTTPException(status_code=401, detail="Invalid token")
    total = crud_categories.get_category_count(db, user_id=UUID(user_id), search=category_list.search, status=category_list.status)
    return CategoryListResponse(
        data=crud_categories.get_category_paginated(db, user_id=UUID(user_id), skip=(category_list.page - 1) * category_list.limit, limit=category_list.limit, search=category_list.search, sort_by=category_list.sort_by, direction=category_list.direction, status=category_list.status),
        next=(category_list.page - 1) * category_list.limit + category_list.limit < total,
        previous=category_list.page > 1,
        page=category_list.page,
        limit=category_list.limit,
        total_pages = ceil(total/category_list.limit) if total > 0 else 1,
        total=total
    )
@router.get("/{category_id}", response_model=CategoryOut)
def read_category(
    category_id: UUID,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    token_decrypt = security.decode_token(token)
    if token_decrypt is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    user_id = token_decrypt.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    if not crud_users.get_user(db, user_id=UUID(user_id)):
        raise HTTPException(status_code=401, detail="Invalid token")
    category = crud_categories.get_category(db, category_id=category_id, user_id=UUID(user_id))
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category
@router.put("/{category_id}", response_model=CategoryOut)
def update_category(
    category_id: UUID,
    category_in: CategoryUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    token_decrypt = security.decode_token(token)
    if token_decrypt is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    user_id = token_decrypt.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    if not crud_users.get_user(db, user_id=UUID(user_id)):
        raise HTTPException(status_code=401, detail="Invalid token")
    category = crud_categories.update_category(db, category_id=category_id, category_in=category_in, user_id=UUID(user_id))
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category
@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: UUID,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    token_decrypt = security.decode_token(token)
    if token_decrypt is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    user_id = token_decrypt.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    if not crud_users.get_user(db, user_id=UUID(user_id)):
        raise HTTPException(status_code=401, detail="Invalid token")
    category = crud_categories.get_category(db, category_id=category_id, user_id=UUID(user_id))
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(category)
    db.commit()