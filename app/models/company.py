from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from .. import db


class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    contact_name = db.Column(db.String, nullable=True)
    phone_number = db.Column(db.String, nullable=True)
    hr_managers = db.relationship('HR', backref='company', lazy=True,  cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Company {self.id}>'
