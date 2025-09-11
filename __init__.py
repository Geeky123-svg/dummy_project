from flask import Flask
def create_app():
    app=Flask(__name__)
    from routes.routes import main_bp
    from routes.admin import admin_bp
    from routes.user import user_bp
    app.register_blueprint(admin_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(main_bp)
    return app