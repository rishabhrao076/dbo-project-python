import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Configure the PostgreSQL database URI using environment variables
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{os.getenv('DB_USERNAME')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_DATABASE')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

@app.route('/')
def index():
    # Data to be passed to the template
    name = "Flask User"
    # Render the template and pass data to it
    return render_template('index.html')

@app.route('/login')
def login():    
    # Render the template and pass data to it
    return render_template('login.html')

@app.route('/register')
def register():
    # Data to be passed to the template
    name = "Flask User"
    # Render the template and pass data to it
    return render_template('index.html', name=name)

@app.route('/dashboard')
def dashboard():
    # Data to be passed to the template
    name = "Flask User"
    # Render the template and pass data to it
    return render_template('index.html', name=name)

if __name__ == '__main__':
    app.run(debug=True)
