# Contains the routes related to the main functionality

from flask import render_template, request, redirect, url_for, jsonify, session, current_app
from .. import db, mail
from ..models import Interview, InterviewParameter, Session, Question, Answer, Result, HR, Applicant, Company  
from ..openai_utils import create_openai_thread, get_openai_thread_response, get_thank_you_message
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
        session.clear() 
        language = request.form['language']
        max_questions = int(request.form['max_questions'])
        role = request.form['role']
        industry = request.form['industry']
        duration = int(request.form['duration'])
        
        interview_parameter = InterviewParameter(
            language=language,
            max_questions=max_questions,
            role=role,
            industry=industry,
            duration=duration,
            interview_id=interview_id
        )
        
        db.session.add(interview_parameter)
        session['interview_parameter_id'] = interview_parameter.id
        session['interview_id'] = interview_id
        session['hr_email'] = 'sidney@tunz.ai'  # Replace with actual HR email when login functionalities
        db.session.commit()
        interview_link = url_for('main.applicant_home', interview_parameter_id=interview_parameter.id, _external=True)

        return render_template('interview_generated.html', interview_link = interview_link)
    return render_template('set_parameters.html', interview_id=interview_id)


@main.route('/applicant_home/<int:interview_parameter_id>', methods=['GET', 'POST'])
def applicant_home(interview_parameter_id):
    interview_parameter = InterviewParameter.query.get_or_404(interview_parameter_id)
    interview_id = interview_parameter.interview_id
    duration = interview_parameter.duration

    if request.method == 'POST':
        name = request.form['name']
        surname = request.form['surname']
        email = request.form['email']

        new_applicant = Applicant(name=name, surname=surname, email_address=email)
        db.session.add(new_applicant)
        db.session.commit()

        session['applicant_id'] = new_applicant.id
        session['applicant_email'] = email
        session['applicant_name'] = name
        session['applicant_surname'] = surname

        return redirect(url_for('main.start_chat', interview_parameter_id=interview_parameter_id, interview_id = interview_id))

    return render_template(
        'applicant_home.html', 
        interview_parameter_id=interview_parameter_id, 
        role=interview_parameter.role, 
        industry=interview_parameter.industry, 
        hr_email=session.get('hr_email', 'HR'),
        duration = duration
        )



@main.route('/start/<int:interview_parameter_id>/<int:interview_id>', methods=['GET','POST'])
def start_chat(interview_parameter_id, interview_id):
    applicant_id = session.get('applicant_id')
    new_session = Session(interview_parameter_id=interview_parameter_id, applicant_id = applicant_id)
    db.session.add(new_session)
    db.session.commit()
    session['session_id'] = new_session.id

    # Retrieve applicant email
    applicant_name = session.get('applicant_name')

    interview_parameter = InterviewParameter.query.get(interview_parameter_id)      # Retrieve interview parameters
    session['language'] = interview_parameter.language

    # Create a new thread and get the first assistant response
    thread_id, assistant_id, assistant_response = create_openai_thread(
        interview_parameter.language,
        interview_parameter.role,
        interview_parameter.industry,
        applicant_name
        )
    
    session['thread_id'] = thread_id
    session['assistant_id'] = assistant_id
    session['interview_parameter_id'] = interview_parameter_id
    session['interview_id'] = interview_id

    # Save the assistant's question to the database
    question = Question(content=assistant_response, session_id=new_session.id)
    db.session.add(question)
    db.session.commit()

    return redirect(url_for('main.chat', session_id=new_session.id, interview_parameter_id=interview_parameter_id, interview_id=interview_id, applicant_name = applicant_name))

@main.route('/chat', methods=['GET', 'POST'])
def chat():

    if 'interview_parameter_id' not in session or 'interview_id' not in session:
        return redirect(url_for('main.home'))

    interview_parameter = InterviewParameter.query.get(session['interview_parameter_id'])
    current_session_id = session['session_id']
    questions = Question.query.filter_by(session_id=current_session_id).all()
    answers = Answer.query.filter_by(session_id=current_session_id).all()
    max_questions = interview_parameter.max_questions
    applicant_name = session.get('applicant_name', 'N/A')
    thank_you_message = get_thank_you_message(applicant_name)

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

    return render_template('chat.html', questions=questions, answers=answers, max_questions=max_questions, thank_you_message=thank_you_message, applicant_name=applicant_name)




@main.route('/applicant_result', methods=['GET'])
def result():
    current_session_id = session.get('session_id')
    if not current_session_id:
        return redirect(url_for('main.home'))

    answers = Answer.query.filter_by(session_id=current_session_id).all()
    score = calculate_score(answers)  # Implement this function based on your grading logic

    applicant_email = session.get('applicant_email', 'N/A')  # Get the applicant's email from the session
    applicant_name = session.get('applicant_name', 'N/A')  # Get the applicant's name from the session
    applicant_surname = session.get('applicant_surname', 'N/A')  # Get the applicant's name from the session


    # Send email to HR
    hr_email = "sidney@tunz.ai"  # Replace with HR email address from a form
    hr_link = url_for('main.hr_result', session_id=current_session_id, _external=True)
    msg = Message('Interview Finished',
                  sender='noreply@tunz.ai',
                  recipients=[hr_email])
    msg.body = f'The interview of {applicant_email} has finished. Click the following link to view the result: {hr_link}'
    mail.send(msg)

    return render_template('applicant_result.html', score=score, applicant_email=applicant_email, applicant_name = applicant_name, applicant_surname = applicant_surname)

@main.route('/hr_result/<int:session_id>', methods=['GET'])
def hr_result(session_id):
    applicant_email = session.get('applicant_email', 'N/A')
    session_data = Session.query.get_or_404(session_id)
    result = Result.query.filter_by(session_id=session_id).first()
    score = result.score_result if result else "No score available"
    return render_template('hr_result.html', score=score, session_data=session_data, applicant_email=applicant_email)



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

