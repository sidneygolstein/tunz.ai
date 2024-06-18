from flask import render_template, request, redirect, url_for, jsonify, session, current_app
from . import db, mail
from .models import Interview, InterviewParameter, Session, Question, Answer, Result, HR, Applicant, Company  
from .openai_utils import create_openai_thread, get_openai_thread_response
from flask import Blueprint
from datetime import datetime
from flask_mail import Message

main = Blueprint('main', __name__)

@main.before_request
def create_or_load_session():
    if 'session_id' not in session:
        session['thread_id'] = None
        session['assistant_id'] = None
        session['language'] = None

@main.route('/')
def home():
    return render_template('home.html')

@main.route('/create_interview', methods=['POST'])
def create_interview():
    new_interview = Interview()
    db.session.add(new_interview)
    db.session.commit()
    return redirect(url_for('main.set_parameters', interview_id=new_interview.id))

@main.route('/set_parameters/<int:interview_id>', methods=['GET', 'POST'])
def set_parameters(interview_id):
    if request.method == 'POST':
        language = request.form['language']
        max_questions = int(request.form['max_questions'])
        interview_parameter = InterviewParameter(
            language=language,
            max_questions=max_questions,
            interview_id=interview_id
        )
        db.session.add(interview_parameter)
        session['interview_parameter_id'] = interview_parameter.id
        session['interview_id'] = interview_id
        db.session.commit()
        interview_link = url_for('main.start_chat', interview_parameter_id=interview_parameter.id, interview_id=interview_id, _external=True)

        # Send email with the interview link
        msg = Message('Your Interview Link', sender='sidney@tunz.ai', recipients=['golstein.sidney@gmail.com'])
        msg.body = f'Please use the following link to start the interview: {interview_link}'
        mail.send(msg)

        return render_template('interview_link.html', interview_link=interview_link)
    return render_template('set_parameters.html', interview_id=interview_id)


@main.route('/start/<int:interview_parameter_id>/<int:interview_id>', methods=['GET','POST'])
def start_chat(interview_parameter_id, interview_id):
    new_session = Session(interview_parameter_id=interview_parameter_id)
    db.session.add(new_session)
    db.session.commit()
    session['session_id'] = new_session.id


    interview_parameter = InterviewParameter.query.get(interview_parameter_id)      # Retrieve interview parameters
    session['language'] = interview_parameter.language

    # Create a new thread and get the first assistant response
    thread_id, assistant_id, assistant_response = create_openai_thread(interview_parameter.language)
    session['thread_id'] = thread_id
    session['assistant_id'] = assistant_id
    session['interview_parameter_id'] = interview_parameter_id
    session['interview_id'] = interview_id

    # Save the assistant's question to the database
    question = Question(content=assistant_response, session_id=new_session.id)
    db.session.add(question)
    db.session.commit()

    return redirect(url_for('main.chat', session_id=new_session.id, interview_parameter_id=interview_parameter_id, interview_id=interview_id))


@main.route('/chat', methods=['GET', 'POST'])
def chat():
    thank_you_message = "Thank you for the interview Sidney." if session['language'] == 'english' else "Merci pour l'entretien Sidney."

    if 'interview_parameter_id' not in session or 'interview_id' not in session:
        return redirect(url_for('main.home'))

    interview_parameter = InterviewParameter.query.get(session['interview_parameter_id'])
    current_session_id = session['session_id']
    questions = Question.query.filter_by(session_id=current_session_id).all()
    answers = Answer.query.filter_by(session_id=current_session_id).all()
    max_questions = interview_parameter.max_questions

    if request.method == 'POST':
        user_input = request.form['answer']
        question_id = request.form['question_id']
        thread_id = session['thread_id']
        assistant_id = session['assistant_id']

        if not thread_id or not assistant_id:
            return redirect(url_for('main.chat'))

        # Save user's answer to the database
        answer = Answer(content=user_input, question_id=question_id, session_id=current_session_id)
        db.session.add(answer)
        db.session.commit()

        # Check if the maximum number of questions has been reached
        num_questions = Question.query.filter_by(session_id=current_session_id).count()

        if num_questions >= interview_parameter.max_questions:
            session['finished'] = True
        else:
            # Get the assistant's next response
            assistant_response = get_openai_thread_response(thread_id, assistant_id, user_input)

            # Save the assistant's question to the database
            question = Question(content=assistant_response, session_id=current_session_id)
            db.session.add(question)
            db.session.commit()

        return redirect(url_for('main.chat'))

    return render_template('chat.html', questions=questions, answers=answers, max_questions=max_questions, thank_you_message=thank_you_message)




@main.route('/result', methods=['GET'])
def result():
    current_session_id = session.get('session_id')
    if not current_session_id:
        return redirect(url_for('main.home'))

    answers = Answer.query.filter_by(session_id=current_session_id).all()
    score = calculate_score(answers)  # Implement this function based on your grading logic
    return render_template('result.html', score=score)

@main.route('/restart', methods=['POST'])
def restart():
    session.pop('session_id', None)
    session.pop('thread_id', None)
    session.pop('assistant_id', None)
    session.pop('language', None)
    session.pop('finished', None)
    session.pop('interview_parameter_id', None)
    session.pop('interview_id', None)
    return redirect(url_for('main.home'))

def calculate_score(answers):
    score_result = len(answers) * 10  # Example logic: 10 points per answer
    score_type = "applicant_score"
    current_session_id = session.get('session_id')
    result = Result(score_type = score_type, score_result = score_result, session_id = current_session_id)
    db.session.add(result)
    db.session.commit()
    return score_result



# API RETRIEVAL

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


@main.route('/api/results', methods=['GET'])
def get_scores():
    results = Result.query.all()
    return jsonify([{
        'id': result.id,
        'score_type': result.score_type,
        'score_result': result.score_result,
        'session_id': result.session_id
    } for result in results])


@main.route('/api/interview_parameters', methods=['GET'])
def get_interview_parameters():
    interview_parameters = InterviewParameter.query.all()
    return jsonify([{
        'id': parameter.id,
        'language': parameter.language,
        'max_questions': parameter.max_questions,
        'interview_id': parameter.interview_id
    } for parameter in interview_parameters])


@main.route('/api/sessions', methods=['GET'])
def get_sessions():
    sessions = Session.query.all()
    return jsonify([{
        'id': session.id,
        'start_time': session.start_time,
        'interview_parameter_id' : session.interview_parameter_id,
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