import os
import flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY')

app.config['SECRET_KEY'] = 'any-secret-key-you-choose'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)


# CREATE TABLE IN DB
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))


# Line below only required once, when creating DB.
# db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = db.session.query(User).filter_by(email=email).first()
        if user:
            error = 'Account for this email already exists'
            return render_template('register.html', error=error)
        else:
            hashed_password = generate_password_hash(password=request.form.get('password'),
                                                     method='pbkdf2:sha256', salt_length=8)
            new_user = User(name=request.form.get('name'),
                            email=request.form.get('email'),
                            password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully')
            return redirect(url_for('secrets', user_name=new_user.name))
    return render_template("register.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = db.session.query(User).filter_by(email=email).first()
        if user:
            if check_password_hash(pwhash=user.password, password=password):
                login_user(user=user, remember=True)
                flash('Logged in successfully')
                return redirect(url_for('secrets', user_name=user.name))
            else:
                error = 'Invalid password'
        else:
            error = 'Invalid email'
    return render_template("login.html", error=error)


@app.route('/secrets/<user_name>')
@login_required
def secrets(user_name):
    return render_template("secrets.html", user_name=user_name)


@app.route('/logout')
@login_required
def logout():
    pass


@app.route('/download/<path:filename>', methods=['GET'])
@login_required
def download(filename):
    return send_from_directory(directory='static/files/',
                               filename=filename)


if __name__ == "__main__":
    app.run(debug=True)

