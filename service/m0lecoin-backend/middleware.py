from flask import request, jsonify, current_app as app
from functools import wraps
import jwt
from models import Users

def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split()[1]
    
        if not token:
            return jsonify({'success': False, 'message': 'a valid token is missing'})
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = Users.query.get(data['address'])
        except:
            return jsonify({'success': False, 'message': 'token is invalid'})
    
        return f(current_user, *args, **kwargs)
    return decorator