from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from .. import db


class ReviewQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    review_id = db.Column(db.Integer, db.ForeignKey('review.id'), nullable=False)