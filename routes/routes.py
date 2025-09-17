from flask import Blueprint,render_template,jsonify
from flask_login import logout_user

main_bp = Blueprint('main_bp',__name__)

@main_bp.route('/')
def home():
    return render_template("home.html")

@main_bp.route('/logout',methods=['GET', 'POST'])
def logout():
    logout_user()
    return render_template('home.html')