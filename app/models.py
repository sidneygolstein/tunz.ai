# This file defines the database models.

# The backref argument in SQLAlchemy's relationship() function is used to create a bidirectional relationship between two models,
# which automatically adds a reverse relationship attribute to the related model. When you use backref, you define a single relationship
# that can be used from either side of the relationship. The back_populates argument is also used for bidirectional relationships but
# requires explicit relationships on both sides of the relationship.

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from . import db

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    contact_name = db.Column(db.String, nullable=False)
    phone_number = db.Column(db.String, nullable=False)
    hr_managers = db.relationship('HR', backref='company', lazy=True)


class HR(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    surname = db.Column(db.String, nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    email_address = db.Column(db.String, nullable=False)
    interviews = db.relationship('Interview', backref='hr_manager', lazy=True)


class Applicant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    surname = db.Column(db.String, nullable=False)
    email_address = db.Column(db.String, nullable=False)
    sessions = db.relationship('Session', backref='applicant', lazy=True)


class Interview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.String, nullable=False, default = "")
    name = db.Column(db.String, nullable=False, default = "")
    rules = db.Column(db.String, nullable=False, default = "")                                      # E.g., maximum number of applicants = 200
    hr_id = db.Column(db.Integer, db.ForeignKey('hr.id'), nullable=False, default = 1)
    interview_parameters = db.relationship('InterviewParameter', backref='interview', lazy=True)


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


class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    applicant_id = db.Column(db.Integer, db.ForeignKey('applicant.id'),  nullable=True)
    interview_parameter_id = db.Column(db.Integer, db.ForeignKey('interview_parameter.id'),  nullable=True)
    questions = db.relationship('Question', backref='session', lazy=True)
    answers = db.relationship('Answer', backref='session', lazy=True)
    results = db.relationship('Result', backref='session', lazy=True)


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'), nullable=False)
    answer = db.relationship('Answer', uselist=False, backref='question')


class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)


class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    score_type = db.Column(db.String, nullable=False)
    score_result = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    feedback_type = db.Column(db.String, nullable=True)
    feedback_content = db.Column(db.String, nullable=True)
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'), nullable=False)