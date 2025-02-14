from functools import wraps
from flask import request, jsonify

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({"error": {
                "code": "401",
                "message": "Authentication required",
                "details": "No authorization token provided"
            }}), 401
            
        if not auth_header.startswith('Bearer '):
            return jsonify({"error": {
                "code": "401",
                "message": "Invalid authentication format",
                "details": "Authorization header must start with 'Bearer'"
            }}), 401
            
        # For mock API, we accept any token
        return f(*args, **kwargs)
    return decorated 