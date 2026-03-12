from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pwdlib import PasswordHash
from fastapi import HTTPException, status

from app.models.account import Account
from app.schemas.account import AccountCreate, AccountUpdate 
from app.services import account_service

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
    try : 
        db.add(new_account)
        db.commit()
        db.refresh(new_account)
        return new_account
    except IntegrityError as e:
        db.rollback()
        if "uq_accounts_user_name" in str(e.orig):
            raise ValueError("Account name already exists for this user.")
        raise ValueError("Database integrity error.")
    except Exception:
        db.rollback()
        raise ValueError("An error occurred while creating the account.")
    
def update_account(db: Session, account_id : UUID, user_id: UUID, account_in: AccountUpdate) -> Account | None:
    account = get_account(db, account_id, user_id)
    if not account:
        return None
    if account_in.name is not None:
        account.name = account_in.name
    if account_in.opening_balance is not None:
        account.opening_balance = account_in.opening_balance
    if account_in.currency is not None:
        account.currency = account_in.currency
    if account_in.is_active is not None:
        account.is_active = account_in.is_active
    if account_in.type is not None:
        account.type = account_in.type
    db.commit()
    db.refresh(account)
    return account

def delete_account(db: Session, account_id: UUID, user_id: UUID) -> bool:
    account = get_account(db, account_id, user_id)
    if not account:
        return False
    db.delete(account)
    db.commit()
    return True
