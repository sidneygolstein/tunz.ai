from flask import Blueprint, request, render_template, redirect, url_for, flash, current_app
from app import db, mail
from app.models.hr import HR
from app.models.company import Company
from app.models.interview import Interview
from flask_mail import Message

admin = Blueprint('admin', __name__)

@admin.route('/confirm/<int:user_id>', methods=['GET', 'POST'])
def confirm_account(user_id):
    user = HR.query.get(user_id)
    if not user_id:
        flash('The confirmation link is invalid or has expired.', 'danger')
        return redirect(url_for('admin.home'))

    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('admin.home'))

    return render_template('admin/admin_account_confirmation.html', email=user.email, name=user.name, surname=user.surname, company_name=user.company.name, user_id=user.id)

@admin.route('/accept/<int:user_id>', methods=['POST'])
def accept_account(user_id):
    user = HR.query.get_or_404(user_id)
    user.confirmed = True
    db.session.commit()

    # Send email to HR confirming account activation
    msg = Message('Account Confirmed',
                  sender='noreply@tunz.ai',
                  recipients=[user.email])
    msg.body = f'Your account has been confirmed by the admin. You can now login using your credentials. Login here: {url_for('auth.login', _external=True)}'
    mail.send(msg)
    return redirect(url_for('admin.home'))

@admin.route('/deny/<int:user_id>', methods=['POST'])
def deny_account(user_id):
    user = HR.query.get_or_404(user_id)
    # Send email to HR denying account activation
    msg = Message('Account Denied',
                  sender='noreply@tunz.ai',
                  recipients=[user.email])
    msg.body = f'Your account has been denied by the admin. You cannot login. If you have any question, please contact: sidney@tunz.ai or sebastien@tunz.ai .'
    mail.send(msg)

    db.session.delete(user)
    db.session.commit()

    
    return redirect(url_for('admin.home'))

@admin.route('/home', methods=['GET'])
def home():
    return render_template('admin/admin_homepage.html')
