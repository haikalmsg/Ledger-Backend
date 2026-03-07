import token
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError

from app.core.database import get_db
from app.schemas.users import UserCreate, UserOut, UserUpdate, UserLogin, UserLoginResponse, PasswordUpdate
from app.core import security
from app.crud import users as crud_users



router = APIRouter(prefix="/users", tags=["users"])
bearer_scheme = HTTPBearer()

@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    existing_user = crud_users.get_user_by_email(db, user_in.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud_users.create_user(db, user_in)
@router.post("/login", response_model=UserLoginResponse)
def login_user(login_data: UserLogin, db: Session = Depends(get_db)):
    user = crud_users.get_user_by_email(db, login_data.email.lower())
    if not user or not crud_users.verify_password(login_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid email or password")
    token = security.create_access_token(data={"user_id": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}
@router.get("/me", response_model=UserOut)
def read_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    token = credentials.credentials
    user_id = security.decode_token(token).get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = crud_users.get_user(db, UUID(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
@router.put("/update-password")
def update_user_password(
    password : PasswordUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    token_decrypt = security.decode_token(token)
    if token_decrypt is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    user_id = token_decrypt.get("user_id")
    user = crud_users.get_user(db, UUID(user_id))
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not password.password:
        raise HTTPException(status_code=400, detail="New password is required")
    if crud_users.verify_password(password.password, user.password_hash):
        raise HTTPException(status_code=400, detail="New password cannot be the same as the old password")
    crud_users.update_user_password(db, UUID(user_id), password)  # Example update, replace with actual logic
    return {"status": "success", "message": "Password updated successfully"}
@router.put("/update")
def update_user(
    user_update: UserUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    token_decrypt = security.decode_token(token)
    existing_user = crud_users.get_user_by_email(db, user_update.email)
    if existing_user :
        raise HTTPException(status_code=400, detail="Email already exists")
    if token_decrypt is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    user_id = token_decrypt.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    if not crud_users.get_user(db, UUID(user_id)):
        raise HTTPException(status_code=401, detail="Invalid token")
    updated_user = crud_users.update_user(db, UUID(user_id), user_update)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"status": "success", "message": "User updated successfully", "email": updated_user.email, "full_name": updated_user.full_name}
@router.delete("/me")
def delete_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    token_decrypt = security.decode_token(token)
    if token_decrypt is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    user_id = token_decrypt.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    if not crud_users.get_user(db, UUID(user_id)):
        raise HTTPException(status_code=401, detail="Invalid token")
    success = crud_users.delete_user(db, UUID(user_id))
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"status": "success", "message": "User deleted successfully"}