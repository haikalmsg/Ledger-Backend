from math import ceil
import token
from uuid import UUID
from app.core import security
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from typing import List

from app.core.database import get_db
from app.schemas.account import AccountCreate, AccountOut, AccountListResponse, AccountUpdate, AccountBalanceResponse
from app.crud import account as crud_account
from app.services import account_service
router = APIRouter(prefix="/accounts", tags=["accounts"])
bearer_scheme = HTTPBearer()
@router.post("/", response_model=AccountOut, status_code=status.HTTP_201_CREATED)
def create_account(
    account_in: AccountCreate,
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
    try: 
        return crud_account.create_account(db, account_in, user_id=UUID(user_id))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
@router.get("/", response_model=AccountListResponse)
def list_accounts(
    page: int = 1,
    limit: int = 10,
    search: str | None = None,
    status: bool | None = None,
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
    skip = (page - 1) * limit
    accounts = crud_account.get_account_paginated(db, user_id=UUID(user_id), skip=skip, limit=limit, search=search, status=status)
    total_accounts = crud_account.get_account_total(db, user_id=UUID(user_id), search=search, status=status)
    total_pages = ceil(total_accounts / limit) if total_accounts > 0 else 1
    return AccountListResponse(
        data=accounts,
        next=page < total_pages,
        previous=page > 1,
        page=page,
        limit=limit,
        total_pages=total_pages,
        total=total_accounts
    )
@router.get("/{account_id}", response_model=AccountOut)
def read_account(
    account_id: UUID,
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
    account = crud_account.get_account(db, account_id, user_id=UUID(user_id))
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account
@router.put("/{account_id}", response_model=AccountOut)
def update_account(
    account_id: UUID,
    account_in: AccountUpdate,
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
    account = crud_account.update_account(db, account_id, user_id=UUID(user_id), account_in=account_in)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account
@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(
    account_id: UUID,
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
    success = crud_account.delete_account(db, account_id, user_id=UUID(user_id))
    if not success:
        raise HTTPException(status_code=404, detail="Account not found")

@router.get("/balance/{account_id}", response_model=AccountBalanceResponse)
def get_account_balance(
    account_id: UUID,
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
    try:
        balance = account_service.get_account_balance(db, user_id=UUID(user_id), account_id=account_id)
        return AccountBalanceResponse(account_id=account_id, balance=float(balance))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)
)