from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator

# --- Requests ---
class CategoryCreate(BaseModel):
    name: str = Field(..., max_length=100)
    is_active: bool = True

class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=100)
    is_active: bool | None = None

class CategoryListRequest(BaseModel):
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=10, ge=1, le=100)

# --- Responses ---
class CategoryOut(BaseModel):
    id: UUID
    name: str
    user_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class CategoryListResponse(BaseModel):
    data: list[CategoryOut]
    next: bool
    previous: bool
    page: int
    limit: int
    total: int