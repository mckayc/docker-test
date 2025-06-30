from typing import Optional, List, Dict, Any
from pydantic import BaseModel, constr
from datetime import datetime
from app.models.game import ItemType

# Achievement schemas
class AchievementBase(BaseModel):
    name: constr(min_length=1, max_length=100)
    description: Optional[str] = None
    icon_url: Optional[str] = None
    experience_reward: int = 50
    gold_reward: int = 25
    requirements: Dict[str, Any]

class AchievementCreate(AchievementBase):
    pass

class Achievement(AchievementBase):
    id: int
    unlocked_at: datetime
    user_id: int
    
    class Config:
        from_attributes = True

# Inventory item schemas
class InventoryItemBase(BaseModel):
    name: constr(min_length=1, max_length=100)
    description: Optional[str] = None
    icon_url: Optional[str] = None
    item_type: ItemType
    rarity: int
    level_requirement: int
    stats: Dict[str, Any]
    effects: Dict[str, Any]
    quantity: int = 1
    is_equipped: bool = False

class InventoryItemCreate(InventoryItemBase):
    pass

class InventoryItemUpdate(BaseModel):
    quantity: Optional[int] = None
    is_equipped: Optional[bool] = None

class InventoryItem(InventoryItemBase):
    id: int
    acquired_at: datetime
    owner_id: int
    
    class Config:
        from_attributes = True

# Category schemas
class CategoryBase(BaseModel):
    name: constr(min_length=1, max_length=50)
    description: Optional[str] = None
    color: Optional[str] = None
    icon_name: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int
    
    class Config:
        from_attributes = True

# Tag schemas
class TaskTagBase(BaseModel):
    name: constr(min_length=1, max_length=30)

class TaskTagCreate(TaskTagBase):
    pass

class TaskTag(TaskTagBase):
    id: int
    task_id: int
    
    class Config:
        from_attributes = True 