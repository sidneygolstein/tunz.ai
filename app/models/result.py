from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON


from .. import db


class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    score_type = db.Column(db.String, nullable=True)
    score_result = db.Column(db.Integer, nullable=True)
    timestamp = db.Column(db.DateTime, nullable = True, default=datetime.utcnow)
    feedback_type = db.Column(db.String, nullable=True)
    feedback_content = db.Column(db.String, nullable=True)
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'), nullable=False)
    criteria_scores = db.Column(JSON, nullable=True, default=dict)


    def __repr__(self):
        return f'<Result {self.id}>'
    

    def set_criteria_score(self, criteria, score):
        """Set the score for a specific criteria."""
        if not self.criteria_scores:
            self.criteria_scores = {}
        self.criteria_scores[criteria] = score

    def get_criteria_score(self, criteria):
        """Get the score for a specific criteria."""
        return self.criteria_scores.get(criteria, None)

    def get_all_criteria_scores(self):
        """Get all criteria scores."""
        return self.criteria_scores

    def remove_criteria_score(self, criteria):
        """Remove the score for a specific criteria."""
        if criteria in self.criteria_scores:
            del self.criteria_scores[criteria]