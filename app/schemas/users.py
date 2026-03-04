from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator


# --- Requests ---
class UserCreate(BaseModel):
    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str):
        if not v:
            raise ValueError("Password is required")
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(c.isalpha() for c in v):
            raise ValueError("Password must contain at least one letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one number")
        return v
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)  # At least 8 chars, 1 letter, 1 number
    full_name: str | None = Field(default=None, max_length=120)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    full_name: str | None = Field(default=None, max_length=120)
    email : EmailStr | None = None
class PasswordUpdate(BaseModel):
    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str):
        if not v:
            raise ValueError("Password is required")
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(c.isalpha() for c in v):
            raise ValueError("Password must contain at least one letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one number")
        return v
    password: str = Field(min_length=8, max_length=128)  # At least 8 chars, 1 letter, 1 number
# --- Responses ---
class UserOut(BaseModel):
    id: UUID
    email: EmailStr
    full_name: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
class UserLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
