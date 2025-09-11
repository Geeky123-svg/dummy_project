from flask import Blueprint,render_template,jsonify
main_bp = Blueprint('main_bp',__name__)
@main_bp.route('/')
def home():
    return render_template('home.html')
@main_bp.route('/help')
def help():
    return render_template('help.html')
@main_bp.route('/data')
def data():
    return jsonify({'message': 'Data retrieved!'})