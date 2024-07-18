from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json


from .. import db


class InterviewParameter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    language = db.Column(db.String(256), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=True)
    duration = db.Column(db.Integer, nullable=True)
    max_questions = db.Column(db.Integer, nullable=True)
    role = db.Column(db.String, nullable=True)                                              # marketing, sales, ops
    situation = db.Column(db.Text, nullable=True)  # Allow storing JSON string for multiple situations
    industry = db.Column(db.String, nullable=True)                                          # Web3/blockchain, fintech, HRTech, MedTech, EdTech...
    position = db.Column(db.String, nullable=True)                                          # CTO, Head of Sales...
    evaluation_criteria = db.Column(db.String, nullable=True)                               # Allow to prompt the scoring 
    interview_url = db.Column(db.String, nullable=True)
    interview_id = db.Column(db.Integer, db.ForeignKey('interview.id'), nullable=False)
    sessions = db.relationship('Session', backref='interview_parameter',  cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Interview Parameter {self.id}>'
    
    def get_situations(self):
        return json.loads(self.situation) if self.situation else []