from flask import Flask, render_template, request, redirect, url_for, session
import logic




import logic
import os
print(f"DEBUG: Soubor logic.py je zde: {os.path.abspath(logic.__file__)}")
print(f"DEBUG: Seznam funkcí: {dir(logic)}")




app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

@app.route('/')
def index():
    # Pokud je uživatel přihlášen, šup na dashboard
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    # Pokud ne, ukážeme mu jen čistý login
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    # Tato cesta teď slouží POUZE pro zpracování dat (POST)
    username = request.form.get('username')
    password = request.form.get('password')
    
    user_id = logic.login_user(username, password)
    
    if user_id:
        session['user_id'] = user_id
        return redirect(url_for('dashboard'))
    else:
        # Pokud se sekne, vrátíme ho na index s hláškou
        return "Chybné jméno nebo heslo. <a href='/'>Zkusit znovu</a>", 401
    
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user_id = logic.register_user(username, password)
        
        if user_id:
            return redirect(url_for('index'))
        else:
            return "Chyba: Uživatel již existuje.", 400
            
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    wheels = logic.get_user_wheels(session['user_id'])
    return render_template('dashboard.html', wheels=wheels)

@app.route('/add_wheel', methods=['POST'])
def add_wheel():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    title = request.form.get('title')
    if title:
        logic.add_new_wheel(session['user_id'], title)
    
    return redirect(url_for('dashboard'))

@app.route('/wheel/<int:wheel_id>')
def wheel_detail(wheel_id):
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    wheel = logic.get_wheel_details(wheel_id)
    items = logic.get_wheel_items(wheel_id)
    
    return render_template('wheel.html', wheel=wheel, items=items)

@app.route('/add_item/<int:wheel_id>', methods=['POST'])
def add_item(wheel_id):
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    label = request.form.get('label')
    if label:
        logic.add_item_to_wheel(wheel_id, label)
    
    return redirect(url_for('wheel_detail', wheel_id=wheel_id))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)