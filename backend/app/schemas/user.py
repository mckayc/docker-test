from typing import Optional, List
from pydantic import BaseModel, EmailStr, constr
from datetime import date

# Shared properties
class UserBase(BaseModel):
    first_name: str
    last_name: str
    username: constr(min_length=3, max_length=50)
    email: EmailStr
    birthday: date
    is_active: bool = True
    is_superuser: bool = False
    experience_points: int = 0
    level: int = 1
    gold: int = 0

# Properties to receive via API on creation
class UserCreate(UserBase):
    password: constr(min_length=8)

# Properties to receive via API on update
class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[constr(min_length=8)] = None

# Properties to return via API
class User(UserBase):
    id: int
    
    class Config:
        from_attributes = True

# Properties to return via API for the current user
class UserInDB(User):
    hashed_password: str 