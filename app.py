import os
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators, DateField
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from dotenv import load_dotenv
from helpers.collectionHelpers import group_by_index, group_by_key, verify_password, generate_password_hash

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('APP_KEY')
# Configure the PostgreSQL database URI using environment variables
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{os.getenv('DB_USERNAME')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_DATABASE')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[validators.DataRequired()])
    last_name = StringField('Last Name', validators=[validators.DataRequired()])
    email = StringField('Email', validators=[validators.DataRequired(), validators.Email()])
    password = PasswordField('Password', validators=[validators.DataRequired()])
    password_confirmation = PasswordField('Confirm Password', validators=[
        validators.DataRequired(),
        validators.EqualTo('password', message='Passwords must match')
    ])

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[validators.DataRequired(), validators.Email()])
    password = PasswordField('Password', validators=[validators.DataRequired()])

class DeleteUserForm(FlaskForm):
    password = PasswordField('Password',validators=[validators.DataRequired()])

class UpdateUserForm(FlaskForm):
    first_name = StringField('First Name', validators=[validators.DataRequired()])
    last_name = StringField('Last Name', validators=[validators.DataRequired()])
    email = StringField('Email', validators=[validators.DataRequired(), validators.Email()])

class UpdatePasswordForm(FlaskForm):
    current_password = StringField('First Name', validators=[validators.DataRequired()])
    last_name = StringField('Last Name', validators=[validators.DataRequired()])
    email = StringField('Email', validators=[validators.DataRequired(), validators.Email()])

class CardForm(FlaskForm):
    number = StringField('Card Number', validators=[
        validators.DataRequired(),
        validators.Length(min=16, max=16, message='Card number must be 16 digits')
    ])
    cvv = StringField('CVV', validators=[
        validators.DataRequired(),
        validators.Length(min=3, max=4, message='CVV must be 3 or 4 digits')
    ])
    expiry = DateField('Expiry Date', format='%Y-%m-%d', validators=[
        validators.DataRequired()
    ])
    name = StringField('Cardholder Name', validators=[
        validators.DataRequired(),
        validators.Length(min=2, message='Cardholder name must have at least 2 characters')
    ])

class User(UserMixin):
    def __init__(self, user_data):
        self.id = user_data['user_id']
        self.email = user_data['email']
        self.first_name = user_data['first_name']
        self.last_name = user_data['last_name']
    
@app.route('/')
def index():
    return render_template('index.html')

@login_manager.user_loader
def load_user(user_id):
    query = db.sql.text("select * from users where user_id=:user_id")
    user_data = db.session.execute(query,{'user_id': user_id}).fetchone()

    if user_data:
        user = User(user_data._asdict())
    else:
        user = User({
                'user_id': '',
                'first_name': '',
                'last_name': '',
                'email': '',
            })
    print(user)
    
    return user

@app.route('/login')
def login():    
    form = LoginForm()
    return render_template('login.html',form=form)

@app.route('/login', methods=['POST'])
def loginUser():
    form = LoginForm()

    if form.validate():
        email = form.email.data
        password = form.password.data

        query = db.sql.text("select * from users where email=:email")
        user = db.session.execute(query,{'email': email}).fetchone()

        if user:
            user = user._asdict()
            if verify_password(hashedpassword=user['password'],password=password):
                user_obj = User(user)
                login_user(user_obj)
                return redirect(url_for('dashboard'))
            flash('Invalid credentials provided')
            return redirect(url_for('login'))
        else:
            flash('Invalid credentials provided')
            return redirect(url_for('login'))
        
    return render_template('login.html',form=form)

@app.route('/register')
def register():
    form = RegistrationForm()

    return render_template('register.html',form=form)

@app.route('/register', methods=['POST'])
def registerUser():
    form = RegistrationForm()

    if form.validate():
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data
        password = form.password.data
        query = db.sql.text("select * from users where email=:email")
        user = db.session.execute(query,{'email': email}).fetchone()

        if not user:
            query = db.sql.text("insert into users(first_name,last_name,email,password) values(:first_name, :last_name, :email, :password)")
            password = generate_password_hash(password)
            user = db.session.execute(query,{'first_name':first_name, 'last_name':last_name, 'email':email, 'password':password })
            # Commit the transaction
            db.session.commit()

            query = db.sql.text("select * from users where email=:email")
            user = db.session.execute(query,{'email': email}).fetchone()._asdict()

            user_obj = User({
                'user_id': user['user_id'],
                'first_name': user['first_name'],
                'last_name': user['last_name'],
                'email': user['email'],
            })

            login_user(user_obj)

            return redirect(url_for('dashboard'))

    return render_template('register.html',form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def profile():
    updateForm = UpdateUserForm()
    deleteForm = DeleteUserForm()
    cardForm = CardForm()
    return render_template('profile.html',updateForm=updateForm,deleteForm=deleteForm,cardForm=cardForm)

@app.route('/update-user',methods=['POST'])
@login_required
def updateUser():    
    form = UpdateUserForm()
    print(form.validate())
    if form.validate():
        query = db.sql.text("update users set first_name=:first_name,last_name=:last_name,email=:email where user_id=:user_id")
        user = db.session.execute(query,{'email': form.email.data,'first_name': form.first_name.data, 'last_name':form.last_name.data,'user_id':current_user.id})
        db.session.commit()
    return redirect(url_for('profile'))


@app.route('/delete-user',methods=['POST'])
@login_required
def deleteUser():
    form = DeleteUserForm()
    if form.validate():
        query = db.sql.text("select * from users where email=:email")
        user = db.session.execute(query,{'email': current_user.email}).fetchone()

        if user:
            user = user._asdict()
            if verify_password(hashedpassword=user['password'],password=form.data['password']):
                logout_user()
                query = db.sql.text("delete from users where email=:email")
                db.session.execute(query,{'email': user['email']})
                db.session.commit()
                # return redirect(url_for('index'))
                return redirect(url_for('index'))
    return redirect(url_for('profile'))

@app.route('/dashboard')
@login_required
def dashboard():
    query = db.sql.text('''select * from ( select a.*, row_number() over (partition by a.genre_id order by a.genre_id,a.added_on desc) as rn from ( select distinct on (contents.content_id) contents.*, genre.genre, genre.genre_id from contents join content_genre on content_genre.content_id = contents.content_id join genre on genre.genre_id = content_genre.genre_id ) as a order by genre_id ) as b where rn <= 20''')

    items = db.session.execute(query).fetchall()
    
    items = [r._asdict() for r in items]
        
    items = group_by_key(items,'genre')
    
    return render_template('dashboard.html',items=items)

@app.route('/movies')
@login_required
def movies():
    query = db.sql.text('''select * from ( select a.*, row_number() over (partition by a.genre_id order by a.genre_id,a.added_on desc) as rn from ( select distinct on (contents.content_id) contents.*, genre.genre, genre.genre_id from contents join content_genre on content_genre.content_id = contents.content_id join genre on genre.genre_id = content_genre.genre_id where contents.content_type = 1) as a order by genre_id ) as b where rn <= 20''')

    items = db.session.execute(query).fetchall()
    
    items = [r._asdict() for r in items]
        
    items = group_by_key(items,'genre')
    
    return render_template('dashboard.html',items=items)

@app.route('/tvshows')
@login_required
def tvShows():
    query = db.sql.text('''select * from ( select a.*, row_number() over (partition by a.genre_id order by a.genre_id,a.added_on desc) as rn from ( select distinct on (contents.content_id) contents.*, genre.genre, genre.genre_id from contents join content_genre on content_genre.content_id = contents.content_id join genre on genre.genre_id = content_genre.genre_id where contents.content_type = 2) as a order by genre_id ) as b where rn <= 20''')

    items = db.session.execute(query).fetchall()
    
    items = [r._asdict() for r in items]
        
    items = group_by_key(items,'genre')
    
    return render_template('dashboard.html',items=items)



@app.route('/content-metadata')
@login_required
def contentMetadata():

    query = db.sql.text("With contentlanguagesgenres as ( select contents.*, string_agg(distinct languages.language, ', ') as languages, string_agg(distinct genre.genre, ', ') as genres from contents join media on contents.content_id = media.content_id join content_language on contents.content_id = content_language.content_id join languages on content_language.language_id = languages.language_id join content_genre on content_genre.content_id = contents.content_id join genre on genre.genre_id = content_genre.genre_id where contents.content_id = :content_id group by contents.content_id ) select contentlanguagesgenres.*, media.* from contentlanguagesgenres join media on media.content_id = contentlanguagesgenres.content_id")

    items = db.session.execute(query,{'content_id':request.args.get('contentId')}).fetchall()

    result_dicts = [r._asdict() for r in items]

    return jsonify(result_dicts)

if __name__ == '__main__':
    app.run(debug=True)
