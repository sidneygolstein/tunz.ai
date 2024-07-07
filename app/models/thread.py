from app import db

class Thread(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    thread_id = db.Column(db.String(256), nullable=False)
    assistant_id = db.Column(db.String(256), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'), nullable=False)