import os
from flask import Flask, render_template, request, redirect, url_for, flash
from pathlib import Path

# Setup base directories
BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / 'templates'

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_dev_key_please_change')

@app.route('/')
def welcome():
    return render_template('welcome.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Get form data
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        birthday = request.form.get('birthday')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Basic validation
        if not all([first_name, last_name, birthday, username, email, password, confirm_password]):
            flash('All fields are required!')
            return render_template('signup.html')

        if password != confirm_password:
            flash('Passwords do not match!')
            return render_template('signup.html')

        # Here you would typically save the user data
        # For now, just redirect to welcome page with a success message
        flash('Welcome to the realm, brave adventurer!')
        return redirect(url_for('welcome'))

    return render_template('signup.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 