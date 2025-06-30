from sqlalchemy.orm import Session
import logging

from app.core.config import settings
from app.core.security import get_password_hash
from app.crud.user import get_user_by_email
from app.schemas.user import UserCreate
from app.models.user import User
from app.models.task import Task
from app.models.game import Achievement, InventoryItem, Category, TaskTag

logger = logging.getLogger(__name__)

def init_db(db: Session) -> None:
    """Initialize the database with required tables and initial data."""
    try:
        # Create an initial superuser if no users exist
        user = get_user_by_email(db, email="admin@taskdonegeon.com")
        if not user:
            user_in = UserCreate(
                first_name="Admin",
                last_name="User",
                username="admin",
                email="admin@taskdonegeon.com",
                password="changeme123",  # This should be changed immediately
                birthday="1990-01-01",
                is_superuser=True,
            )
            user = User(
                first_name=user_in.first_name,
                last_name=user_in.last_name,
                username=user_in.username,
                email=user_in.email,
                birthday=user_in.birthday,
                hashed_password=get_password_hash(user_in.password),
                is_superuser=True,
            )
            db.add(user)
            db.commit()
            logger.info("Created initial superuser")
        
        # Create default categories if they don't exist
        default_categories = [
            {"name": "Daily Quests", "color": "#FF5733", "icon_name": "sun"},
            {"name": "Weekly Missions", "color": "#33FF57", "icon_name": "calendar"},
            {"name": "Epic Quests", "color": "#3357FF", "icon_name": "star"},
            {"name": "Side Quests", "color": "#FF33F5", "icon_name": "bookmark"},
        ]
        
        for cat_data in default_categories:
            category = db.query(Category).filter(Category.name == cat_data["name"]).first()
            if not category:
                category = Category(**cat_data)
                db.add(category)
                logger.info(f"Created category: {cat_data['name']}")
        
        db.commit()
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}", exc_info=True)
        raise 