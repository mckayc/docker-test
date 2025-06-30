from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, Text, Enum, JSON
from sqlalchemy.orm import relationship
import enum
from datetime import datetime

from app.db.session import Base

class ItemType(str, enum.Enum):
    WEAPON = "weapon"
    ARMOR = "armor"
    POTION = "potion"
    SCROLL = "scroll"
    QUEST_ITEM = "quest_item"
    COSMETIC = "cosmetic"

class Achievement(Base):
    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    icon_url = Column(String(200))
    unlocked_at = Column(DateTime, default=datetime.utcnow)
    
    # Achievement properties
    experience_reward = Column(Integer, default=50)
    gold_reward = Column(Integer, default=25)
    
    # Requirements stored as JSON
    requirements = Column(JSON)
    
    # Relationships
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="achievements")

class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    icon_url = Column(String(200))
    acquired_at = Column(DateTime, default=datetime.utcnow)
    
    # Item properties
    item_type = Column(Enum(ItemType))
    rarity = Column(Integer, default=1)  # 1-5 scale
    level_requirement = Column(Integer, default=1)
    
    # Stats and effects stored as JSON
    stats = Column(JSON)
    effects = Column(JSON)
    
    # Inventory management
    quantity = Column(Integer, default=1)
    is_equipped = Column(Boolean, default=False)
    
    # Relationships
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="inventory")

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    description = Column(Text)
    color = Column(String(7))  # Hex color code
    icon_name = Column(String(50))
    
    # Relationships
    tasks = relationship("Task", back_populates="category")

class TaskTag(Base):
    __tablename__ = "task_tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(30), nullable=False)
    
    # Relationships
    task_id = Column(Integer, ForeignKey("tasks.id"))
    task = relationship("Task", back_populates="tags") 