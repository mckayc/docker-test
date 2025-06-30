import os
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///task_donegeon.db')
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

@app.before_request
def check_first_run():
    if request.endpoint != 'first_run' and User.query.count() == 0:
        return redirect(url_for('first_run'))

@app.route('/first-run', methods=['GET', 'POST'])
def first_run():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        username = request.form['username']
        birthday = request.form['birthday']
        password = request.form['password']
        password2 = request.form['password2']
        if password != password2:
            flash('Passwords do not match!')
            return render_template('first_run.html')
        user = User(
            first_name=first_name,
            last_name=last_name,
            username=username,
            birthday=birthday,
            password_hash=generate_password_hash(password),
            is_admin=True
        )
        db.session.add(user)
        db.session.commit()
        flash('Admin user created!')
        return redirect(url_for('hello_world'))
    return render_template('first_run.html')

@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 