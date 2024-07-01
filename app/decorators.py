# app/decorators.py
from functools import wraps
from flask import request, jsonify, redirect, url_for, session
from app.models.admin import Admin

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        admin_id = request.args.get('admin_id')
        print(f"admin_id from URL: {admin_id}")

        if not admin_id:
            return jsonify({"msg": "Admin ID missing from URL"}), 400
        
        admin = Admin.query.get(admin_id)
        if not admin:
            return jsonify({"msg": "Access denied: Not an admin"}), 403
        
        session['admin_id'] = admin_id  # Set admin_id in session
        print(f"admin_id set in session: {session['admin_id']}")
        return f(*args, **kwargs)
    return decorated_function