from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate
from app.crud.user import add_experience, add_gold

def get_task(db: Session, task_id: int) -> Optional[Task]:
    return db.query(Task).filter(Task.id == task_id).first()

def get_tasks_by_user(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    include_completed: bool = False
) -> List[Task]:
    query = db.query(Task).filter(Task.owner_id == user_id)
    if not include_completed:
        query = query.filter(Task.is_completed == False)
    return query.offset(skip).limit(limit).all()

def get_tasks_by_category(
    db: Session,
    category_id: int,
    user_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[Task]:
    return db.query(Task).filter(
        and_(
            Task.category_id == category_id,
            Task.owner_id == user_id
        )
    ).offset(skip).limit(limit).all()

def create_task(
    db: Session,
    task_in: TaskCreate,
    user_id: int
) -> Task:
    db_task = Task(
        **task_in.model_dump(),
        owner_id=user_id
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def update_task(
    db: Session,
    task: Task,
    task_in: TaskUpdate
) -> Task:
    update_data = task_in.model_dump(exclude_unset=True)
    
    # Handle task completion
    if "is_completed" in update_data and update_data["is_completed"] and not task.is_completed:
        task.completed_at = datetime.utcnow()
        
        # Update streak if applicable
        if task.parent_id:
            parent_task = get_task(db, task.parent_id)
            if parent_task and parent_task.is_completed:
                task.streak_count = parent_task.streak_count + 1
        
        # Award experience and gold
        add_experience(db, task.owner, task.experience_reward)
        add_gold(db, task.owner, task.gold_reward)
    
    for field in update_data:
        setattr(task, field, update_data[field])
    
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

def delete_task(db: Session, task_id: int) -> Optional[Task]:
    task = db.query(Task).filter(Task.id == task_id).first()
    if task:
        db.delete(task)
        db.commit()
    return task

def get_overdue_tasks(
    db: Session,
    user_id: int
) -> List[Task]:
    now = datetime.utcnow()
    return db.query(Task).filter(
        and_(
            Task.owner_id == user_id,
            Task.due_date < now,
            Task.is_completed == False
        )
    ).all()

def get_tasks_due_today(
    db: Session,
    user_id: int
) -> List[Task]:
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    return db.query(Task).filter(
        and_(
            Task.owner_id == user_id,
            Task.due_date >= today_start,
            Task.due_date <= today_end,
            Task.is_completed == False
        )
    ).all()

def get_subtasks(
    db: Session,
    parent_id: int
) -> List[Task]:
    return db.query(Task).filter(Task.parent_id == parent_id).all() 