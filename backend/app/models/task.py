from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
import enum
from datetime import datetime

from app.db.session import Base

class TaskPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class TaskDifficulty(str, enum.Enum):
    TRIVIAL = "trivial"
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EPIC = "epic"

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    due_date = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    is_completed = Column(Boolean, default=False)
    
    # Task properties
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM)
    difficulty = Column(Enum(TaskDifficulty), default=TaskDifficulty.MEDIUM)
    
    # Game mechanics
    experience_reward = Column(Integer, default=10)
    gold_reward = Column(Integer, default=5)
    streak_count = Column(Integer, default=0)
    
    # Relationships
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="tasks")
    subtasks = relationship("Task", backref="parent_task")
    parent_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)
    
    # Tags/Categories
    tags = relationship("TaskTag", back_populates="task")
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    category = relationship("Category", back_populates="tasks") 