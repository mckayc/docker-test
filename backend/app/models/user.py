from sqlalchemy import Boolean, Column, Integer, String, Date
from sqlalchemy.orm import relationship

from app.db.session import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    birthday = Column(Date, nullable=False)
    hashed_password = Column(String(128), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    # Game-related fields
    experience_points = Column(Integer, default=0)
    level = Column(Integer, default=1)
    gold = Column(Integer, default=0)
    
    # Relationships
    tasks = relationship("Task", back_populates="owner")
    achievements = relationship("Achievement", back_populates="user")
    inventory = relationship("InventoryItem", back_populates="owner") 