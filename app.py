import os
from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import logging
import re
from datetime import datetime
import shutil
from pathlib import Path
import json
from logging.handlers import RotatingFileHandler
import psutil
import time
from functools import wraps
from collections import defaultdict
import threading
import sys
from werkzeug.exceptions import HTTPException

# Setup base directories
BASE_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = BASE_DIR / 'instance'
CONFIG_DIR = BASE_DIR / 'config'
UPLOADS_DIR = BASE_DIR / 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}

# Ensure directories exist
INSTANCE_DIR.mkdir(exist_ok=True)
CONFIG_DIR.mkdir(exist_ok=True)
UPLOADS_DIR.mkdir(exist_ok=True)

# Setup logging with rotation
def setup_logging():
    log_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(pathname)s:%(lineno)d] - %(message)s'
    )
    
    # File handler with rotation (10MB max size, keep 5 backup files)
    file_handler = RotatingFileHandler(
        CONFIG_DIR / 'app.log',
        maxBytes=10*1024*1024,
        backupCount=5
    )
    file_handler.setFormatter(log_format)
    
    # Also log to console with more detailed format
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_format)
    
    # Setup audit log for file operations
    audit_handler = RotatingFileHandler(
        CONFIG_DIR / 'audit.log',
        maxBytes=10*1024*1024,
        backupCount=5
    )
    audit_handler.setFormatter(log_format)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Setup audit logger
    audit_logger = logging.getLogger('audit')
    audit_logger.setLevel(logging.INFO)
    audit_logger.addHandler(audit_handler)
    
    return root_logger.getChild('app'), audit_logger

logger, audit_logger = setup_logging()

# Load environment variables
env_file = CONFIG_DIR / '.env'
if not env_file.exists() and os.path.exists(BASE_DIR / '.env'):
    logger.info("Copying .env to config volume")
    shutil.copy(BASE_DIR / '.env', env_file)

# Load .env file if it exists, but don't override existing environment variables
if env_file.exists():
    load_dotenv(env_file, override=False)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def log_file_operation(operation, filename, user_id=None):
    """Log file operations to audit log"""
    audit_logger.info(json.dumps({
        'operation': operation,
        'filename': filename,
        'user_id': user_id,
        'timestamp': datetime.now().isoformat()
    }))

app = Flask(__name__)

# Configuration
app.config.update(
    SECRET_KEY=os.getenv('SECRET_KEY', 'default_dev_key_please_change'),
    SQLALCHEMY_DATABASE_URI=os.getenv('DATABASE_URL', f'sqlite:///{INSTANCE_DIR}/task_donegeon.db'),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    UPLOAD_FOLDER=str(UPLOADS_DIR),
    MAX_CONTENT_LENGTH=16 * 1024 * 1024  # 16MB max file size
)

if app.config['SECRET_KEY'] == 'default_dev_key_please_change':
    logger.warning('Using default SECRET_KEY! Please set a secure key in production.')

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    birthday = db.Column(db.Date, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

def validate_password(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r"\d", password):
        return False, "Password must contain at least one number"
    return True, ""

def validate_username(username):
    if not re.match(r"^[a-zA-Z0-9_-]{3,50}$", username):
        return False, "Username must be 3-50 characters and contain only letters, numbers, underscores, and hyphens"
    return True, ""

@app.before_request
def check_first_run():
    if request.endpoint not in ['first_run', 'health'] and User.query.count() == 0:
        return redirect(url_for('first_run'))

@app.before_request
def log_request_info():
    """Log detailed request information"""
    logger.info(f"""
Request Details:
  - Endpoint: {request.endpoint}
  - Method: {request.method}
  - URL: {request.url}
  - Headers: {dict(request.headers)}
  - Args: {dict(request.args)}
  - Form Data: {dict(request.form) if request.form else 'No form data'}
  - Files: {[f.filename for f in request.files.values()] if request.files else 'No files'}
  - Remote Addr: {request.remote_addr}
""".strip())

@app.after_request
def log_response_info(response):
    """Log response information"""
    logger.info(f"""
Response Details:
  - Status: {response.status_code}
  - Headers: {dict(response.headers)}
  - Content Type: {response.content_type}
  - Content Length: {response.content_length}
""".strip())
    return response

@app.errorhandler(Exception)
def handle_exception(e):
    """Log all unhandled exceptions"""
    logger.error(f"""
Exception Details:
  - Type: {type(e).__name__}
  - Message: {str(e)}
  - URL: {request.url}
  - Method: {request.method}
  - Remote Addr: {request.remote_addr}
  - User Agent: {request.user_agent}
""".strip(), exc_info=True)
    
    # Return appropriate error response
    if isinstance(e, HTTPException):
        return e
    return "An unexpected error occurred", 500

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """Serve uploaded files."""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Metrics tracking
request_counts = defaultdict(int)
request_times = defaultdict(list)
error_counts = defaultdict(int)
last_requests = []
MAX_REQUEST_HISTORY = 100

def track_request(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        try:
            response = f(*args, **kwargs)
            request_counts[request.endpoint] += 1
            duration = time.time() - start_time
            request_times[request.endpoint].append(duration)
            # Keep only last 100 request times
            if len(request_times[request.endpoint]) > 100:
                request_times[request.endpoint].pop(0)
            
            # Track last requests
            last_requests.append({
                'endpoint': request.endpoint,
                'method': request.method,
                'status': response.status_code if hasattr(response, 'status_code') else 'Unknown',
                'time': datetime.now().isoformat(),
                'duration': duration
            })
            if len(last_requests) > MAX_REQUEST_HISTORY:
                last_requests.pop(0)
            
            return response
        except Exception as e:
            error_counts[request.endpoint] += 1
            raise
    return decorated_function

# Apply tracking to all routes
def init_request_tracking(app):
    for endpoint, view_func in app.view_functions.items():
        app.view_functions[endpoint] = track_request(view_func)

@app.route('/metrics')
def metrics():
    """Enhanced metrics endpoint for monitoring"""
    try:
        # System metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Application metrics
        total_users = User.query.count()
        
        # Calculate request statistics
        request_stats = {}
        for endpoint, times in request_times.items():
            if times:
                avg_time = sum(times) / len(times)
                max_time = max(times)
                min_time = min(times)
            else:
                avg_time = max_time = min_time = 0
                
            request_stats[endpoint] = {
                'count': request_counts[endpoint],
                'errors': error_counts[endpoint],
                'avg_response_time': avg_time,
                'max_response_time': max_time,
                'min_response_time': min_time
            }
        
        # Volume statistics
        volume_stats = {
            'uploads': {
                'total_files': len(list(UPLOADS_DIR.glob('*'))),
                'total_size': sum(f.stat().st_size for f in UPLOADS_DIR.glob('*') if f.is_file()),
            },
            'data': {
                'size': sum(f.stat().st_size for f in INSTANCE_DIR.glob('*') if f.is_file()),
            }
        }
        
        metrics_data = {
            'timestamp': datetime.now().isoformat(),
            'system': {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available': memory.available,
                'disk_percent': disk.percent,
                'disk_free': disk.free,
            },
            'application': {
                'total_users': total_users,
                'uptime': time.time() - app.start_time,
                'request_stats': request_stats,
                'volume_stats': volume_stats,
                'last_requests': last_requests[-10:],  # Last 10 requests
            }
        }
        
        return jsonify(metrics_data)
    except Exception as e:
        logger.error(f"Error collecting metrics: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error collecting metrics'
        }), 500

@app.route('/health')
def health():
    """Enhanced health check including system status"""
    try:
        # Test database connection
        db.session.execute('SELECT 1')
        
        # Check volume access and space
        volumes_status = {}
        for name, path in [
            ('instance', INSTANCE_DIR),
            ('config', CONFIG_DIR),
            ('uploads', UPLOADS_DIR)
        ]:
            try:
                disk = psutil.disk_usage(str(path))
                volumes_status[name] = {
                    'accessible': os.access(path, os.W_OK),
                    'free_space': disk.free,
                    'free_percent': 100 - disk.percent
                }
            except Exception as e:
                volumes_status[name] = {
                    'error': str(e)
                }
        
        # Check system resources
        memory = psutil.virtual_memory()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'database': 'connected',
            'volumes': volumes_status,
            'system': {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_available_percent': memory.available * 100 / memory.total,
                'memory_available_bytes': memory.available
            }
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }), 500

# Store application start time
app.start_time = time.time()

# Initialize request tracking
init_request_tracking(app)

@app.route('/first-run', methods=['GET', 'POST'])
def first_run():
    if User.query.count() > 0:
        flash('Admin user already exists!')
        return redirect(url_for('hello_world'))

    if request.method == 'POST':
        try:
            first_name = request.form['first_name'].strip()
            last_name = request.form['last_name'].strip()
            username = request.form['username'].strip()
            birthday = request.form['birthday']
            password = request.form['password']
            password2 = request.form['password2']

            # Validate inputs
            if not all([first_name, last_name, username, birthday, password, password2]):
                flash('All fields are required!')
                return render_template('first_run.html')

            # Validate username
            username_valid, username_msg = validate_username(username)
            if not username_valid:
                flash(username_msg)
                return render_template('first_run.html')

            # Check if username exists
            if User.query.filter_by(username=username).first():
                flash('Username already exists!')
                return render_template('first_run.html')

            # Validate password
            if password != password2:
                flash('Passwords do not match!')
                return render_template('first_run.html')

            password_valid, password_msg = validate_password(password)
            if not password_valid:
                flash(password_msg)
                return render_template('first_run.html')

            # Validate birthday
            try:
                birthday_date = datetime.strptime(birthday, '%Y-%m-%d').date()
                if birthday_date > datetime.now().date():
                    flash('Birthday cannot be in the future!')
                    return render_template('first_run.html')
            except ValueError:
                flash('Invalid birthday format!')
                return render_template('first_run.html')

            user = User(
                first_name=first_name,
                last_name=last_name,
                username=username,
                birthday=birthday_date,
                password_hash=generate_password_hash(password),
                is_admin=True
            )
            db.session.add(user)
            db.session.commit()
            flash('Admin user created successfully!')
            logger.info(f'Admin user {username} created successfully')
            return redirect(url_for('hello_world'))

        except Exception as e:
            db.session.rollback()
            logger.error(f'Error creating admin user: {str(e)}')
            flash('An error occurred while creating the admin user. Please try again.')
            return render_template('first_run.html')

    return render_template('first_run.html')

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file uploads"""
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = Path(app.config['UPLOAD_FOLDER']) / filename
        
        # Check if file exists and append number if it does
        counter = 1
        while file_path.exists():
            name, ext = os.path.splitext(filename)
            filename = f"{name}_{counter}{ext}"
            file_path = Path(app.config['UPLOAD_FOLDER']) / filename
            counter += 1
        
        try:
            file.save(file_path)
            log_file_operation('upload', filename)
            flash('File uploaded successfully')
            return jsonify({
                'status': 'success',
                'filename': filename,
                'url': url_for('uploaded_file', filename=filename)
            })
        except Exception as e:
            logger.error(f"Error uploading file: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': 'Error uploading file'
            }), 500
    
    flash('Invalid file type')
    return redirect(request.url)

@app.route('/files')
def list_files():
    """List uploaded files"""
    files = []
    for file in UPLOADS_DIR.iterdir():
        if file.is_file():
            files.append({
                'name': file.name,
                'size': file.stat().st_size,
                'modified': datetime.fromtimestamp(file.stat().st_mtime).isoformat(),
                'url': url_for('uploaded_file', filename=file.name)
            })
    return jsonify(files)

@app.route('/uploads')
def upload_page():
    """Show the upload page"""
    return render_template('upload.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

if __name__ == '__main__':
    with app.app_context():
        try:
            # Log system information
            logger.info(f"""
System Information:
  - Python Version: {sys.version}
  - Platform: {sys.platform}
  - Working Directory: {os.getcwd()}
  - Base Directory: {BASE_DIR}
  - Environment: {app.env}
  - Debug Mode: {app.debug}
""".strip())

            # Log configuration
            logger.info(f"""
Application Configuration:
  - Secret Key Set: {'Yes' if app.config['SECRET_KEY'] != 'default_dev_key_please_change' else 'No (using default)'}
  - Database URL: {app.config['SQLALCHEMY_DATABASE_URI']}
  - Upload Folder: {app.config['UPLOAD_FOLDER']}
  - Max Content Length: {app.config['MAX_CONTENT_LENGTH']} bytes
""".strip())

            # Log directory status
            for dir_name, dir_path in [
                ('Instance', INSTANCE_DIR),
                ('Config', CONFIG_DIR),
                ('Uploads', UPLOADS_DIR)
            ]:
                logger.info(f"""
{dir_name} Directory Status:
  - Path: {dir_path}
  - Exists: {dir_path.exists()}
  - Writable: {os.access(dir_path, os.W_OK)}
  - Owner: {os.stat(dir_path).st_uid}
  - Permissions: {oct(os.stat(dir_path).st_mode)[-3:]}
""".strip())

            # Test database connection and log status
            db.create_all()
            logger.info('Database tables created or verified successfully')
            
            user_count = User.query.count()
            logger.info(f'Database Status: {user_count} users found')
            if user_count == 0:
                logger.info('No users found - First run wizard will be shown')
            else:
                logger.info('Users found - First run wizard will be skipped')
                
        except Exception as e:
            logger.error('Failed to initialize application', exc_info=True)
            raise

    port = int(os.environ.get('PORT', 5000))
    logger.info(f'Starting Task Donegeon on http://0.0.0.0:{port}')
    app.run(host='0.0.0.0', port=port) 