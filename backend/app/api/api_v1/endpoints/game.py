from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user
from app.crud.game import (
    get_user_achievements,
    create_achievement,
    check_achievement_requirements,
    get_user_inventory,
    create_inventory_item,
    update_inventory_item,
    get_categories,
    create_category,
    get_task_tags,
    create_task_tag,
    delete_task_tag
)
from app.models.user import User
from app.schemas.game import (
    Achievement,
    AchievementCreate,
    InventoryItem,
    InventoryItemCreate,
    InventoryItemUpdate,
    Category,
    CategoryCreate,
    TaskTag,
    TaskTagCreate
)

router = APIRouter()

# Achievement endpoints
@router.get("/achievements", response_model=List[Achievement])
def read_achievements(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve achievements for the current user.
    """
    achievements = get_user_achievements(db=db, user_id=current_user.id)
    return achievements

@router.post("/achievements", response_model=Achievement)
def create_user_achievement(
    *,
    db: Session = Depends(get_db),
    achievement_in: AchievementCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create new achievement for the current user.
    First checks if the user meets the requirements.
    """
    if not check_achievement_requirements(db, current_user, achievement_in.requirements):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Requirements not met for this achievement"
        )
    achievement = create_achievement(
        db=db,
        achievement_in=achievement_in,
        user_id=current_user.id
    )
    return achievement

# Inventory endpoints
@router.get("/inventory", response_model=List[InventoryItem])
def read_inventory(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve inventory items for the current user.
    """
    items = get_user_inventory(db=db, user_id=current_user.id)
    return items

@router.post("/inventory", response_model=InventoryItem)
def create_user_inventory_item(
    *,
    db: Session = Depends(get_db),
    item_in: InventoryItemCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create new inventory item for the current user.
    """
    if current_user.level < item_in.level_requirement:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User level {current_user.level} is too low for this item (requires level {item_in.level_requirement})"
        )
    item = create_inventory_item(
        db=db,
        item_in=item_in,
        user_id=current_user.id
    )
    return item

@router.put("/inventory/{item_id}", response_model=InventoryItem)
def update_user_inventory_item(
    *,
    db: Session = Depends(get_db),
    item_id: int,
    item_in: InventoryItemUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update an inventory item.
    """
    item = db.query(InventoryItem).filter(InventoryItem.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    if item.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not enough permissions"
        )
    item = update_inventory_item(db=db, item=item, item_in=item_in)
    return item

# Category endpoints
@router.get("/categories", response_model=List[Category])
def read_categories(
    db: Session = Depends(get_db),
) -> Any:
    """
    Retrieve all categories.
    """
    categories = get_categories(db=db)
    return categories

@router.post("/categories", response_model=Category)
def create_new_category(
    *,
    db: Session = Depends(get_db),
    category_in: CategoryCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create new category.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not enough permissions"
        )
    category = create_category(db=db, category_in=category_in)
    return category

# Tag endpoints
@router.get("/tasks/{task_id}/tags", response_model=List[TaskTag])
def read_task_tags_endpoint(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve tags for a task.
    """
    task = db.query(Task).filter(Task.id == task_id).first()
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
    return get_task_tags(db=db, task_id=task_id)

@router.post("/tasks/{task_id}/tags", response_model=TaskTag)
def create_task_tag_endpoint(
    *,
    db: Session = Depends(get_db),
    task_id: int,
    tag_in: TaskTagCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create new tag for a task.
    """
    task = db.query(Task).filter(Task.id == task_id).first()
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
    return create_task_tag(db=db, tag_in=tag_in, task_id=task_id)

@router.delete("/tasks/tags/{tag_id}", response_model=TaskTag)
def delete_task_tag_endpoint(
    *,
    db: Session = Depends(get_db),
    tag_id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Delete a task tag.
    """
    tag = db.query(TaskTag).filter(TaskTag.id == tag_id).first()
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )
    task = db.query(Task).filter(Task.id == tag.task_id).first()
    if task.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not enough permissions"
        )
    return delete_task_tag(db=db, tag_id=tag_id) 