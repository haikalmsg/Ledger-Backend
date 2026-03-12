from datetime import datetime
from uuid import UUID
from decimal import Decimal

from pydantic import BaseModel, EmailStr, Field, field_validator

# --- Requests ---
class AccountCreate(BaseModel):
    name : str
    type : str
    currency : str = Field(..., max_length=3, min_length=3)  # ISO 4217 currency code
    opening_balance : float
    is_active : bool = True
class AccountUpdate(BaseModel):
    name : str | None = Field(default=None)
    type : str | None = Field(default=None)
    currency : str | None = Field(default=None, max_length=3, min_length=3)  # ISO 4217 currency code
    opening_balance : float | None = None
    is_active : bool | None = None
class AccountListRequest(BaseModel):
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=10, ge=1, le=100)
    search: str | None = None
    kind: str | None = None


# --- Responses ---
class AccountOut(BaseModel):
    id : UUID
    name : str
    type : str
    currency : str
    opening_balance : Decimal
    is_active : bool
    created_at : datetime
    updated_at : datetime
    model_config = {"from_attributes": True}
class AccountBalanceResponse(BaseModel):
    account_id: UUID
    balance: float

class AccountWithBalancePagination(AccountOut):
    current_balance : Decimal
class AccountListResponse(BaseModel):
    data: list[AccountWithBalancePagination]
    next: bool
    previous: bool
    page: int
    limit: int
    total_pages : int
    total: int