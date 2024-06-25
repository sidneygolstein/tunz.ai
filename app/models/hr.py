from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from .. import db


class HR(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    surname = db.Column(db.String, nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    email_address = db.Column(db.String, nullable=False)
    interviews = db.relationship('Interview', backref='hr_manager', lazy=True)

    def __repr__(self):
        return f'<Hiring Manager {self.id}>'