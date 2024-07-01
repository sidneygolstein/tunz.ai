from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, current_app, session
from app import db, bcrypt, mail
from app.models.hr import HR
from app.models.company import Company
from app.models.admin import Admin
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer

auth = Blueprint('auth', __name__)



def generate_confirmation_token(user_id, admin_id):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps({'user_id': user_id, 'admin_id': admin_id}, salt=current_app.config['SECURITY_PASSWORD_SALT'])

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
        admin = Admin.query.filter_by(email='sidney@tunz.ai').first()
        admin_id = admin.id  # Ensure the admin is logged in when registering a new HR
        admin_email = admin.email #'sidney@tunz.ai'  # Admin email

        if not admin_id:
            return jsonify({"msg": "Admin must be logged in to register a new HR"}), 403
        confirm_url = url_for('admin.confirm_account', user_id=hr.id, admin_id=admin_id, _external=True)
        
        
        # Send confirmation email to admin        
        msg = Message('New Account Registration',
                      sender='noreply@tunz.ai',
                      recipients=[admin_email])
        msg.body = f'New account registration request:\n\nEmail: {email}\nName: {name}\nSurname: {surname}\nCompany: {company_name}\n\nPlease confirm the account by visiting the following link: {confirm_url}'
        mail.send(msg)

        return jsonify({"msg": "Registration request sent to admin for confirmation. You will receive an email when your account will be confirmed"}), 200
    return render_template('auth/register.html')



## ADMIN AUTH ##

@auth.route('/admin_register', methods=['GET', 'POST'])
def admin_register():
    if request.method == 'POST':
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')
        surname = data.get('surname')

        if email != 'sidney@tunz.ai':
            return jsonify({"msg": "Only the designated admin can register"}), 400

        existing_admin = Admin.query.filter_by(email=email).first()
        if existing_admin:
            return jsonify({"msg": "Admin already exists"}), 400

        admin = Admin(email=email, name=name, surname=surname)
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()

        return jsonify({"msg": "Admin registration successful"}), 200
    return render_template('auth/admin_register.html')


@auth.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        admin = Admin.query.filter_by(email=email).first()

        if admin and admin.check_password(password):
            session['admin_id'] = admin.id  # Store admin_id in session
            session['admin_email'] = admin.email
            return jsonify({"msg": "Login successful", "admin_id": admin.id}), 200
        return jsonify({"msg": "Invalid credentials"}), 401
    return render_template('auth/admin_login.html')
