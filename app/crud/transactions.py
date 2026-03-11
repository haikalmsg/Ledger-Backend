from decimal import Decimal
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pwdlib import PasswordHash
from fastapi import HTTPException, status
from sqlalchemy import func


from app.models.transaction import Transaction
from app.schemas.transactions import TransactionCreate, TransactionUpdate

def get_transaction_by_id(db: Session, transaction_id: UUID, user_id: UUID) -> Transaction | None:
    return db.query(Transaction).filter(Transaction.id == transaction_id, Transaction.user_id == user_id).first()

def get_transaction_paginated(db: Session, user_id: UUID, skip: int, limit: int, search: str | None = None, kind: str | None = None, account_id: UUID | None = None) -> list[Transaction]:
    query = db.query(Transaction).filter(Transaction.user_id == user_id)
    if search:
        query = query.filter(Transaction.description.ilike(f"%{search}%"))
    if kind is not None:
        query = query.filter(Transaction.kind == kind)
    if account_id:
        query = query.filter(Transaction.account_id == account_id)
    return query.offset(skip).limit(limit).all()
def get_transaction_count(db: Session, user_id: UUID, search: str | None = None, kind : str | None = None, account_id: UUID | None = None) -> int:
    query = db.query(Transaction).filter(Transaction.user_id == user_id)
    if search:
        query = query.filter(Transaction.description.ilike(f"%{search}%"))
    if kind is not None:
        query = query.filter(Transaction.kind == kind)
    if account_id:
        query = query.filter(Transaction.account_id == account_id)
    return query.count()

def create_transaction(db: Session, transaction_in: TransactionCreate, user_id: UUID) -> Transaction:
    new_transaction = Transaction(
        amount=transaction_in.amount,
        occurred_at=transaction_in.occurred_at,
        kind=transaction_in.kind,
        description=transaction_in.description,
        account_id=transaction_in.account_id,
        category_id=transaction_in.category_id,
        merchant = transaction_in.merchant,
        user_id=user_id
    )
    try :
        db.add(new_transaction)
        db.commit()
        db.refresh(new_transaction)
        return new_transaction
    except IntegrityError as e:
        db.rollback()
        if "transactions_account_id_fkey" in str(e.orig):
            raise ValueError("Account does not exist or does not belong to the user.")
        if "transactions_category_id_fkey" in str(e.orig):
            raise ValueError("Category does not exist or does not belong to the user.")
        raise ValueError("Database integrity error.")
    except Exception:
        db.rollback()
        raise ValueError("An error occurred while creating the transaction.")

def update_transaction(db: Session, transaction_id: UUID, user_id: UUID, transaction_in: TransactionUpdate) -> Transaction | None:
    transaction = get_transaction_by_id(db, transaction_id, user_id)
    if not transaction:
        return None
    if transaction_in.amount is not None:
        transaction.amount = transaction_in.amount
    if transaction_in.occurred_at is not None:
        transaction.occurred_at = transaction_in.occurred_at
    if transaction_in.description is not None:
        transaction.description = transaction_in.description
    if transaction_in.account_id is not None:
        transaction.account_id = transaction_in.account_id
    if transaction_in.category_id is not None:
        transaction.category_id = transaction_in.category_id
    try :
        db.commit()
        db.refresh(transaction)
        return transaction
    except IntegrityError as e:
        db.rollback()
        if "transactions_account_id_fkey" in str(e.orig):
            raise ValueError("Account does not exist or does not belong to the user.")
        if "transactions_category_id_fkey" in str(e.orig):
            raise ValueError("Category does not exist or does not belong to the user.")
        raise ValueError("Database integrity error.")
    except Exception:
        db.rollback()
        raise ValueError("An error occurred while updating the transaction.")

def delete_transaction(db: Session, transaction_id: UUID, user_id: UUID) -> bool:
    transaction = get_transaction_by_id(db, transaction_id, user_id)
    if not transaction:
        return False
    db.delete(transaction)
    db.commit()
    return True

def get_net_account_transaction_ammount_filtered(db: Session, user_id: UUID, account_id: UUID) -> Decimal | None:
    try : 
        income_sum = db.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(
            Transaction.user_id == user_id,
            Transaction.account_id == account_id,
            Transaction.kind == "income"
        ).scalar()
        expense_sum = db.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(
            Transaction.user_id == user_id,
            Transaction.account_id == account_id,
            Transaction.kind == "expense"
        ).scalar()
    except Exception:
        raise ValueError("An error occurred while calculating the net amount.")
    return Decimal(income_sum - expense_sum)



