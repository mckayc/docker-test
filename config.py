import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base directory of the application
BASE_DIR = Path(__file__).resolve().parent

class Config:
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev_key_change_in_production')
    
    # SQLAlchemy
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', f'sqlite:///{BASE_DIR}/task_donegeon.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security
    PASSWORD_SALT = os.getenv('PASSWORD_SALT', 'change_in_production')
    
    # Development vs Production
    DEBUG = os.getenv('FLASK_DEBUG', '0') == '1' 