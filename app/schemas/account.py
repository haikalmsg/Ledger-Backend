from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator

# --- Requests ---
class AccountCreate(BaseModel):
    name : str
    type : str
    currency : str = Field(..., max_length=3, min_length=3)  # ISO 4217 currency code
    opening_balance : float
    is_active : bool = True


# --- Responses ---
class AccountOut(BaseModel):
    id : UUID
    name : str
    type : str
    currency : str
    opening_balance : float
    is_active : bool
    created_at : datetime
    updated_at : datetime
