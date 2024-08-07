# Contains the routes related to the main functionality

import json
import math
import os
from flask import render_template, request, redirect, url_for, jsonify, session, current_app, flash
from .. import db, mail
from ..models import Interview, InterviewParameter, Session, Question, Answer, Result, HR, Applicant, Company, Review, ReviewQuestion, Thread 
from ..openai_utils import create_openai_thread, get_openai_thread_response, get_thank_you_message, create_scoring_thread
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from ..forms import ReviewForm, RatingForm
from flask import Blueprint
from datetime import datetime
from flask_mail import Message
from helpers import get_url, get_color


main = Blueprint('main', __name__)


### USEFUL METHOD

def get_interview_conversation(session_id):
    # Retrieve all questions and answers for the session
    questions = Question.query.filter_by(session_id=session_id).all()
    answers = Answer.query.filter_by(session_id=session_id).all()

    # Initialize conversation list
    conversation = []

    # Iterate through questions and answers, assuming they are in order
    for i in range(max(len(questions), len(answers))):
        if i < len(questions):
            conversation.append({'role': 'Q', 'content': questions[i].content})
        if i < len(answers):
            conversation.append({'role': 'A', 'content': answers[i].content})

    return conversation



######### HR ROUTES 

@main.route('/home/<int:hr_id>')
def home(hr_id):
    hr = HR.query.get_or_404(hr_id)
    if not hr:
        return redirect(url_for('auth.login'))
    
    interviews = Interview.query.filter_by(hr_id=hr_id).all()
    interview_data = []

    total_sessions = 0
    total_applicants_set = set()

    for interview in interviews:
        interview_parameters = InterviewParameter.query.filter_by(interview_id=interview.id).first()
        if not interview_parameters:
            continue  # Skip if no interview parameters are found

        sessions = Session.query.filter_by(interview_parameter_id=interview_parameters.id).all()
        session_data = []
        for session in sessions:
            applicant = Applicant.query.get(session.applicant_id)
            result = Result.query.filter_by(session_id=session.id).first()
            if not result or not result.score_interview or not result.score_interview.get('criteria_score'):
                continue  # Skip sessions with no results, no score_interview, or no criteria scores

            criteria_scores = result.score_interview['criteria_score']

            criteria_keys = [
                'communication_skills',
                'logical_reasoning_and_structure_and_problem_solving',
                'creativity',
                'business_acumen',
                'analytical_skills',
                'project_management_and_prioritization'
            ]

             # Retrieve the criteria values
            criteria_value = [criteria_scores.get(key, 0) for key in criteria_keys]

            # Load the ponderation from the interview parameters
            situations = json.loads(interview_parameters.situation) if interview_parameters.situation else []
            ponderation = json.loads(interview_parameters.ponderation) if interview_parameters.ponderation else [[1, 1, 1, 1, 1, 1] for _ in range(len(situations))]


            # Calculate the weighted criteria values
            weighted_criteria_values = [criteria_value[i] * ponderation[0][i] for i in range(len(criteria_value))]


            mean_score = sum(weighted_criteria_values) / (sum(ponderation[0]))

            if mean_score is None:
                continue  # Skip if mean score is None

            session_data.append({
                'applicant_name': applicant.name,
                'applicant_surname': applicant.surname,
                'applicant_email': applicant.email_address,
                'start_time': session.start_time,
                'score': criteria_scores,
                'mean_score': mean_score,
                'id': session.id
            })
            total_applicants_set.add(applicant.email_address)
        interview_data.append({
            'created_at': interview_parameters.start_time,
            'industry': interview_parameters.industry,
            'role': interview_parameters.role,            
            'subrole': interview_parameters.subrole,
            'situation': interview_parameters.get_situations(),
            'language': interview_parameters.language,
            'duration': interview_parameters.duration,
            'max_questions': interview_parameters.max_questions,
            'sessions_count': len(sessions),
            'interview_parameter_id': interview_parameters.id,
            'interview_id': interview_parameters.id,
            'sessions': session_data
        })

        total_sessions += len(sessions)

    total_interviews = len(interviews) 
    total_applicants = len(total_applicants_set)

    return render_template('hr/hr_homepage.html', hr_name=hr.name, hr_surname=hr.surname, company_name=hr.company.name,
                            hr_id=hr.id, interview_data=interview_data, total_interviews=total_interviews,
                           total_sessions=total_sessions, total_applicants=total_applicants, get_color=get_color)



@main.route('/create_interview/<int:hr_id>', methods=['GET', 'POST'])
def create_interview(hr_id):
    if request.method == 'POST':
        language = request.form['language']
        #role = request.form['role']
        role = "Sales"
        subrole = request.form['subrole']
        industry = request.form['industry']
        duration = int(request.form['duration'])
        situations = request.form.getlist('situations')

        # Load the JSON file to get the ponderation
        json_path = os.path.join(current_app.root_path, 'interview_situations_v3.json')
        with open(json_path) as f:
            interview_situations = json.load(f)
        
        ponderations = []
        for situation in situations:
            ponderation = interview_situations.get(role, {}).get(subrole, {}).get(situation, [3, 3, 3, 3, 3])
            ponderation = [1+(int(ponderation[i])-3)*0.1 for i in range(len(ponderation))]
            ponderations.append(ponderation)

        new_interview = Interview(hr_id=hr_id)
        db.session.add(new_interview)
        db.session.commit()

        interview_parameter = InterviewParameter(
            language=language,
            role=role,
            subrole = subrole,
            industry=industry,
            duration=duration,
            situation=json.dumps(situations),  # Store situations as JSON string
            ponderation=json.dumps(ponderations),  # Store ponderations as JSON string
            interview_id=new_interview.id
        )
        
        db.session.add(interview_parameter)
        db.session.commit()
        interview_link = get_url('main.applicant_home', hr_id=hr_id, interview_parameter_id=interview_parameter.id)
        return render_template('hr/interview_generated.html', interview_link=interview_link, hr_id=hr_id, interview_parameter=interview_parameter)
    
    # Construct the correct file path to the JSON file
    #json_path = os.path.join(current_app.root_path, 'interview_situations.json')

    # Construct the correct file path to the JSON file
    json_path = os.path.join(current_app.root_path, 'interview_situations_v3.json')

    with open(json_path) as f:
        interview_situations = json.load(f)

    return render_template('hr/create_interview.html', hr_id=hr_id, interview_situations=interview_situations)




@main.route('/session_details/<int:hr_id>/<int:session_id>', methods=['GET'])
def session_details(hr_id, session_id):
    session = Session.query.get(session_id)
    if not session:
        flash("Failed to retrieve interview thread. Please try again.", "danger")
        return redirect(url_for('main.home', hr_id=hr_id))

    applicant = Applicant.query.get_or_404(session.applicant_id)
    questions = Question.query.filter_by(session_id=session_id).all()
    result = Result.query.filter_by(session_id=session_id).first()
    interview_parameter = InterviewParameter.query.get(session.interview_parameter_id)

    conversation = get_interview_conversation(session_id)
    # Load criteria scores from the JSON string
    score_interview = result.score_interview

    criteria_scores = result.score_interview['criteria_score']

    criteria_keys = [
        'communication_skills',
        'logical_reasoning_and_structure_and_problem_solving',
        'creativity',
        'business_acumen',
        'analytical_skills',
        'project_management_and_prioritization'
    ]


    # Load the ponderation from the interview parameters
    situations = json.loads(interview_parameter.situation) if interview_parameter.situation else []
    ponderation = json.loads(interview_parameter.ponderation) if interview_parameter.ponderation else [[1, 1, 1, 1, 1, 1] for _ in range(len(situations))]

    # Map the ponderation values to importance descriptions
    ponderation_map = {
        1.2: 'Very important',
        1.1: 'Important',
        1.0: 'Moderately important',
        0.9: 'Slightly important',
        0.8: 'Not important'
    }

    # Map the ponderation values to star ratings
    star_rating_map = {
        1.2: '★★★★★',
        1.1: '★★★★☆',
        1.0: '★★★☆☆',
        0.9: '★★☆☆☆',
        0.8: '★☆☆☆☆'
    }
    criteria_importance = [(criteria_keys[i], star_rating_map.get(ponderation[0][i], '☆☆☆☆☆')) for i in range(len(criteria_keys))]




    return render_template('hr/session_details.html',
                           criteria_importance=criteria_importance,
                           hr_id=hr_id,    
                           session=session,
                           applicant=applicant,
                           conversation=conversation,
                           result=result,
                           interview_parameter=interview_parameter,
                           score_interview = score_interview)



@main.route('/comparison_details/<int:hr_id>/<int:interview_id>', methods=['GET'])
def comparison_details(hr_id, interview_id):
    hr = HR.query.get_or_404(hr_id)
    interview_parameters = InterviewParameter.query.filter_by(interview_id=interview_id).first()
    sessions = Session.query.filter_by(interview_parameter_id=interview_parameters.id).all()
    comparison_data = []
    for session in sessions:
        applicant = Applicant.query.get(session.applicant_id)
        result = Result.query.filter_by(session_id=session.id).first()
        
        if result and result.score_interview:
            criteria_score = result.score_interview.get("criteria_score")
            if criteria_score:
                mean_score = sum(criteria_score.values()) / len(criteria_score)
                comparison_data.append({
                    'applicant_name': applicant.name,
                    'applicant_surname': applicant.surname,
                    'applicant_email': applicant.email_address,
                    'criteria_scores': criteria_score,
                    'mean_score': mean_score,
                    'id': session.id  # Add session id here
                })

    return render_template('hr/comparison_details.html',
                           hr=hr,
                           hr_id=hr_id,
                           interview_parameters=interview_parameters,
                           comparison_data=comparison_data,
                           get_color=get_color)

####################################################################################################################################################################################
############################################################ APPLICANT #############################################################################################################
####################################################################################################################################################################################

@main.route('/applicant_home/<int:hr_id>/<int:interview_parameter_id>', methods=['GET', 'POST'])
def applicant_home(hr_id, interview_parameter_id):
    hr = HR.query.get_or_404(hr_id)
    interview_parameter = InterviewParameter.query.get_or_404(interview_parameter_id)
    interview_id = interview_parameter.interview_id
    duration = interview_parameter.duration
    company = Company.query.get_or_404(hr.company_id)
    company_name = company.name
    

    if request.method == 'POST':
        name = request.form['name']
        surname = request.form['surname']
        email = request.form['email']

        new_applicant = Applicant(name=name, surname=surname, email_address=email)
        db.session.add(new_applicant)
        db.session.commit()

        return redirect(url_for('main.start_chat', hr_id = hr_id, interview_parameter_id=interview_parameter_id, interview_id=interview_id, applicant_id = new_applicant.id))

    return render_template(
        'applicant/applicant_home.html', 
        interview_parameter_id=interview_parameter_id, 
        hr_id = hr_id,
        role=interview_parameter.role,
        subrole = interview_parameter.subrole, 
        industry=interview_parameter.industry, 
        hr_email=hr.email,
        duration=duration,
        company_name = company_name
    )



@main.route('/start/<int:hr_id>/<int:interview_parameter_id>/<int:interview_id>/<int:applicant_id>', methods=['GET', 'POST'])
def start_chat(hr_id, interview_parameter_id, interview_id, applicant_id):
    # Retrieve data
    interview_parameter = InterviewParameter.query.get_or_404(interview_parameter_id)
    applicant = Applicant.query.get_or_404(applicant_id)
    hr = HR.query.get_or_404(hr_id)

    company = Company.query.get_or_404(hr.company_id)

    company_name = company.name

    # Create thread
    thread_id, assistant_id, assistant_response = create_openai_thread(
        interview_parameter.language,
        interview_parameter.role,
        interview_parameter.subrole,
        interview_parameter.industry,
        interview_parameter.situation,
        applicant.name,
        applicant.surname,
        company_name
    )
    
    # Create and save a new session
    new_session = Session(interview_parameter_id=interview_parameter_id,
                        applicant_id=applicant_id,
                        remaining_time = 60*int(interview_parameter.duration), 
                        thread_id = thread_id, 
                        assistant_id = assistant_id,
                        finished=False)
    db.session.add(new_session)
    db.session.commit()
    
    # Create and save the question
    question = Question(content=assistant_response, session_id=new_session.id)
    db.session.add(question)
    db.session.commit()

    return redirect(url_for('main.chat', 
                            hr_id=hr_id, 
                            interview_id=interview_id, 
                            interview_parameter_id=interview_parameter_id, 
                            session_id=new_session.id, 
                            applicant_name=applicant.name, 
                            applicant_id=applicant.id))



@main.route('/chat/<int:hr_id>/<int:interview_id>/<int:interview_parameter_id>/<int:session_id>/<int:applicant_id>', methods=['GET', 'POST'])
def chat(hr_id, interview_id, interview_parameter_id, session_id, applicant_id):
    
    # Retrieve data
    hr = HR.query.get_or_404(hr_id)
    company = Company.query.get_or_404(hr.company_id)

    interview_parameter = InterviewParameter.query.get_or_404(interview_parameter_id)
    current_session = Session.query.get_or_404(session_id)
    applicant = Applicant.query.get_or_404(applicant_id)
    questions = Question.query.filter_by(session_id=session_id).all()
    answers = Answer.query.filter_by(session_id=session_id).all()

    thread_id = current_session.thread_id
    assistant_id = current_session.assistant_id
    
    applicant_name = applicant.name
    applicant_email = applicant.email_address
    applicant_surname = applicant.surname

    max_questions = interview_parameter.max_questions
    thank_you_message = get_thank_you_message(applicant.name)

    # If POST
    if request.method == 'POST':
        user_input = request.form['answer']
        question_id = request.form['question_id'] # ALWAYS THE SAME QUESTION ID
        remaining_time = int(request.form['remaining_time'])
        current_session.remaining_time = remaining_time
        db.session.commit()

        if not thread_id or not assistant_id:
            return redirect(url_for('main.chat', 
                                    hr_id=hr_id, 
                                    interview_id=interview_id, 
                                    interview_parameter_id=interview_parameter_id, 
                                    session_id=session_id,
                                    applicant_id=applicant_id))
        else:
            answer = Answer(content=user_input, question_id=question_id, session_id=session_id)
            db.session.add(answer)
            db.session.commit()

        

        if remaining_time <= 0:
            current_session.finished = True
            db.session.commit()
            hr_email = hr.email
            hr_link = get_url('main.home', hr_id=hr_id)
            msg = Message('Interview Finished',
                          sender='noreply@tunz.ai',
                          recipients=[hr_email])
            msg.body = f'The interview of {applicant_name} {applicant_surname} (email: {applicant_email}) has finished. Click the following link to view the result: {hr_link}'
            mail.send(msg)

        else:
            assistant_response = get_openai_thread_response(thread_id, assistant_id, user_input)
            question = Question(content=assistant_response, session_id=session_id)
            db.session.add(question)
            db.session.commit()

        # STILL NEED TO BE ENHANCED: WHEN THE SESSION IS FINISHED? NOT POSSIBLE TO COME BACK
        """
        if current_session.finished:
            return  redirect(url_for('main.applicant_review', 
                                    hr_id=hr_id, 
                                    interview_id=interview_id, 
                                    interview_parameter_id=interview_parameter_id, 
                                    session_id=session_id,
                                    applicant_id=applicant_id))
        """

        return redirect(url_for('main.chat', 
                            hr_id=hr_id, 
                            interview_id=interview_id, 
                            interview_parameter_id=interview_parameter_id, 
                            session_id=session_id, 
                            applicant_name=applicant_name, 
                            applicant_id=applicant.id))
        
    remaining_time = current_session.remaining_time

    return render_template('applicant/chat.html',
                           interview_parameter = interview_parameter,
                           company = company,
                           hr =hr,
                           questions=questions,
                           hr_id=hr_id,
                           answers=answers,
                           max_questions=max_questions,
                           thank_you_message=thank_you_message,
                           applicant_name=applicant_name,
                           duration=remaining_time,
                           session_id=session_id,
                           is_finished=current_session.finished,
                           interview_id=interview_id,
                           interview_parameter_id=interview_parameter_id,
                           applicant_id=applicant_id,
                           applicant = applicant)





@main.route('/finish_interview/<int:hr_id>/<int:interview_id>/<int:interview_parameter_id>/<int:session_id>/<int:applicant_id>', methods=['GET'])
def finish_chat(hr_id, interview_id, interview_parameter_id, session_id, applicant_id):
    #db.session.commit()
    current_session = Session.query.get_or_404(session_id)
    current_session.finished = True
    db.session.commit()
    interview_parameter = InterviewParameter.query.get_or_404(interview_parameter_id)
    hr = HR.query.get_or_404(hr_id)
    hr_email =  hr.email
    applicant = Applicant.query.get_or_404(applicant_id)
    applicant_name = applicant.name
    applicant_email = applicant.email_address
    applicant_surname = applicant.surname

    answers = Answer.query.filter_by(session_id=session_id).all()

    conversation = get_interview_conversation(session_id)
    
    score_interview = create_scoring_thread(interview_parameter.language, 
                                                                     interview_parameter.role, 
                                                                     interview_parameter.subrole,
                                                                     interview_parameter.industry, 
                                                                     interview_parameter.situation, 
                                                                     conversation)
    
    # CRITERIA RESULT = TOUT LE BIG DICO. 
    # Convert the dictionary to a JSON string before saving to the database
    score_interview_str = json.loads(score_interview)  
    
    result = Result(score_type = 'applicant_score', session_id = session_id, score_interview = score_interview_str)
    db.session.add(result)
    db.session.commit()

    hr_link = get_url('main.home',
                      hr_id = hr_id)
    msg = Message('Interview Finished',
                  sender='noreply@tunz.ai',
                  recipients=[hr_email])
    msg.body = f'The interview of {applicant_name} {applicant_surname} (email: {applicant_email}) has finished. The subject was about {interview_parameter}. Click the following link to view the result: {hr_link}'
    mail.send(msg)
    return redirect(url_for('main.applicant_review',  
                            hr_id = hr_id, 
                            interview_id=interview_id, 
                            interview_parameter_id=interview_parameter_id, 
                            session_id=session_id, 
                            applicant_id = applicant_id))


@main.route('/applicant_review/<int:hr_id>/<int:interview_id>/<int:interview_parameter_id>/<int:session_id>/<int:applicant_id>', methods=['GET', 'POST'])
def applicant_review(hr_id, interview_id, interview_parameter_id, session_id, applicant_id):
    form = ReviewForm()
    questions = [
        "How was the user experience with the AI interface?",
        "How fluid is the conversation?",
        "How pertinent were the questions?",]
    
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
        return redirect(url_for('main.applicant_result',  
                                hr_id = hr_id, 
                                interview_id=interview_id, 
                                interview_parameter_id=interview_parameter_id,
                                session_id=session_id, 
                                applicant_id = applicant_id))
    return render_template('applicant/applicant_review.html', 
                           form=form, 
                           hr_id = hr_id,
                           interview_id = interview_id,
                           interview_parameter_id = interview_parameter_id,
                           session_id=session_id, 
                           applicant_id = applicant_id,
                           questions=questions)


@main.route('/applicant_result/<int:hr_id>/<int:interview_id>/<int:interview_parameter_id>/<int:session_id>/<int:applicant_id>', methods=['GET'])
def applicant_result(hr_id, interview_id, interview_parameter_id, session_id, applicant_id):
    current_session_id = session_id
    interview_parameter = InterviewParameter.query.get_or_404(interview_parameter_id)
    if not current_session_id:
        return redirect(url_for('main.home'))
    score = Result.query.filter_by(session_id=session_id).first()  # Implement this function based on your grading logic
    applicant_feedback = score.score_interview['applicant_feedback']


    applicant = Applicant.query.get_or_404(applicant_id)
    applicant_name = applicant.name
    applicant_email = applicant.email_address
    applicant_surname = applicant.surname

    return render_template('applicant/applicant_result.html',
                            score=score, 
                            applicant_feedback = applicant_feedback,
                            applicant_email=applicant_email, 
                            applicant_name=applicant_name, 
                            applicant_surname=applicant_surname, 
                            applicant_id = applicant_id)





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

def calculate_score(answers,session_id):
    score_result = len(answers) * 10  # Example logic: 10 points per answer
    return score_result


def send_email(email_sender, email_receiver, message):
    msg = Message('Interview Finished',
                  sender=email_sender,
                  recipients=[email_receiver])
    msg.body = message
    return mail.send(msg)