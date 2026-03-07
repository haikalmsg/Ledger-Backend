from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator

# --- Requests ---

class TransactionCreate(BaseModel):
    account_id : UUID
    category_id : UUID
    kind : str
    amount: float = Field(..., gt=0)
    occurred_at: datetime
    description: str | None = None
    merchant: str | None = None

class TransactionUpdate(BaseModel):
    account_id : UUID | None = None
    category_id : UUID | None = None
    kind : str | None = None
    amount: float = Field(default=None, gt=0)
    occurred_at: datetime | None = None
    description: str | None = None
    merchant: str | None = None
class TransactionListRequest(BaseModel):
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=10, ge=1, le=100)
    search: str | None = None
    kind: str | None = None
    account_id: UUID | None = None

# --- Responses ---
class TransactionOut(BaseModel):
    id : UUID
    user_id : UUID
    account_id : UUID
    category_id : UUID
    kind : str
    amount: float
    occurred_at: datetime
    description: str | None = None
    merchant: str | None = None
    created_at : datetime
    updated_at : datetime

    model_config = {"from_attributes": True}

class TransactionListResponse(BaseModel):
    data: list[TransactionOut]
    next: bool
    previous: bool
    page: int
    limit: int
    total_pages : int
    total: int