from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
import re

app = Flask(__name__)
app.secret_key = 'harshitha'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def __init__(self, first_name, last_name, email, username, password):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.username = username
        self.password = password

def password_check(password):
    errors = []
    if len(password) < 8:
        errors.append("Password should be at least 8 characters long.")
    if not re.search("[a-z]", password):
        errors.append("Password must contain a lowercase letter.")
    if not re.search("[A-Z]", password):
        errors.append("Password must contain an uppercase letter.")
    if not password[-1].isdigit():
        errors.append("Password must end with a number.")
    return errors

@app.route('/')
def index():
    return redirect(url_for('sign_up'))

@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Check if the passwords matches
        if password != confirm_password:
            flash("Passwords do not match!")
            return render_template('sign_up.html', first_name=first_name, last_name=last_name, email=email, username=username)

        # Check the password strength
        errors = password_check(password)
        if errors:
            for error in errors:
                flash(error)
            return render_template('sign_up.html', first_name=first_name, last_name=last_name, email=email, username=username)

        # Check if the username or email already exists
        existing_user_by_username = User.query.filter_by(username=username).first()
        existing_user_by_email = User.query.filter_by(email=email).first()
        
        if existing_user_by_username:
            flash("Username already exists. Please choose a different username.")
            return render_template('sign_up.html', first_name=first_name, last_name=last_name, email=email, username=username)

        if existing_user_by_email:
            flash("Email already registered. Please use a different email.")
            return render_template('sign_up.html', first_name=first_name, last_name=last_name, email=email, username=username)

        # If everything is good, create a new user
        new_user = User(first_name, last_name, email, username, password)
        db.session.add(new_user)
        db.session.commit()
        return render_template('thankyou.html')

    return render_template('sign_up.html')

@app.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username, password=password).first()
        
        if user:
            session['user_id'] = user.id  # To store the user login session and access across different pages
            return redirect(url_for('secret_page'))
        else:
            flash("Invalid username or password.")
            return redirect(url_for('sign_in'))
    
    return render_template('sign_in.html')

@app.route('/secret_page')
def secret_page():
    if 'user_id' not in session:
        flash("You need to sign in first.")
        return redirect(url_for('sign_in'))
    
    user = User.query.get(session['user_id'])
    return render_template('secretPage.html', user=user)

if __name__ == '__main__':
   with app.app_context():
        db.create_all()
   app.run(debug=True)
