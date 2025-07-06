import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from pathlib import Path
from models import db, User
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

# Setup base directories
BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / 'templates'
STATIC_DIR = BASE_DIR / 'static'

# Ensure static directory exists
STATIC_DIR.mkdir(exist_ok=True)

app = Flask(__name__, static_folder=str(STATIC_DIR))
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Create tables
with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.static_folder, 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/health')
def health_check():
    return {'status': 'healthy'}, 200

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('first_run.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        birthday = datetime.strptime(request.form.get('birthday'), '%Y-%m-%d')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return render_template('signup.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return render_template('signup.html')
        
        user = User(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            birthday=birthday
        )
        
        db.session.add(user)
        db.session.commit()
        
        flash('Welcome to the guild, brave adventurer!')
        login_user(user)
        return redirect(url_for('dashboard'))
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Welcome back, brave adventurer!')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    flash('Farewell, brave adventurer! Return soon to continue your quest.')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True) 