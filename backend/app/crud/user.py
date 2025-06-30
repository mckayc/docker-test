from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()

def get_users(
    db: Session,
    skip: int = 0,
    limit: int = 100
) -> List[User]:
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, user_in: UserCreate) -> User:
    db_user = User(
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        username=user_in.username,
        email=user_in.email,
        birthday=user_in.birthday,
        hashed_password=get_password_hash(user_in.password),
        is_active=user_in.is_active,
        is_superuser=user_in.is_superuser,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(
    db: Session,
    db_user: User,
    user_in: UserUpdate
) -> User:
    user_data = jsonable_encoder(db_user)
    update_data = user_in.model_dump(exclude_unset=True)
    
    if update_data.get("password"):
        hashed_password = get_password_hash(update_data["password"])
        del update_data["password"]
        update_data["hashed_password"] = hashed_password
    
    for field in user_data:
        if field in update_data:
            setattr(db_user, field, update_data[field])
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int) -> Optional[User]:
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
    return user

def authenticate_user(
    db: Session,
    username: str,
    password: str
) -> Optional[User]:
    user = get_user_by_username(db, username=username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

# Game mechanics
def add_experience(
    db: Session,
    user: User,
    amount: int
) -> User:
    user.experience_points += amount
    
    # Level up logic (simple example)
    level_threshold = user.level * 100  # Each level requires level * 100 XP
    while user.experience_points >= level_threshold:
        user.level += 1
        user.experience_points -= level_threshold
        level_threshold = user.level * 100
    
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def add_gold(
    db: Session,
    user: User,
    amount: int
) -> User:
    user.gold += amount
    db.add(user)
    db.commit()
    db.refresh(user)
    return user 