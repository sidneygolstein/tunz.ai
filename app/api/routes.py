# Contains the routes related to API functionality.

from flask import Blueprint, jsonify
from ..models import Question, Answer, Result, InterviewParameter, Session, Applicant

# API RETRIEVAL
api = Blueprint('api', __name__)

@api.route('/api/questions', methods=['GET'])
def get_questions():
    questions = Question.query.all()
    return jsonify([{
        'id': question.id,
        'content': question.content,
        'timestamp': question.timestamp,
        'session_id': question.session_id
    } for question in questions])

@api.route('/api/answers', methods=['GET'])
def get_answers():
    answers = Answer.query.all()
    return jsonify([{
        'id': answer.id,
        'content': answer.content,
        'question_id': answer.question_id,
        'timestamp': answer.timestamp,
        'session_id': answer.session_id
    } for answer in answers])


@api.route('/api/results', methods=['GET'])
def get_scores():
    results = Result.query.all()
    return jsonify([{
        'id': result.id,
        'score_type': result.score_type,
        'score_result': result.score_result,
        'session_id': result.session_id
    } for result in results])


@api.route('/api/interview_parameters', methods=['GET'])
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


@api.route('/api/sessions', methods=['GET'])
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


@api.route('/api/applicants', methods=['GET'])
def get_applicants():
    applicants = Applicant.query.all()
    return jsonify([{
        'id': applicant.id,
        'name': applicant.name,
        'surname': applicant.surname,
        'email_address': applicant.email_address,
    } for applicant in applicants])

