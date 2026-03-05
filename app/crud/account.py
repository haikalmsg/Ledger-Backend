from uuid import UUID
from sqlalchemy.orm import Session
from pwdlib import PasswordHash

from app.models.account import Account
from app.schemas.account import AccountCreate

def get_account_paginated(db: Session, user_id: UUID, skip: int, limit: int, search: str | None = None, status: bool | None = None) -> list[Account]:
    query = db.query(Account).filter(Account.user_id == user_id)
    if search:
        query = query.filter(Account.name.ilike(f"%{search}%"))
    if status is not None:
        query = query.filter(Account.is_active == status)
    return query.offset(skip).limit(limit).all()

def get_account_total (db: Session, user_id: UUID, search: str | None = None, status: bool | None = None) -> int:
    query = db.query(Account).filter(Account.user_id == user_id)
    if search:
        query = query.filter(Account.name.ilike(f"%{search}%"))
    if status is not None:
        query = query.filter(Account.is_active == status)
    return query.count()
def get_account(db: Session, account_id: UUID, user_id: UUID) -> Account | None:
    return db.query(Account).filter(Account.id == account_id, Account.user_id == user_id).first()
def create_account(db: Session, account_in: AccountCreate, user_id: UUID) -> Account:
    new_account = Account(
        name=account_in.name,
        opening_balance=account_in.opening_balance,
        currency = account_in.currency,
        is_active=account_in.is_active,
        type=account_in.type,
        user_id=user_id
    )
    db.add(new_account)
    db.commit()
    db.refresh(new_account)
    return new_account