# This file initializes the Flask application and SQLAlchemy.


from flask import Flask, session as flask_session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_mail import Mail, Message


db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()
mail = Mail()
bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)

    with app.app_context():
        from app import models
        from .main.routes import main as main_blueprint
        from .auth.routes import auth as auth_blueprint
        from .api.routes import api as api_blueprint
        from .admin.routes import admin as admin_blueprint
        app.register_blueprint(main_blueprint)          # we import the main blueprint and register it with the Flask application.
        app.register_blueprint(auth_blueprint, url_prefix='/auth')
        app.register_blueprint(api_blueprint, url_prefix='/api')
        app.register_blueprint(admin_blueprint, url_prefix='/admin')


        # Import models
        from .models import answer, applicant, company, hr, interview_parameter, interview, question, result, session, review, review_question, admin

    return app

