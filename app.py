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

class UpdateProfileForm(FlaskForm):
    email = StringField('Email', validators=[validators.DataRequired(), validators.Email()])
    name =  StringField('name', validators=[validators.DataRequired()])

class DeleteUserForm(FlaskForm):
    password = PasswordField('Password',validators=[validators.DataRequired()])

class UpdateUserForm(FlaskForm):
    first_name = StringField('First Name', validators=[validators.DataRequired()])
    last_name = StringField('Last Name', validators=[validators.DataRequired()])
    email = StringField('Email', validators=[validators.DataRequired(), validators.Email()])

class UpdatePasswordForm(FlaskForm):
    current_password = PasswordField('Password', validators=[validators.DataRequired()])
    new_password = PasswordField('New Password', validators=[validators.DataRequired()])
    password_confirmation = PasswordField('Confirm Password', validators=[
        validators.DataRequired(),
        validators.EqualTo('new_password', message='Passwords must match')
    ])

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

class BillForm(FlaskForm):
    month = StringField('Month', validators=[
        validators.DataRequired()
    ]) 
    year = StringField('Year', validators=[
        validators.DataRequired()
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

@app.route('/update_profile', methods=['POST'])
def update_profile():
    form = UpdateProfileForm()
    print(form.email.data)
    print(request.form.get('fname'))
    print(current_user.id)
    user_id = current_user.id
    email = form.email.data
    fname = request.form.get('fname')
    lname = request.form.get('lname')
    print(form.validate())
    query = db.sql.text("UPDATE users SET first_name=:fname, last_name=:lname, email=:email WHERE user_id=:user_id")
    result = db.session.execute(query,{"email":email, "fname":fname, "lname":lname, "user_id": user_id})
    db.session.commit()

    # print(result)
    # if result:
    #     print(result)
    #     return redirect(url_for('profile'))
    # else:
    return redirect(url_for('profile'))    
    return render_template('profile.html', user=current_user)

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

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    updateForm = UpdateUserForm()
    deleteForm = DeleteUserForm()
    cardForm = CardForm()
    updatePasswordForm = UpdatePasswordForm()
    
    query = db.sql.text("select * from card_information where user_id=:user_id")
    cards = db.session.execute(query,{'user_id':current_user.id })

    query1 = db.sql.text("select count(*) from watch_history where user_id=:user_id")
    totalwatched = db.session.execute(query1,{'user_id':current_user.id}).fetchone()._asdict()
    query2 = db.sql.text("select count(*) from likes where user_id=:user_id and status=true")
    totalliked = db.session.execute(query2,{'user_id':current_user.id}).fetchone()._asdict()
    query3 = db.sql.text("select sum(TO_TIMESTAMP(progress, 'HH24:MI:SS')::TIME) as totalwatch from watch_history where user_id=:user_id")
    totalscreen = db.session.execute(query3,{'user_id':current_user.id}).fetchone()._asdict()
    query4 = db.sql.text("select max(genre) as favgenre from contents c, content_genre cg , genre g,watch_history w, media m  where w.media_id = m.media_id and c.content_id = m.content_id and cg.content_id=c.content_id and g.genre_id=cg.genre_id  and w.user_id=:user_id")
    favgenre = db.session.execute(query4,{'user_id':current_user.id}).fetchone()._asdict()
   
    # Update Password code here
    if updatePasswordForm.validate_on_submit():
        user = query = db.sql.text("select * from users where email=:email")
        user = db.session.execute(query,{'email': current_user.email}).fetchone()._asdict()

        if verify_password(hashedpassword=user['password'],password=updatePasswordForm.current_password.data):
            query = db.sql.text("update users set password=:new_password where user_id=:user_id")
            new_password = generate_password_hash(updatePasswordForm.new_password.data)
            user = db.session.execute(query,{'user_id':current_user.id, 'new_password': new_password})
            db.session.commit()

        return render_template('profile.html',updateForm=updateForm,deleteForm=deleteForm,cardForm=cardForm,cards=cards,updatePasswordForm=updatePasswordForm,
        totalwatched=totalwatched, totalliked=totalliked, totalscreen=totalscreen['totalwatch'], favgenre=favgenre['favgenre'] )

    return render_template('profile.html',updateForm=updateForm,deleteForm=deleteForm,cardForm=cardForm,cards=cards,updatePasswordForm=updatePasswordForm,
    totalwatched=totalwatched, totalliked=totalliked, totalscreen=totalscreen['totalwatch'], favgenre=favgenre['favgenre'] )

@app.route('/update-user',methods=['POST'])
@login_required
def updateUser():    
    form = UpdateUserForm()
    if form.validate():
        query = db.sql.text("update users set first_name=:first_name,last_name=:last_name,email=:email where user_id=:user_id")
        user = db.session.execute(query,{'email': form.email.data,'first_name': form.first_name.data, 'last_name':form.last_name.data,'user_id':current_user.id})
        db.session.commit()
    return redirect(url_for('profile'))

@app.route('/add-card',methods=['POST'])
@login_required
def addCard():
    form = CardForm()

    if form.validate():
        name = form.name.data
        number = form.number.data
        cvv = form.cvv.data
        expiry = form.expiry.data

        query = db.sql.text("insert into card_information(name,card_number,expiry,cvv,user_id) values(:name, :number, :expiry, :cvv, :user_id)")
        card = db.session.execute(query,{'name':name, 'number':number, 'cvv':cvv, 'expiry':expiry, 'user_id':current_user.id })
        # Commit the transaction
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

@app.route('/olap-example')
@login_required
def olapExample():
    query = db.sql.text('''SELECT user_id, billing_date, plan, SUM(amount_paid) FROM billing_history GROUP BY ROLLUP(user_id, billing_date, plan) Having plan IS NOT NULL LIMIT 100;''')

    result = db.session.execute(query)
    items = result.fetchall()
    columns  = result.keys()

    items = [r._asdict() for r in items]

    return render_template('olap.html',items=items,columns=columns)

@app.route('/search')
@login_required
def search():
    query = db.sql.text("select * from contents where title like :title limit 100;")

    items = db.session.execute(query,{'title':'%'+request.args.get('title')+'%'}).fetchall()

    items = [r._asdict() for r in items]

    return render_template('search.html',items=items)

@app.route('/billing-history', methods=['POST'])
@login_required
def billingHistory():
    # months=[
    #      'January',
    #      'February',
    #      'March',
    #      'April',
    #      'May',
    #      'June',
    #      'July',
    #      'August',
    #      'September',
    #      'October',
    #     'November',
    #      'December'
    # ]
    billForm = BillForm()
    month = billForm.month.data
    year = billForm.year.data
    print(year)
    query5= db.sql.text("SELECT AVG(amount_paid) AS avg_price FROM billing_history WHERE EXTRACT(MONTH FROM billing_date) = :month  AND EXTRACT(YEAR FROM billing_date) = :year and user_id=:user_id")
    monthlyavgbilling = db.session.execute(query5,{'month':month,'user_id':current_user.id, 'year':year}).fetchone()._asdict()
    query6= db.sql.text("SELECT SUM(amount_paid) AS sum_price FROM billing_history WHERE EXTRACT(MONTH FROM billing_date) = :month  AND EXTRACT(YEAR FROM billing_date) = :year and user_id=:user_id")
    monthlysumbilling = db.session.execute(query6,{'month':month,'user_id':current_user.id, 'year':year}).fetchone()._asdict()
    query7= db.sql.text("SELECT COUNT(amount_paid) AS count_price FROM billing_history WHERE EXTRACT(MONTH FROM billing_date) = :month  AND EXTRACT(YEAR FROM billing_date) = :year and user_id=:user_id")
    monthlycountbilling = db.session.execute(query7,{'month':month,'user_id':current_user.id, 'year':year}).fetchone()._asdict()
    print( month)
    avg = 0
    sumtotal =0 
    count = 0
    query = db.sql.text("select * from billing_history where user_id=:user and EXTRACT(MONTH FROM billing_date) = :month AND EXTRACT(YEAR FROM billing_date) = :year")

    items = db.session.execute(query,{'user':current_user.id,'month':month,'year':year}).fetchall()
    
    items = [r._asdict() for r in items]

    if(monthlyavgbilling['avg_price']):
        avg = round(monthlyavgbilling['avg_price'],2)
    
    if(monthlysumbilling['sum_price']):
        sumtotal = round(monthlysumbilling['sum_price'],2)
    
    if(monthlycountbilling['count_price']):
        count = round(monthlycountbilling['count_price'],2)

    print(monthlycountbilling['count_price'])
    return render_template('billingHistory.html',items=items, avg=avg, sum=sumtotal, count=count)

@app.route('/content-metadata')
@login_required
def contentMetadata():

    query = db.sql.text("With contentlanguagesgenres as ( select contents.*, string_agg(distinct languages.language, ', ') as languages, string_agg(distinct genre.genre, ', ') as genres from contents join media on contents.content_id = media.content_id join content_language on contents.content_id = content_language.content_id join languages on content_language.language_id = languages.language_id join content_genre on content_genre.content_id = contents.content_id join genre on genre.genre_id = content_genre.genre_id where contents.content_id = :content_id group by contents.content_id ) select contentlanguagesgenres.*, media.* from contentlanguagesgenres join media on media.content_id = contentlanguagesgenres.content_id")

    items = db.session.execute(query,{'content_id':request.args.get('contentId')}).fetchall()

    result_dicts = [r._asdict() for r in items]

    return jsonify(result_dicts)

if __name__ == '__main__':
    app.run(debug=True)
