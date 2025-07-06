import os
from flask import Flask, render_template
from pathlib import Path

# Setup base directories
BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / 'templates'

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_dev_key_please_change')

@app.route('/')
def welcome():
    return render_template('welcome.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 