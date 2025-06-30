from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user
from app.crud.task import (
    get_task,
    get_tasks_by_user,
    get_tasks_by_category,
    create_task,
    update_task,
    delete_task,
    get_overdue_tasks,
    get_tasks_due_today,
    get_subtasks
)
from app.models.user import User
from app.schemas.task import Task, TaskCreate, TaskUpdate, TaskWithRelations

router = APIRouter()

@router.get("", response_model=List[Task])
def read_tasks(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    include_completed: bool = False,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve tasks for the current user.
    """
    tasks = get_tasks_by_user(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        include_completed=include_completed
    )
    return tasks

@router.post("", response_model=Task)
def create_user_task(
    *,
    db: Session = Depends(get_db),
    task_in: TaskCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create new task for the current user.
    """
    task = create_task(db=db, task_in=task_in, user_id=current_user.id)
    return task

@router.get("/category/{category_id}", response_model=List[Task])
def read_tasks_by_category(
    category_id: int,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve tasks by category for the current user.
    """
    tasks = get_tasks_by_category(
        db=db,
        category_id=category_id,
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )
    return tasks

@router.get("/overdue", response_model=List[Task])
def read_overdue_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve overdue tasks for the current user.
    """
    tasks = get_overdue_tasks(db=db, user_id=current_user.id)
    return tasks

@router.get("/today", response_model=List[Task])
def read_today_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve tasks due today for the current user.
    """
    tasks = get_tasks_due_today(db=db, user_id=current_user.id)
    return tasks

@router.get("/{task_id}", response_model=TaskWithRelations)
def read_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get task by ID.
    """
    task = get_task(db=db, task_id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    if task.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not enough permissions"
        )
    return task

@router.put("/{task_id}", response_model=Task)
def update_user_task(
    *,
    db: Session = Depends(get_db),
    task_id: int,
    task_in: TaskUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update a task.
    """
    task = get_task(db=db, task_id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    if task.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not enough permissions"
        )
    task = update_task(db=db, task=task, task_in=task_in)
    return task

@router.delete("/{task_id}", response_model=Task)
def delete_user_task(
    *,
    db: Session = Depends(get_db),
    task_id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Delete a task.
    """
    task = get_task(db=db, task_id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    if task.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not enough permissions"
        )
    task = delete_task(db=db, task_id=task_id)
    return task

@router.get("/{task_id}/subtasks", response_model=List[Task])
def read_task_subtasks(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get subtasks for a task.
    """
    task = get_task(db=db, task_id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    if task.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not enough permissions"
        )
    return get_subtasks(db=db, parent_id=task_id) 