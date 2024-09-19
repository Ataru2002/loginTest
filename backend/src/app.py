import sqlite3
from flask import Flask, jsonify, request
from flasgger import Swagger, swag_from

app = Flask(__name__)
swagger = Swagger(app)


DATABASE = '../../database/test.db'


def get_db_connection():
    connect = sqlite3.connect(DATABASE)
    connect.row_factory = sqlite3.Row
    return connect

def init_db():
    connect = get_db_connection()
    #TODO: define Primary Key
    connect.execute('''
        CREATE TABLE IF NOT EXISTS users(
            id int,
            username TEXT UNIQUE PRIMARY KEY,
            password TEXT
        )
    ''')
    connect.commit()
    connect.close()

'''
@app.route('/api/list_all_members', methods=['POST'])
@swag_from({
    'parameters': [
        {
            'name': 'sql',
            'in': 'body',
            'required': True,
            'description': 'SQL command to execute',
            'schema': {
                'type': 'object',
                'properties': {
                    'query': {
                        'type': 'string',
                        'example': 'SELECT * FROM users;'
                    }
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'SQL command success',
            'schema': {
                'type': 'object',
                'properties': {
                    'result': {
                        'type': 'array',
                        'items': {
                            'type': 'object'
                        }
                    }
                }
            }
        },
        400:{
            'description': 'SQL execution fail',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'Error message'
                    }
                }
            }
        }
    }
})
'''

@app.route('/api/list_all_members', methods=['GET'])
@swag_from({
    'responses': {
        200: {
            'description': 'SQL command success',
            'schema': {
                'type': 'object',
                'properties': {
                    'result': {
                        'type': 'array',
                        'items': {
                            'type': 'object'
                        }
                    }
                }
            }
        },
        400:{
            'description': 'SQL execution fail',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'Error message'
                    }
                }
            }
        }
    }
})

def list_all_members():
    try:
        query = "SELECT * from users"
        connect = get_db_connection()
        cursor = connect.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        result = [dict(row) for row in rows]
        connect.close()
        return jsonify(result=result), 200
    except Exception as e:
        print(str(e))
        return jsonify({'error': str(e)}), 400


@app.route('/api/insert_members', methods=['POST'])
@swag_from({
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'description': 'SQL command to execute',
            'schema': {
                'type': 'object',
                'properties': {
                    'username': {
                        'type': 'string',
                        'example': 'john_doe'
                    },
                    'password': {
                        'type': 'string',
                        'example': 'some_secure_password'
                    }
                }
            }
        }
    ],
    'responses': {
        201: {
            'description': 'User successfully added',
            'schema': {
                'type': 'object',
                'properties': {
                    'result': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'example': 'User successfully added'
                        }
                    }
                }
            }
        },
        400:{
            'description': 'Error adding user to database',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'User already exist or database error'
                    }
                }
            }
        }
    }
})

def insert_user():
    try:
        data = request.json
        ids = -1 #will need to change later
        username = data.get('username')
        password = data.get('password')

        connect = get_db_connection()
        cursor = connect.cursor()

        cursor.execute('INSERT INTO users (id, username, password) VALUES (?, ?, ?)', (ids, username, password))
        connect.commit()
        connect.close()

        return jsonify(message="User successfully added"), 201

    except sqlite3.IntegrityError:
        return jsonify(error="Username already exists"), 400
    except Exception as e:
        return jsonify(error=str(e)), 400

@app.route('/api/delete_members', methods=['POST'])
@swag_from({
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'description': 'SQL command to execute',
            'schema': {
                'type': 'object',
                'properties': {
                    'username': {
                        'type': 'string',
                        'example': 'john_doe'
                    }
                },
                'required':['username']
            }
        }
    ],
    'responses': {
        202: {
            'description': 'User successfully deleted',
            'schema': {
                'type': 'object',
                'properties': {
                    'result': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'example': 'User successfully deleted'
                        }
                    }
                }
            }
        },
        400:{
            'description': 'Error deleting user to database',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'User does not exist or database error'
                    }
                }
            }
        }
    }
})

def delete_user():
    try:
        data = request.json
        username = data.get('username')

        connect = get_db_connection()
        cursor = connect.cursor()

        cursor.execute('DELETE FROM users WHERE username = ?', (username,))
        connect.commit()
        connect.close()

        if cursor.rowcount == 0:
            return jsonify(message="User not found"), 400

        return jsonify(message="User successfully added"), 202
    except Exception as e:
        return jsonify(error=str(e)), 400

@app.route('/api/user_login', methods=['POST'])
@swag_from({
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'description': 'SQL command to execute',
            'schema': {
                'type': 'object',
                'properties': {
                    'username': {
                        'type': 'string',
                        'example': 'john_doe'
                    },
                    'password': {
                        'type': 'string',
                        'example': 'some_user_password'
                    }
                },
                'required':['username', 'password']
            }
        }
    ],
    'responses': {
        203: {
            'description': 'User successfully logged in',
            'schema': {
                'type': 'object',
                'properties': {
                    'result': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'example': 'User successfully logged in'
                        }
                    }
                }
            }
        },
        400:{
            'description': 'Error logging user in',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'Wrong username or password, or user does not exist'
                    }
                }
            }
        }
    }
})

def user_login():
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')

        connect = get_db_connection()
        cursor = connect.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?' (username, password))
        connect.commit()
        connect.close()

        if cursor.rowcount != 1:
            return jsonify(message="Wrong username or password, or user does not exist"), 400
        
        return jsonify(message="Logged in successfully"), 203
    except Exception as e:
        return jsonify(error=str(e)), 400


with app.app_context():
    init_db()

if __name__ == "__main__":
    app.run(debug=True)

