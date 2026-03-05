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
from app.schemas.account import AccountCreate, AccountOut
from app.crud import account as crud_account
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
    return crud_account.create_account(db, account_in, user_id=UUID(user_id))