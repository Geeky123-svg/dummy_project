from flask import Flask
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager,login_manager
from models.models import db,User

bcrypt=Bcrypt()

def create_admin():
    from models.models import User
    admin = User.query.filter_by(username="admin").first()
    if not admin:
        hashed_password = bcrypt.generate_password_hash("mec").decode('utf-8')
        admin = User(username="admin", password=hashed_password, full_name="Quiz Master", is_admin=True)
        db.session.add(admin)
        db.session.commit()
        
def create_app():
    app=Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///new.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'supersecret'
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager = LoginManager()
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    login_manager.init_app(app)
    login_manager.session_protection = "strong"
    from routes.routes import main_bp
    from routes.admin import admin_bp
    from routes.user import user_bp
    from routes.auth import auth_bp
    app.register_blueprint(admin_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    with app.app_context():
        db.create_all()
        create_admin()
    return app