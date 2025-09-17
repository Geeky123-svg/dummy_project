from flask import Blueprint,render_template,request,redirect,url_for
from flask_login import login_user
from models.models import User,db
from __init__ import bcrypt
from datetime import datetime
from utils.email_validator import is_valid_email

auth_bp=Blueprint('auth_bp',__name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):  # Check user exists AND password is correct FIRST
            login_user(user)
            if user.is_admin: # THEN check if admin
                print("Redirecting to admin portal..")
                return redirect(url_for('admin_bp.admin_portal'))
            else:
                print("Redirecting to user portal...")
                return redirect(url_for('user_bp.user_portal'))
        else:
            return render_template("login.html", flag="danger", message="Invalid Credentials! Try again!")

    return render_template("login.html")

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        message = request.args.get('message')
        return render_template("signup.html", message=message)

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        full_name = request.form.get('full_name')
        qualification = request.form.get('qualification')
        dob = request.form.get('dob')  # Expecting dd/mm/yyyy

        if not is_valid_email(username):
            return render_template(
                "signup.html",
                message="Invalid email address!",
                username=username,
                full_name=full_name,
                qualification=qualification,
                dob=dob
            )
        
        if password != confirm_password:
            return render_template(
                "signup.html",
                message="Password does not match!",
                username=username,
                full_name=full_name,
                qualification=qualification,
                dob=dob
            )

        user = User.query.filter_by(username=username).first()
        if user:
            return render_template(
                "signup.html",
                message="Username taken!",
                username=username,
                full_name=full_name,
                qualification=qualification,
                dob=dob
            )
        if dob:
            try:
                dob = datetime.strptime(dob, "%Y-%m-%d").strftime("%d/%m/%Y")  # Convert format
                dob = datetime.strptime(dob, "%d/%m/%Y").date()  # Convert to date object
            except ValueError:
                return redirect(url_for('auth_bp.signup', message="Invalid date format! Use DD/MM/YYYY"))


        hashpass = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, password=hashpass, full_name=full_name, qualification=qualification, dob=dob)
        print("New User added!\nUser_id:",username,"\nfullname:",full_name,"\ndob: ",dob)
        db.session.add(new_user)
        db.session.commit()

        return render_template("login.html",flag="success", message="User created")
