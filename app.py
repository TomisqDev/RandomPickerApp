from flask import Flask, render_template, request, redirect, url_for, session, flash
import logic
from dotenv import load_dotenv
import os
import re

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'vyvojarsky-klic-123')

# Fix pro "csrf_token is undefined" - pokud ho HTML vyžaduje, ale app ho nepoužívá
@app.context_processor
def inject_csrf():
    return dict(csrf_token=lambda: "")

def is_safe(text):
    if not text: return False
    pattern = re.compile(r"^[a-zA-Z0-9 áéíóúůýčďěňřšťžÁÉÍÓÚŮÝČĎĚŇŘŠŤŽ?!]+$")
    return bool(pattern.match(text))

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    
    if not is_safe(username):
        flash('Invalid characters in username!', 'error')
        return redirect(url_for('index'))
    
    user_id = logic.login_user(username, password)
    
    if user_id:
        session['user_id'] = user_id
        return redirect(url_for('dashboard'))
    else:
        # CATEGORY: error
        flash('Invalid username or password!', 'error') 
        return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session: return redirect(url_for('index'))
    wheels = logic.get_user_wheels(session['user_id'])
    return render_template('dashboard.html', wheels=wheels, active_wheel=None, items=[])

@app.route('/wheel/<int:wheel_id>')
def wheel_detail(wheel_id):
    if 'user_id' not in session: return redirect(url_for('index'))
    all_wheels = logic.get_user_wheels(session['user_id'])
    current_wheel = logic.get_wheel_details(wheel_id)
    items = logic.get_wheel_items(wheel_id)
    return render_template('dashboard.html', wheels=all_wheels, active_wheel=current_wheel, items=items)

@app.route('/add_wheel', methods=['POST'])
def add_wheel():
    if 'user_id' not in session: return redirect(url_for('index'))
    title = request.form.get('title', '').strip()
    if title and is_safe(title):
        logic.add_new_wheel(session['user_id'], title)
    return redirect(url_for('dashboard'))

@app.route('/add_item/<int:wheel_id>', methods=['POST'])
def add_item(wheel_id):
    if 'user_id' not in session: return redirect(url_for('index'))
    label = request.form.get('label', '').strip()
    if label and is_safe(label):
        logic.add_item_to_wheel(wheel_id, label)
    return redirect(url_for('wheel_detail', wheel_id=wheel_id))

# --- TYHLE ROUTY TI CHYBĚLY (aby fungovalo mazání z HTML) ---

@app.route('/remove_wheel/<int:wheel_id>')
def remove_wheel(wheel_id):
    if 'user_id' in session:
        logic.delete_wheel(wheel_id)
    return redirect(url_for('dashboard'))

@app.route('/remove_item/<int:wheel_id>/<int:item_id>')
def remove_item(wheel_id, item_id):
    if 'user_id' in session:
        logic.delete_item(item_id)
    return redirect(url_for('wheel_detail', wheel_id=wheel_id))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not is_safe(username):
            flash("Invalid characters in username.", "error")
            return redirect(url_for('register'))
            
        user_id = logic.register_user(username, password)
        if user_id:
            # CATEGORY: success
            flash('Registration successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash("User already exists.", "error")
            return redirect(url_for('register'))
            
    return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True)