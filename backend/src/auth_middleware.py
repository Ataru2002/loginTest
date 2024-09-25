from functools import wraps
import jwt
from flask import request, abort, jsonify
from flask import current_app
from user import User

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]
        if not token:
            return {
                "message": "Authentication Token is missing!",
                "data": None,
                "error": "Unauthorized"
            }, 401
        try:
            data=jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
            current_user=User().get_by_id(data["userid"])
            if current_user is None:
                return {
                    "message": "Invalid Authentication token!",
                    "data": None,
                    "error": "Unauthorized"
                }, 401
            if current_user["tag"] != 'ADMIN':
                return {
                    "message": "Admin access required",
                    "data": None,
                    "error": "Forbidden"
                }, 403
        except jwt.ExpiredSignatureError: 
            return {
                "message": "Token has expired!",
                "data": None,
                "error": "Unauthorized"
            }, 401
        except jwt.InvalidTokenError:
            return {
                "message": "Invalid Token!",
                "data": None,
                "error": "Unauthorized"
            }, 401
        except Exception as e:
            return {
                "message": "Something went wrong",
                "data": None,
                "error": str(e)
            }, 500

        return f(*args, **kwargs)

    return decorated