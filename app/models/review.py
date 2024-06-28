from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from .. import db


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'), nullable=False)
    comment = db.Column(db.Text, nullable=True)
    
    questions = db.relationship('ReviewQuestion', backref='review', cascade="all, delete-orphan")