from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pwdlib import PasswordHash
from fastapi import HTTPException, status
from sqlalchemy import func
from decimal import Decimal

from app.crud import transactions as crud_transactions
from app.crud import account as crud_accounts
from app.crud import users as crud_users
from app.schemas.account import AccountListResponse, AccountWithBalancePagination, AccountListRequest
from math import ceil

def get_account_balance(db: Session, user_id: UUID, account_id: UUID) -> Decimal | None:
    account = crud_accounts.get_account(db, account_id=account_id, user_id=user_id)
    if not account:
        raise ValueError("Account does not exist or does not belong to the user.")
    return crud_transactions.get_net_account_transaction_ammount_filtered(db, user_id=user_id, account_id=account_id) + account.opening_balance

def get_accounts_with_balance(
    db: Session,
    user_id: UUID,
    AccountListRequest : AccountListRequest
) -> AccountListResponse:
    user = crud_users.get_user(db, user_id = user_id)
    if user is None:
        return None 
    accounts = crud_accounts.get_account_paginated(db, user_id, AccountListRequest.skip, AccountListRequest.limit, AccountListRequest.search, AccountListRequest.status)
    total = crud_accounts.get_account_total(db, user_id, AccountListRequest.search, AccountListRequest.status)


    page = (AccountListRequest.skip // AccountListRequest.limit) + 1
    total_pages = ceil(total / AccountListRequest.limit) if total > 0 else 1

    enriched = [
        AccountWithBalancePagination(
            **account.__dict__,
            current_balance=get_account_balance(db, user_id, account.id)
        )
        for account in accounts
    ]

    return AccountListResponse(
        data=enriched,
        next=AccountListRequest.skip + AccountListRequest.limit < total,
        previous=AccountListRequest.skip > 0,
        page=page,
        limit=AccountListRequest.limit,
        total_pages=total_pages,
        total=total
    )