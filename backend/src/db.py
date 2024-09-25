import sqlite3

#TODO: will need to be changed to a hosted db url 
DATABASE = '../../database/test.db'

#TODO: make this global variable worldwide
admin_id = 100000001
next_id = 200000001

def get_db_connection():
    connect = sqlite3.connect(DATABASE)
    connect.row_factory = sqlite3.Row
    return connect

def init_db():
    connect = get_db_connection()
    connect.execute('''
        CREATE TABLE IF NOT EXISTS users(
            userid int NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL, 
            email TEXT NOT NULL,
            tag TEXT NOT NULL,
            PRIMARY KEY (userid, username)
        )
    ''')
    connect.commit()
    connect.close()

#delete all data stored in the db and recreate tables
def reset_db():
    global admin_id 
    global next_id 

    admin_id = 100000001
    next_id = 200000001

    connect = get_db_connection()
    connect.execute('''
        DROP TABLE IF EXISTS users;
    ''')
    init_db()

#temporary function TODO: delete this
def get_next_userid():
    global next_id
    temp = next_id
    next_id += 1
    return temp

#temporary function TODO: delete this
def get_next_adminid():
    global admin_id
    temp = admin_id
    admin_id += 1
    return temp