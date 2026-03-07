import token
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from math import ceil

from app.core.database import get_db
from app.schemas.transactions import TransactionCreate, TransactionOut, TransactionUpdate, TransactionListResponse, TransactionListRequest
from app.core import security
from app.crud import transactions as crud_transactions
from app.crud import users as crud_users

router = APIRouter(prefix="/transactions", tags=["transactions"])
bearer_scheme = HTTPBearer()
@router.post("/", response_model=TransactionOut, status_code=status.HTTP_201_CREATED)
def create_transaction(
    transaction_in: TransactionCreate,
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
    if transaction_in.kind not in ("income", "expense"):
        raise HTTPException(status_code=400, detail="Invalid transaction kind. Must be 'income' or 'expense'.")
    try: 
        return crud_transactions.create_transaction(db, transaction_in, user_id=UUID(user_id))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=TransactionListResponse)
def list_transactions(
    transaction_list: TransactionListRequest = Depends(),
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
    total = crud_transactions.get_transaction_count(db, user_id=UUID(user_id), search=transaction_list.search, kind=transaction_list.kind, account_id=transaction_list.account_id)
    return TransactionListResponse(
        data=crud_transactions.get_transaction_paginated(db, user_id=UUID(user_id), skip=(transaction_list.page - 1) * transaction_list.limit, limit=transaction_list.limit, search=transaction_list.search, kind=transaction_list.kind, account_id=transaction_list.account_id),
        next=(transaction_list.page - 1) * transaction_list.limit + transaction_list.limit < total,
        previous=transaction_list.page > 1,
        page=transaction_list.page,
        limit=transaction_list.limit,
        total_pages = ceil(total/transaction_list.limit) if total > 0 else 1,
        total=total
    )
@router.get("/{transaction_id}", response_model=TransactionOut)
def read_transaction(
    transaction_id: UUID,
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
    transaction = crud_transactions.get_transaction_by_id(db, transaction_id=transaction_id, user_id=UUID(user_id))
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction
@router.put("/{transaction_id}", response_model=TransactionOut)
def update_transaction(
    transaction_id: UUID,
    transaction_in: TransactionUpdate,
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
    if transaction_in.kind is not None and transaction_in.kind not in ("income", "expense"):
        raise HTTPException(status_code=400, detail="Invalid transaction kind. Must be 'income' or 'expense'.")
    try : 
        updated_transaction = crud_transactions.update_transaction(db, transaction_id=transaction_id, user_id=UUID(user_id), transaction_in=transaction_in)
        if not updated_transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        return updated_transaction
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    transaction_id: UUID,
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
    success = crud_transactions.delete_transaction(db, transaction_id=transaction_id, user_id=UUID(user_id))
    if not success:
        raise HTTPException(status_code=404, detail="Transaction not found")
