import os
import mysql.connector
from dotenv import load_dotenv
import bcrypt

load_dotenv()

db_host = os.getenv('DB_HOST')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_name = os.getenv('DB_NAME')

class DatabaseConnector:
    def __init__(self):
        self.config = {
            'host': db_host,
            'user': db_user,
            'password': db_password,
            'database': db_name
        }
        self.connection = None

    def connect(self):
        if self.connection is None or not self.connection.is_connected():
            self.connection = mysql.connector.connect(**self.config)
        return self.connection
    
    def get_cursor(self):
        conn = self.connect()
        return conn.cursor(dictionary=True)
    
    def close(self):        
        if self.connection and self.connection.is_connected():
            self.connection.close()

    def commit(self):
        if self.connection:
            self.connection.commit()

def write_to_db(query, params):
    db = DatabaseConnector()
    cursor = db.get_cursor()
    cursor.execute(query, params)
    new_id = cursor.lastrowid
    db.commit()
    cursor.close()
    db.close()
    return new_id

def fetch_from_db(query, params):
    db = DatabaseConnector()
    cursor = db.get_cursor()
    cursor.execute(query, params)
    result = cursor.fetchall()
    cursor.close()
    db.close()
    return result

def username_exists(username):
    query = "SELECT * FROM users WHERE username = %s"
    params = (username,)
    result = fetch_from_db(query, params)
    if not result:
        return False

def get_user_id(username):
    query = "SELECT id FROM users WHERE username = %s"
    params = (username,)
    result = fetch_from_db(query, params)
    if not result:
        return None
    else:
        return result[0]['id']

def register_user(username, password):
    if username_exists(username):
        return None
    
    hash_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    query = "INSERT INTO users (username, password_hash) VALUES (%s, %s)"
    return write_to_db(query, (username, hash_pw))

def login_user(username, password):
    query = "SELECT id, password_hash FROM users WHERE username = %s"
    result = fetch_from_db(query, (username,))
    
    if result:
        user = result[0]
        stored_hash = user['password_hash'].encode('utf-8')
        if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
            return user['id']
            
    return None

def get_user_wheels(user_id):
    query = "SELECT * FROM wheels WHERE user_id = %s"
    return fetch_from_db(query, (user_id,))

def add_new_wheel(user_id, title):
    query = "INSERT INTO wheels (user_id, title) VALUES (%s, %s)"
    return write_to_db(query, (user_id, title))

def add_item_to_wheel(wheel_id, label):
    query = "INSERT INTO items (wheel_id, label) VALUES (%s, %s)"
    write_to_db(query, (wheel_id, label))


def random_pick(wheel_id):
    query = "SELECT label FROM items WHERE wheel_id = %s"
    items = fetch_from_db(query, (wheel_id,))
    if not items:
        return None
    import random
    return random.choice(items)['label']

