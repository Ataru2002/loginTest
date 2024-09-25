import sqlite3
from db import get_next_adminid, get_next_userid

#TODO: will need to be changed to a hosted db url 
DATABASE = '../../database/test.db'

def get_db_connection():
    connect = sqlite3.connect(DATABASE)
    connect.row_factory = sqlite3.Row
    return connect

class User:
    def __init__(self):
        self.conn = get_db_connection()
    
    def create(self, username="", email="", password="", isAdmin=False):
        user = self.get_by_username(username)
        if user:
            return None
        if isAdmin:
            tag = "ADMIN"
            new_user_id = get_next_adminid()
        else:
            tag = "USER"
            new_user_id = get_next_userid()
        self.conn.execute('INSERT INTO users (userid, username, password, email, tag) VALUES (?, ?, ?, ?, ?)', (new_user_id, username, password, email, tag))
        self.conn.commit()
        return self.get_by_id(new_user_id)
    
    def get_all(self):
        users = self.conn.execute('SELECT * from users').fetchall()
        return [dict(user) for user in users]
    
    def get_by_id(self, userid):
        user = self.conn.execute('SELECT * FROM users WHERE userid = ?', (userid,)).fetchone()
        if not user:
            return None
        return dict(user)
    
    def get_by_username(self, username):
        user = self.conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        if not user:
            return None
        return dict(user)
    
    def get_by_email(self, email):
        user = self.conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        if not user:
            return None
        return dict(user)

    def delete(self, userid):
        self.conn.execute('DELETE FROM users WHERE userid = ?', (userid,))
        self.conn.commit()
        user = self.get_by_id(userid)
        return user #should be None

    def login(self, username, password):
        user = self.get_by_username(username)
        if not user or password != user.get('password'):
            return None
        user.pop('password')
        return user
