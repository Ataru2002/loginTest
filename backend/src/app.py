import jwt, os, json
from flask import Flask, render_template, Response, jsonify, request
from flasgger import Swagger, swag_from
from auth_middleware import admin_required
from user import User
from model.main import execute
import cv2
import time
import threading

#TODO: will need to remove direct db setup from final product
from db import init_db, reset_db

app = Flask(__name__)
#TODO: set default anthentication key
SECRET_KEY = os.environ.get('SECRET_KEY') or 'sample_authentication_key'
print(SECRET_KEY)
app.config['SECRET_KEY'] = SECRET_KEY

swagger = Swagger(app)
camera = None



@app.route('/admin/list_all_users', methods=['GET'])
@admin_required
@swag_from({
    'tags': ['admin'],
    'summary': 'List all users (admin access only)',
    'parameters':[
        {
            'name': 'Authorization token',
            'in': 'header',
            'required': True,
            'description': 'Bearer token for admin authorization',
            'type': 'string',
            'example': 'Bearer sample_token'
        }
    ],
    'responses': {
        200: {
            'description': 'Successfully retrieved the list of users',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': 'Output written to user.txt'},
                    'result': {
                        'type': 'array',
                        'items': {'type': 'object'}
                    }
                }
            }
        },
        500: {
            'description': 'Internal server error',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': 'Something went wrong'},
                    'error': {'type': 'string', 'example': 'Error message'}
                }
            }
        }
    }
})
def list_all_users():
    try:
        user_lists = User().get_all()
        #with open('user.txt', 'w') as file:
        #    json.dump(user_lists, file, indent=4)
        #    return jsonify(message='Output written to user.txt'), 200
        return jsonify(user_lists), 200
    except Exception as e:
        return jsonify(message="Something went wrong", error=str(e)), 500

@app.route('/admin/delete_user', methods=['DELETE'])
@admin_required
@swag_from({
    'tags': ['admin'],
    'summary': 'Delete a user by ID (admin access only)',
    'parameters': [
        {
            'name': 'userid',
            'in': 'body',
            'required': True,
            'description': 'User ID to be deleted',
            'schema': {
                'type': 'object',
                'properties': {
                    'userid': {'type': 'string', 'example': '613b7d9f2b3d9a003d8b2a72'}
                },
                'required': ['userid']
            }
        }
    ],
    'responses': {
        202: {
            'description': 'User successfully deleted',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': 'User successfully deleted'}
                }
            }
        },
        400: {
            'description': 'Bad request - missing or invalid data',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': 'Please provide user info'},
                    'error': {'type': 'string', 'example': 'Bad request'}
                }
            }
        },
        402: {
            'description': 'Failed to delete user due to database issue',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': 'Failed to delete user with id {id}'},
                    'error': {'type': 'string', 'example': 'Database failed'}
                }
            }
        },
        500: {
            'description': 'Internal server error',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': 'Something went wrong'},
                    'error': {'type': 'string', 'example': 'Error message'}
                }
            }
        }
    }
})
def delete_user():
    try:
        data = request.json
        if not data:
            return jsonify(message="Please provide user info", error="Bad request"), 400
        
        old_user = User().delete(data['userid'])
        if old_user:
            id = data['userid']
            return jsonify(message="Failed to delete user with id {id}", error="Database failed"), 402
        
        return jsonify(message="User successfully deleted"), 202
    except Exception as e:
        return jsonify(message="Something went wrong", error=str(e)), 500

@app.route('/user/user_register', methods=['POST'])
@swag_from({
    'tags': ['user'],
    'summary': 'Register a new user',
    'parameters': [
        {
            'name': 'user',
            'in': 'body',
            'required': True,
            'description': 'Username and password to be registered',
            'schema': {
                'type': 'object',
                'properties': {
                    'username': {'type': 'string', 'example': 'john_doe'},
                    'password': {'type': 'string', 'example': 'some_secure_password'},
                    'email': {'type': 'string', 'example': 'someemail@test.com'}
                }
            }
        }
    ],
    'responses': {
        201: {
            'description': 'User successfully registered',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': 'User successfully added'}
                }
            }
        },
        400: {
            'description': 'Bad request - missing or invalid data',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': 'Please provide user info'},
                    'error': {'type': 'string', 'example': 'Bad request'}
                }
            }
        },
        401: {
            'description': 'User already exists or database error',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'User already exists or database error'}
                }
            }
        },
        500: {
            'description': 'Internal server error',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': 'Something went wrong'},
                    'error': {'type': 'string', 'example': 'Error message'}
                }
            }
        }
    }
})
def add_user():
    try:
        new_user = request.json
        if not new_user:
            return jsonify(message="Please provide user info", error="Bad request"), 400
        user = User().create(new_user["username"], new_user["email"], new_user["password"], isAdmin=False)
        if not user:
            return jsonify(error="User already exists or database error"), 401

        return jsonify(message="User successfully added"), 201
    except Exception as e:
        return jsonify(message="Something went wrong", error=str(e)), 500
    
@app.route('/user/user_login', methods=['POST'])
@swag_from({
    'tags': ['user'],
    'summary': 'User login',
    'parameters': [
        {
            'name': 'user',
            'in': 'body',
            'required': True,
            'description': 'Username and password for login',
            'schema': {
                'type': 'object',
                'properties': {
                    'username': {'type': 'string', 'example': 'john_doe'},
                    'password': {'type': 'string', 'example': 'some_user_password'}
                },
                'required': ['username', 'password']
            }
        }
    ],
    'responses': {
        203: {
            'description': 'User successfully logged in',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': 'Logged in successfully'},
                    'data': {'type': 'object'}
                }
            }
        },
        400: {
            'description': 'Bad request - missing or invalid data',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': 'Please provide user info'},
                    'error': {'type': 'string', 'example': 'Bad request'}
                }
            }
        },
        404: {
            'description': 'Unauthorized - incorrect credentials or user does not exist',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': 'Wrong username or password, or user does not exist'},
                    'error': {'type': 'string', 'example': 'Unauthorized'}
                }
            }
        },
        500: {
            'description': 'Internal server error',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': 'Something went wrong'},
                    'error': {'type': 'string', 'example': 'Error message'}
                }
            }
        }
    }
})
def user_login():
    try:
        data = request.json
        if not data:
            return jsonify(message="Please provide user info", error="Bad request"), 400
        
        curr_user = User().login(
            data['username'],
            data['password']
        )

        if curr_user:
            try:
                curr_user['token'] = jwt.encode(
                    {"userid": curr_user["userid"],
                     "tag": curr_user["tag"]},
                    app.config["SECRET_KEY"],
                    algorithm="HS256"
                )
                #TODO: should only return needed data
                return jsonify(message="Logged in successfully", data=curr_user), 203
            except Exception as e:
                return jsonify(message="Something went wrong", error=str(e)), 500

        return jsonify(message="Wrong username or password, or user does not exist", error="Unauthorized"), 404
        
    except Exception as e:
        return jsonify(message="Something went wrong", error=str(e)), 500


@app.route('/user/activate_webcam', methods=['POST'])
@swag_from({
    'tags': ['user'],
    'summary': 'Activate webcam from user',
    'responses': {
        204: {
            'description': 'Webcam activated and streaming',
        },
        400: {
            'description': 'Webcam failed',
        },
    }
})
def activate_webcam():
    global camera
    if camera is None:
        camera = cv2.VideoCapture(0)  # Start the webcam
        if not camera.isOpened():
            return jsonify({"message": "Webcam failed"}), 400
        
        # Start a thread to deactivate the camera after 10 seconds
        threading.Thread(target=stop_webcam, args=(10,)).start()
        return jsonify({"message": "Camera activated for 10 seconds"}), 204

def frames_gen():  
    global camera
    num_frames = [0]
    success, frame = camera.read()
    while success:
        execute(camera, frame, num_frames)
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        success, frame = camera.read()

def stop_webcam(duration):
    """
    Stop webcam after a certain amount of time
    """
    global camera
    time.sleep(duration)
    if camera is not None:
        camera.release()
        camera = None
        print("Camera deactivated")

@app.route('/video_feed')
def video_feed():
    global camera
    if camera is None or not camera.isOpened():
        return "Camera is not active", 404
    return Response(frames_gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    """
    HTML page to display the video stream.
    """
    return render_template('index.html')


with app.app_context():
    reset_db()
    init_db()
    dummy_admin = User().create("dummyAdmin", "admin@email.com", "admin_password", isAdmin=True)
    with open('admin.txt', 'w') as file:
            json.dump(dummy_admin, file, indent=4)




if __name__ == "__main__":
    app.run(debug=True, port=5000)

