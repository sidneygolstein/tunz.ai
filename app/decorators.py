# app/decorators.py
from functools import wraps
from flask import request, jsonify, redirect, url_for, session
from app.models.admin import Admin

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        admin_id = session.get('admin_id')
        if not admin_id:
            return jsonify({"msg": "Admin ID missing from session"}), 400
        
        admin = Admin.query.get(admin_id)
        if not admin:
            return jsonify({"msg": "Access denied: Not an admin"}), 403
        
        return f(*args, **kwargs)
    return decorated_function