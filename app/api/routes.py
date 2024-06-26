# Contains the routes related to API functionality.

from flask import Blueprint, jsonify
from ..models import Question, Answer, Result, InterviewParameter, Session, Applicant, Review, ReviewQuestion
from .. import db
# API RETRIEVAL
api = Blueprint('api', __name__)

@api.route('/questions', methods=['GET'])
def get_questions():
    questions = Question.query.all()
    return jsonify([{
        'id': question.id,
        'content': question.content,
        'timestamp': question.timestamp,
        'session_id': question.session_id
    } for question in questions])

@api.route('/answers', methods=['GET'])
def get_answers():
    answers = Answer.query.all()
    return jsonify([{
        'id': answer.id,
        'content': answer.content,
        'question_id': answer.question_id,
        'timestamp': answer.timestamp,
        'session_id': answer.session_id
    } for answer in answers])


@api.route('/results', methods=['GET'])
def get_scores():
    results = Result.query.all()
    return jsonify([{
        'id': result.id,
        'score_type': result.score_type,
        'score_result': result.score_result,
        'session_id': result.session_id
    } for result in results])


@api.route('/interview_parameters', methods=['GET'])
def get_interview_parameters():
    interview_parameters = InterviewParameter.query.all()
    return jsonify([{
        'id': parameter.id,
        'language': parameter.language,
        'max_questions': parameter.max_questions,
        'duration': parameter.duration,
        'role': parameter.role,
        'industry': parameter.industry,
        'interview_id': parameter.interview_id
    } for parameter in interview_parameters])


@api.route('/sessions', methods=['GET'])
def get_sessions():
    sessions = Session.query.all()
    return jsonify([{
        'id': session.id,
        'start_time': session.start_time,
        'interview_parameter_id' : session.interview_parameter_id,
        'applicant_id' : session.applicant_id,
        'questions' : [{
            'id': question.id,
            'content': question.content,
            'timestamp': question.timestamp,
            'session_id': question.session_id
        } for question in session.questions],
        'answers' : [{
            'id': answer.id,
            'content': answer.content,
            'question_id': answer.question_id,
            'timestamp': answer.timestamp,
            'session_id': answer.session_id
        } for answer in session.answers],
        'results' : [{
            'id': result.id,
            'score_type': result.score_type,
            'score_result': result.score_result,
            'session_id': result.session_id
        } for result in session.results]
    } for session in sessions])


@api.route('/applicants', methods=['GET'])
def get_applicants():
    applicants = Applicant.query.all()
    return jsonify([{
        'id': applicant.id,
        'name': applicant.name,
        'surname': applicant.surname,
        'email_address': applicant.email_address,
    } for applicant in applicants])



@api.route('/applicant_reviews', methods=['GET'])
def get_applicant_reviews():
    reviews = Review.query.all()
    all_reviews = []
    for review in reviews:
        review_data = {
            'review_id': review.id,
            'session_id': review.session_id,
            'comment': review.comment,
            'questions': []
        }
        review_questions = ReviewQuestion.query.filter_by(review_id=review.id).all()
        for question in review_questions:
            question_data = {
                'question_text': question.text,
                'rating': question.rating
            }
            review_data['questions'].append(question_data)
        all_reviews.append(review_data)
    return jsonify(all_reviews)


@api.route('/mean_ratings_per_question', methods=['GET'])
def get_mean_ratings_per_question():
    from sqlalchemy import func
    questions = ReviewQuestion.query.with_entities(ReviewQuestion.text).distinct().all()
    question_ratings = {}
    for question in questions:
        avg_rating = db.session.query(func.avg(ReviewQuestion.rating)).filter(ReviewQuestion.text == question.text).scalar()
        question_ratings[question.text] = avg_rating
    return jsonify(question_ratings)

