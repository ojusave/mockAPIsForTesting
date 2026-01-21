from functools import wraps
from flask import request, jsonify

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        # Debug logging to help diagnose issues
        print(f"DEBUG: Authorization header received: {auth_header}")
        print(f"DEBUG: All headers: {dict(request.headers)}")
        
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
                "details": f"Authorization header must start with 'Bearer '. Received: '{auth_header[:20]}...'"
            }}), 401
            
        # For mock API, we accept any token
        return f(*args, **kwargs)
    return decorated 