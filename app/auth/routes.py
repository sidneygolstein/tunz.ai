from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, current_app
from app import db, bcrypt, mail
from app.models.hr import HR
from app.models.company import Company
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer

auth = Blueprint('auth', __name__)



def generate_confirmation_token(user_id):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(user_id, salt=current_app.config['SECURITY_PASSWORD_SALT'])

def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        user_id = serializer.loads(token, salt=current_app.config['SECURITY_PASSWORD_SALT'], max_age=expiration)
    except:
        return False
    return user_id

# To be enhanced with jwt
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        user = HR.query.filter_by(email=email).first()

        if user and user.check_password(password):
            if user.confirmed:
                return jsonify({"msg": "Login successful", "user_id": user.id}), 200
            else:
                return jsonify({"msg": "Account not confirmed by admin"}), 400
        return jsonify({"msg": "Invalid credentials"}), 401
    return render_template('auth/login.html')

# To be enhanced with jwt
@auth.route('/logout', methods=['POST'])
def logout():
    return redirect(url_for('auth.login'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')
        surname = data.get('surname')
        company_name = data.get('company_name')

        existing_user = HR.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({"msg": "User already exists"}), 400
        
        existing_company = Company.query.filter_by(name=company_name).first()
        if not existing_company:
            company = Company(name=company_name)
            db.session.add(company)
            db.session.commit()
        else:
            company = existing_company

        hr = HR(email=email, name=name, surname=surname, company_id=company.id)
        hr.set_password(password)
        hr.confirmed = False  # New accounts need to be confirmed
        db.session.add(hr)
        db.session.commit()

        # Generate confirmation link
        token = generate_confirmation_token(hr.id)
        confirm_url = url_for('auth.confirm_account', user_id=hr.id, _external=True)
        deny_url = url_for('auth.deny_account', user_id=hr.id, _external=True)
        
        # Send confirmation email to admin
        admin_email = 'sidney@tunz.ai'  # Admin email
        msg = Message('New Account Registration',
                      sender='noreply@tunz.ai',
                      recipients=[admin_email])
        msg.body = f'New account registration request:\n\nEmail: {email}\nName: {name}\nSurname: {surname}\nCompany: {company_name}\n\nPlease confirm the account by visiting the following link: {confirm_url}, or deny the account by visiting the following link: {deny_url}'
        mail.send(msg)

        return jsonify({"msg": "Registration request sent to admin for confirmation. You will receive an email when your account will be confirmed"}), 200
    return render_template('auth/register.html')

@auth.route('/confirm/<int:user_id>', methods=['GET'])
def confirm_account(user_id):
    hr_confirmed = HR.query.get_or_404(user_id)
    hr_confirmed.confirmed = True
    db.session.commit()

    # Send email to HR confirming account activation
    msg = Message('Account Confirmed',
                  sender='noreply@tunz.ai',
                  recipients=[hr_confirmed.email])
    msg.body = f'Your account has been confirmed by the admin. You can now login using your credentials.'
    mail.send(msg)
    return redirect(url_for('auth.login'))  # Redirect to login page after confirmation

@auth.route('/deny/<int:user_id>', methods=['GET'])
def deny_account(user_id):
    hr_denied = HR.query.get_or_404(user_id)
    hr_denied.confirmed = False
    user_id = hr_denied.id
    if not user_id:
        flash('The confirmation link is invalid or has expired.', 'danger')
        return redirect(url_for('main.home'))

    db.session.delete(hr_denied)
    db.session.commit()
    # Send email to HR denying account activation
    msg = Message('Account Denied',
                  sender='noreply@tunz.ai',
                  recipients=[hr_denied.email])
    msg.body = f'Your account has been denied by the admin. You cannot login. If you have any question, please contact: sidney@tunz.ai or sebastien@tunz.ai .'
    mail.send(msg)
    return redirect(url_for('auth.login'))  # Redirect to login page after confirmation

