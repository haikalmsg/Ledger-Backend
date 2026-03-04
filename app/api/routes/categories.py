import token
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from typing import List

from app.core.database import get_db
from app.schemas.categories import CategoryCreate, CategoryOut, CategoryUpdate, CategoryListResponse
from app.core import security
from app.crud import categories as crud_categories
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
    return crud_categories.create_category(db, category_in, user_id=UUID(user_id))
@router.get("/", response_model=CategoryListResponse)
def read_categories(
    skip: int = 0,
    limit: int = 10,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    token_decrypt = security.decode_token(token)
    if token_decrypt is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    user_id = token_decrypt.get("user_id")
    total = crud_categories.get_category_count(db, user_id=UUID(user_id))
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    return CategoryListResponse(
        data=crud_categories.get_category_paginated(db, user_id=UUID(user_id), skip=skip, limit=limit),
        next=skip + limit < total,
        previous=skip > 0,
        page=skip // limit + 1,
        limit=limit,
        total=total
    )