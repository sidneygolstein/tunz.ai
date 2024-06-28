from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from .. import db

class Applicant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    surname = db.Column(db.String, nullable=False)
    email_address = db.Column(db.String, nullable=False)
    sessions = db.relationship('Session', backref='applicant',  cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Applicant {self.id}>'