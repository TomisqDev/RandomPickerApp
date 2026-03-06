import bcrypt
import random
from database import DatabaseConnector

# Pomocná funkce pro čtení (upraveno pro vaši třídu)
def fetch_from_db(query, params):
    db = DatabaseConnector()
    cursor = db.get_cursor()
    cursor.execute(query, params)
    result = cursor.fetchall()
    cursor.close()
    db.close()
    return result

# Pomocná funkce pro zápis (vrací lastrowid)
def write_to_db(query, params):
    db = DatabaseConnector()
    conn = db.connect()
    cursor = conn.cursor()
    cursor.execute(query, params)
    new_id = cursor.lastrowid
    db.commit()
    cursor.close()
    db.close()
    return new_id

def username_exists(username):
    query = "SELECT id FROM users WHERE username = %s"
    result = fetch_from_db(query, (username,))
    return len(result) > 0  # Vrátí True, pokud uživatel existuje

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
    query = "SELECT id, title FROM wheels WHERE user_id = %s"
    return fetch_from_db(query, (user_id,))

def add_new_wheel(user_id, title):
    query = "INSERT INTO wheels (user_id, title) VALUES (%s, %s)"
    return write_to_db(query, (user_id, title))

def random_pick(wheel_id):
    query = "SELECT label FROM items WHERE wheel_id = %s"
    items = fetch_from_db(query, (wheel_id,))
    if not items:
        return None
    return random.choice(items)['label']

def add_item_to_wheel(wheel_id, label):
    query = "INSERT INTO items (wheel_id, label) VALUES (%s, %s)"
    return write_to_db(query, (wheel_id, label))

def get_wheel_details(wheel_id):
    query = "SELECT * FROM wheels WHERE id = %s"
    result = fetch_from_db(query, (wheel_id,))
    return result[0] if result else None

def get_wheel_items(wheel_id):
    query = "SELECT * FROM items WHERE wheel_id = %s"
    return fetch_from_db(query, (wheel_id,))