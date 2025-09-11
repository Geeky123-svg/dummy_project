from flask import Blueprint
user_bp=Blueprint('user_bp',__name__)

@user_bp.route('/user')
def home():
    return "Welcome user.."