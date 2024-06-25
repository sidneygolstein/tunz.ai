from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from .. import db

class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    applicant_id = db.Column(db.Integer, db.ForeignKey('applicant.id'),  nullable=True)
    interview_parameter_id = db.Column(db.Integer, db.ForeignKey('interview_parameter.id'),  nullable=True)
    questions = db.relationship('Question', backref='session', lazy=True)
    answers = db.relationship('Answer', backref='session', lazy=True)
    results = db.relationship('Result', backref='session', lazy=True)

    def __repr__(self):
        return f'<Session {self.id}>'