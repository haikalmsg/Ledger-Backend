from uuid import UUID
from sqlalchemy.orm import Session
from pwdlib import PasswordHash


from app.models.users import User
from app.schemas.users import PasswordUpdate, UserCreate, UserUpdate

pwd_hash = PasswordHash.recommended()
def get_user(db: Session, user_id: UUID) -> User | None:
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user_in: UserCreate) -> User:
    new_user = User(
        email=user_in.email.lower(),
        password_hash=pwd_hash.hash(user_in.password),  # In production, hash the password!
        full_name=user_in.full_name
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def update_user(db: Session, user_id: UUID, user_in: UserUpdate) -> User | None:
    user = get_user(db, user_id)
    if not user:
        return None
    if user_in.email is not None:
        user.email = user_in.email.lower()
    if user_in.full_name is not None:
        user.full_name = user_in.full_name
    db.commit()
    db.refresh(user)
    return user

def update_user_password(db: Session, user_id: UUID, new_password: PasswordUpdate) -> User | None:
    user = get_user(db, user_id)
    if not user:
        return None
    user.password_hash = pwd_hash.hash(new_password.password)
    db.commit()
    db.refresh(user)
    return user

def delete_user_by_email(db: Session, email: str) -> bool:
    user = get_user_by_email(db, email.lower())
    if not user:
        return False
    db.delete(user)
    db.commit()
    return True
def delete_user(db: Session, user_id: UUID) -> bool:
    user = get_user(db, user_id)
    if not user:
        return False
    db.delete(user)
    db.commit()
    return True
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_hash.verify(plain_password, hashed_password)
