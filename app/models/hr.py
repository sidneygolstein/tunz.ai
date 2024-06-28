from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from app import bcrypt
from flask_login import UserMixin
from itsdangerous import URLSafeTimedSerializer as Serializer
from flask import current_app
from flask_jwt_extended import create_access_token
from .. import db


class HR(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    name = db.Column(db.String, nullable=False, default = "")
    surname = db.Column(db.String, nullable=False, default = "")
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), default = 0)
    email = db.Column(db.String, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    confirmed = db.Column(db.Boolean, default=False)
    interviews = db.relationship('Interview', backref='hr_manager', cascade="all, delete-orphan")
    admin = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Hiring Manager {self.id}>'
    
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'hr_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            hr_id = s.loads(token)['hr_id']
        except Exception as e:
            return None
        return HR.query.get(hr_id)
    
    def get_access_token(self):
        return create_access_token(identity=self.id)