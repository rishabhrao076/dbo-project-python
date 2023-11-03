import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from helpers.collectionHelpers import group_by_index, group_by_key

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

@app.route('/login', methods=['POST'])
def loginUser():
    username = request.form['email']
    password = request.form['password']
    
    print(username,password)



@app.route('/register')
def register():
    # Render the template and pass data to it
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    query = db.sql.text('''select * from ( select a.*, row_number() over (partition by a.genre_id order by a.genre_id,a.added_on desc) as rn from ( select distinct on (contents.content_id) contents.*, genre.genre, genre.genre_id from contents join content_genre on content_genre.content_id = contents.content_id join genre on genre.genre_id = content_genre.genre_id ) as a order by genre_id ) as b where rn <= 20''')

    items = db.session.execute(query).fetchall()
    
    items = [r._asdict() for r in items]
        
    items = group_by_key(items,'genre')
    
    return render_template('dashboard.html',items=items)


@app.route('/content-metadata')
def contentMetadata():

    query = db.sql.text("With contentlanguagesgenres as ( select contents.*, string_agg(distinct languages.language, ', ') as languages, string_agg(distinct genre.genre, ', ') as genres from contents join media on contents.content_id = media.content_id join content_language on contents.content_id = content_language.content_id join languages on content_language.language_id = languages.language_id join content_genre on content_genre.content_id = contents.content_id join genre on genre.genre_id = content_genre.genre_id where contents.content_id = :content_id group by contents.content_id ) select contentlanguagesgenres.*, media.* from contentlanguagesgenres join media on media.content_id = contentlanguagesgenres.content_id")

    items = db.session.execute(query,{'content_id':request.args.get('contentId')}).fetchall()

    result_dicts = [r._asdict() for r in items]

    return jsonify(result_dicts)

if __name__ == '__main__':
    app.run(debug=True)
