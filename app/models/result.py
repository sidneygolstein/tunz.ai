from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from .. import db


class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    score_type = db.Column(db.String, nullable=False)
    score_result = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    feedback_type = db.Column(db.String, nullable=True)
    feedback_content = db.Column(db.String, nullable=True)
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'), nullable=False)

    def __repr__(self):
        return f'<Result {self.id}>'