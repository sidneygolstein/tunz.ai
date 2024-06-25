from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from .. import db


class InterviewParameter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    language = db.Column(db.String(256), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=True)
    duration = db.Column(db.Integer, nullable=True)
    max_questions = db.Column(db.Integer, nullable=False)
    role = db.Column(db.String, nullable=True)
    role_description = db.Column(db.String, nullable=True)
    industry = db.Column(db.String, nullable=True)
    evaluation_criteria = db.Column(db.String, nullable=True)
    interview_url = db.Column(db.String, nullable=True)
    interview_id = db.Column(db.Integer, db.ForeignKey('interview.id'), nullable=False)
    sessions = db.relationship('Session', backref='interview_parameter', lazy=True)

    def __repr__(self):
        return f'<Interview Parameter {self.id}>'