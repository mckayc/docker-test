import os
from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import logging
import re
from datetime import datetime

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
if not app.config['SECRET_KEY']:
    logger.warning('No SECRET_KEY set! Using an insecure default key.')
    app.config['SECRET_KEY'] = 'dev'

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///instance/task_donegeon.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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

@app.route('/health')
def health():
    try:
        # Test database connection
        db.session.execute('SELECT 1')
        return jsonify({"status": "healthy", "database": "connected"}), 200
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({"status": "unhealthy", "database": "disconnected"}), 500

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
            db.create_all()
            logger.info('Database tables created or verified.')
            if User.query.count() == 0:
                logger.info('No users found. First run wizard will be shown.')
            else:
                logger.info('Users found. Skipping first run wizard.')
        except Exception as e:
            logger.error(f'Error initializing database: {str(e)}')

    port = int(os.environ.get('PORT', 5000))
    logger.info(f'Starting Task Donegeon on http://0.0.0.0:{port}')
    app.run(host='0.0.0.0', port=port) 