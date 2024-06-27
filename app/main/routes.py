# Contains the routes related to the main functionality

from flask import render_template, request, redirect, url_for, jsonify, session, current_app, flash
from .. import db, mail
from ..models import Interview, InterviewParameter, Session, Question, Answer, Result, HR, Applicant, Company, Review, ReviewQuestion 
from ..openai_utils import create_openai_thread, get_openai_thread_response, get_thank_you_message
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from ..forms import ReviewForm, RatingForm
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

@main.route('/home')
#@jwt_required()
# routes/main.py
@main.route('/home/<int:user_id>')
def home(user_id):
    user = HR.query.get(user_id)
    if not user:
        return redirect(url_for('auth.login'))

    return render_template('hr/hr_homepage.html', hr_name=user.name, hr_surname=user.surname, company_name=user.company.name)

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

        return render_template('hr/interview_generated.html', interview_link = interview_link)
    return render_template('hr/create_interview.html', interview_id=interview_id)


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
        'applicant/applicant_home.html', 
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

    duration = interview_parameter.duration # Retrieve duration in minutes
    remaining_time = session.get('remaining_time', duration * 60)  # Get remaining time from session, default to full duration

    questions = Question.query.filter_by(session_id=current_session_id).all()
    answers = Answer.query.filter_by(session_id=current_session_id).all()
    max_questions = interview_parameter.max_questions
    applicant_name = session.get('applicant_name', 'N/A')
    applicant_email = session.get('applicant_email', 'N/A')  # Get the applicant's email from the session
    applicant_surname = session.get('applicant_surname', 'N/A')  # Get the applicant's name from the session

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

        # Update remaining time in session
        remaining_time = int(request.form['remaining_time'])
        session['remaining_time'] = remaining_time

        # Check if the maximum number of questions has been reached
        num_questions = Question.query.filter_by(session_id=current_session_id).count()

        if num_questions >= interview_parameter.max_questions or remaining_time <= 0:
            session['finished'] = True
            # Send email to HR
            hr_email = "sidney@tunz.ai"  # Replace with HR email address from a form
            hr_link = url_for('main.hr_result', session_id=current_session_id, _external=True)
            msg = Message('Interview Finished',
                        sender='noreply@tunz.ai',
                        recipients=[hr_email])
            msg.body = f'The interview of {applicant_name} {applicant_surname} (email: {applicant_email}) has finished. Click the following link to view the result: {hr_link}'
            mail.send(msg)
        else:
            # Get the assistant's next response
            assistant_response = get_openai_thread_response(thread_id, assistant_id, user_input)

            # Save the assistant's question to the database
            question = Question(content=assistant_response, session_id=current_session_id)
            db.session.add(question)
            db.session.commit()

        return redirect(url_for('main.chat'))

    return render_template('applicant/chat.html', questions=questions, answers=answers, max_questions=max_questions, thank_you_message=thank_you_message, applicant_name=applicant_name, duration=remaining_time, session_id=current_session_id)




@main.route('/finish_interview/<int:session_id>', methods=['GET'])
def finish_chat(session_id):
    current_session = Session.query.get_or_404(session_id)
    current_session.finished = True
    db.session.commit()

    # Send email to HR
    hr_email = "sidney@tunz.ai"  # Replace with HR email address from a form
    applicant_name = session.get('applicant_name', 'N/A')
    applicant_email = session.get('applicant_email', 'N/A')  # Get the applicant's email from the session
    applicant_surname = session.get('applicant_surname', 'N/A')  # Get the applicant's name from the session

    hr_link = url_for('main.hr_result', session_id=session_id, _external=True)
    msg = Message('Interview Finished',
                  sender='noreply@tunz.ai',
                  recipients=[hr_email])
    msg.body = f'The interview of {applicant_name} {applicant_surname} (email: {applicant_email}) has finished. Click the following link to view the result: {hr_link}'
    mail.send(msg)

    return redirect(url_for('main.applicant_review', session_id=session_id))




@main.route('/applicant_review/<int:session_id>', methods=['GET', 'POST'])
def applicant_review(session_id):
    form = ReviewForm()
    questions = [
        "How was the user experience with the AI interface?",
        "How fluid is the conversation?",
        "How pertinent were the questions?",
    ]

    if not form.questions.entries:
        for question_text in questions:
            question_form = RatingForm()
            form.questions.append_entry(question_form)

    if form.validate_on_submit():
        review = Review(
            session_id=session_id,
            comment=form.comment.data
        )
        db.session.add(review)
        db.session.commit()

        for idx, question_form in zip(range(len(questions)), form.questions.entries):
            question = ReviewQuestion(
                text=questions[idx],
                rating=int(question_form.rating.data),
                review_id=review.id
            )
            db.session.add(question)

        db.session.commit()
        flash('Thank you for your feedback!', 'success')
        return redirect(url_for('main.applicant_result'))

    return render_template('applicant/applicant_review.html', form=form, session_id=session_id, questions=questions)



@main.route('/applicant_result', methods=['GET'])
def applicant_result():
    current_session_id = session.get('session_id')
    if not current_session_id:
        return redirect(url_for('main.home'))

    answers = Answer.query.filter_by(session_id=current_session_id).all()
    score = calculate_score(answers)  # Implement this function based on your grading logic

    applicant_email = session.get('applicant_email', 'N/A')  # Get the applicant's email from the session
    applicant_name = session.get('applicant_name', 'N/A')  # Get the applicant's name from the session
    applicant_surname = session.get('applicant_surname', 'N/A')  # Get the applicant's name from the session

    return render_template('applicant/applicant_result.html', score=score, applicant_email=applicant_email, applicant_name=applicant_name, applicant_surname=applicant_surname)



@main.route('/hr_result/<int:session_id>', methods=['GET'])
def hr_result(session_id):
    applicant_email = session.get('applicant_email', 'N/A')
    session_data = Session.query.get_or_404(session_id)
    result = Result.query.filter_by(session_id=session_id).first()
    score = result.score_result if result else "No score available"
    return render_template('hr/hr_result.html', score=score, session_data=session_data, applicant_email=applicant_email)



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


def send_email(email_sender, email_receiver, message):
    msg = Message('Interview Finished',
                  sender=email_sender,
                  recipients=[email_receiver])
    msg.body = message
    return mail.send(msg)