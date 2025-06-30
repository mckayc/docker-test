from typing import Optional, List
from pydantic import BaseModel, constr
from datetime import datetime
from app.models.task import TaskPriority, TaskDifficulty

# Shared properties
class TaskBase(BaseModel):
    title: constr(min_length=1, max_length=200)
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    difficulty: TaskDifficulty = TaskDifficulty.MEDIUM
    experience_reward: int = 10
    gold_reward: int = 5
    parent_id: Optional[int] = None
    category_id: Optional[int] = None

# Properties to receive via API on creation
class TaskCreate(TaskBase):
    pass

# Properties to receive via API on update
class TaskUpdate(BaseModel):
    title: Optional[constr(min_length=1, max_length=200)] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: Optional[TaskPriority] = None
    difficulty: Optional[TaskDifficulty] = None
    is_completed: Optional[bool] = None

# Properties to return via API
class Task(TaskBase):
    id: int
    created_at: datetime
    completed_at: Optional[datetime] = None
    is_completed: bool
    streak_count: int
    owner_id: int
    
    class Config:
        from_attributes = True

# Properties to return via API with relationships
class TaskWithRelations(Task):
    subtasks: List['TaskWithRelations'] = []
    tags: List[str] = []

TaskWithRelations.model_rebuild()  # Required for self-referencing models 