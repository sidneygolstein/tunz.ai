# This file initializes the Flask application and SQLAlchemy.


from flask import Flask, session as flask_session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from flask import Flask
from flask_mail import Mail, Message


db = SQLAlchemy()
migrate = Migrate()
mail = Mail()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    with app.app_context():
        from app import models
        from .main.routes import main as main_blueprint
        from .auth.routes import auth as auth_blueprint
        from .api.routes import api as api_blueprint
        app.register_blueprint(main_blueprint)          # we import the main blueprint and register it with the Flask application.
        app.register_blueprint(auth_blueprint, url_prefix='/auth')
        app.register_blueprint(api_blueprint, url_prefix='/api')

        # Import models
        from .models import answer, applicant, company, hr, interview_parameter, interview, question, result, session

    return app