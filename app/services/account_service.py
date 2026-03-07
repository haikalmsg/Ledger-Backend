from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pwdlib import PasswordHash
from fastapi import HTTPException, status
from sqlalchemy import func
from decimal import Decimal

from app.crud import transactions as crud_transactions
from app.crud import account as crud_accounts

def get_account_balance(db: Session, user_id: UUID, account_id: UUID) -> Decimal | None:
    account = crud_accounts.get_account(db, account_id=account_id, user_id=user_id)
    if not account:
        raise ValueError("Account does not exist or does not belong to the user.")
    return crud_transactions.get_net_account_transaction_ammount_filtered(db, user_id=user_id, account_id=account_id) + account.opening_balance