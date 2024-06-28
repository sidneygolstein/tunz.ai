# app/decorators.py
from functools import wraps
from flask import request, jsonify, redirect, url_for
from app.models.admin import Admin

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        admin_id = request.args.get('admin_id')
        admin = Admin.query.get(admin_id)
        if not admin:
            return jsonify({"msg": "Access denied: Not an admin"}), 403
        return f(*args, **kwargs)
    return decorated_function

