# This file initializes the Flask application and SQLAlchemy.


from flask import Flask, session as flask_session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config


db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        from app import routes, models
        from app.routes import main as main_blueprint
        app.register_blueprint(main_blueprint)          # we import the main blueprint and register it with the Flask application.

    return app