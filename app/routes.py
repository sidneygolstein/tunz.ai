from flask import render_template, request, redirect, url_for, jsonify, session as flask_session, current_app
from . import db
from .models import Session, Question, Answer
from .openai_utils import create_openai_thread, get_openai_thread_response
from flask import Blueprint

main = Blueprint('main', __name__)

@main.before_request
def create_or_load_session():
    if 'session_id' not in flask_session:
        new_session = Session()
        db.session.add(new_session)
        db.session.commit()
        flask_session['session_id'] = new_session.id
        flask_session['thread_id'] = None
        flask_session['assistant_id'] = None

@main.route('/', methods=['GET'])
def chat():
    current_session_id = flask_session['session_id']
    questions = Question.query.filter_by(session_id=current_session_id).all()
    answers = Answer.query.filter_by(session_id=current_session_id).all()
    max_questions = current_app.config.get('MAX_QUESTIONS')
    return render_template('chat.html', questions=questions, answers=answers, max_questions=max_questions)

@main.route('/start', methods=['POST'])
def start_chat():
    current_session_id = flask_session['session_id']

    # Create a new thread and get the first assistant response
    thread_id, assistant_id, assistant_response = create_openai_thread()
    flask_session['thread_id'] = thread_id
    flask_session['assistant_id'] = assistant_id

    # Save the assistant's question to the database
    question = Question(content=assistant_response, session_id=current_session_id)
    db.session.add(question)
    db.session.commit()

    return redirect(url_for('main.chat'))

@main.route('/chat', methods=['POST'])
def continue_chat():
    user_input = request.form['answer']
    question_id = request.form['question_id']
    current_session_id = flask_session['session_id']
    thread_id = flask_session.get('thread_id')
    assistant_id = flask_session.get('assistant_id')
    if not thread_id:
        return redirect(url_for('main.chat'))

    # Save user's answer to the database
    answer = Answer(content=user_input, question_id=question_id, session_id=current_session_id)
    db.session.add(answer)
    db.session.commit()

    # Check if the maximum number of questions has been reached
    max_questions = current_app.config.get('MAX_QUESTIONS')
    num_questions = Question.query.filter_by(session_id=current_session_id).count()

    if num_questions >= max_questions:
        return redirect(url_for('main.result'))

    # Get the assistant's next response
    assistant_response = get_openai_thread_response(thread_id, assistant_id, user_input)

    # Save the assistant's question to the database
    question = Question(content=assistant_response, session_id=current_session_id)
    db.session.add(question)
    db.session.commit()

    return redirect(url_for('main.chat'))

@main.route('/result', methods=['GET'])
def result():
    current_session_id = flask_session['session_id']
    answers = Answer.query.filter_by(session_id=current_session_id).all()
    score = calculate_score(answers)  # Implement this function based on your grading logic
    return render_template('result.html', score=score)

@main.route('/restart', methods=['POST'])
def restart():
    flask_session.pop('session_id', None)  # Remove the session ID from the Flask session
    flask_session.pop('thread_id', None)  # Remove the thread ID from the Flask session
    return redirect(url_for('main.chat'))

def calculate_score(answers):
    return len(answers) * 10  # Example logic: 10 points per answer

@main.route('/api/questions', methods=['GET'])
def get_questions():
    questions = Question.query.all()
    return jsonify([{
        'id': question.id,
        'content': question.content,
        'timestamp': question.timestamp,
        'session_id': question.session_id
    } for question in questions])

@main.route('/api/answers', methods=['GET'])
def get_answers():
    answers = Answer.query.all()
    return jsonify([{
        'id': answer.id,
        'content': answer.content,
        'question_id': answer.question_id,
        'timestamp': answer.timestamp,
        'session_id': answer.session_id
    } for answer in answers])
