from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf.csrf import CSRFProtect
from markupsafe import escape
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'vasi-velmi-tajne-heslo-12345' # Změňte na silný klíč
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Aktivace CSRF ochrany
csrf = CSRFProtect(app)
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# --- MODELY (Předpokládaná struktura) ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)

class Wheel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    items = db.relationship('Item', backref='wheel', cascade="all, delete-orphan", lazy=True)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(100), nullable=False)
    wheel_id = db.Column(db.Integer, db.ForeignKey('wheel.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- ROUTES ---

@app.route('/')
@login_required
def dashboard():
    wheels = Wheel.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', wheels=wheels, active_wheel=None, items=[])

@app.route('/wheel/<int:wheel_id>')
@login_required
def wheel_detail(wheel_id):
    # Ochrana: Kolo musí patřit přihlášenému uživateli
    active_wheel = Wheel.query.filter_by(id=wheel_id, user_id=current_user.id).first_or_404()
    wheels = Wheel.query.filter_by(user_id=current_user.id).all()
    items = Item.query.filter_by(wheel_id=active_wheel.id).all()
    return render_template('dashboard.html', wheels=wheels, active_wheel=active_wheel, items=items)

@app.route('/add_wheel', methods=['POST'])
@login_required
def add_wheel():
    # Čištění a validace vstupu
    title = escape(request.form.get('title', '').strip())
    if not title or len(title) > 50:
        flash("Neplatný název kola.")
        return redirect(url_for('dashboard'))

    new_wheel = Wheel(title=title, user_id=current_user.id)
    db.session.add(new_wheel)
    db.session.commit()
    return redirect(url_for('wheel_detail', wheel_id=new_wheel.id))

@app.route('/add_item/<int:wheel_id>', methods=['POST'])
@login_required
def add_item(wheel_id):
    # Autorizace: Patří kolo mně?
    wheel = Wheel.query.filter_by(id=wheel_id, user_id=current_user.id).first_or_404()
    
    label = escape(request.form.get('label', '').strip())
    if not label or len(label) > 100:
        flash("Neplatná položka.")
        return redirect(url_for('wheel_detail', wheel_id=wheel_id))

    new_item = Item(label=label, wheel_id=wheel.id)
    db.session.add(new_item)
    db.session.commit()
    return redirect(url_for('wheel_detail', wheel_id=wheel_id))

@app.route('/remove_item/<int:wheel_id>/<int:item_id>')
@login_required
def remove_item(wheel_id, item_id):
    # SQL Injection ochrana: SQLAlchemy parametry
    # IDOR ochrana: join s Wheel a kontrola user_id
    item = Item.query.join(Wheel).filter(
        Item.id == item_id,
        Wheel.id == wheel_id,
        Wheel.user_id == current_user.id
    ).first_or_404()

    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('wheel_detail', wheel_id=wheel_id))

@app.route('/remove_wheel/<int:wheel_id>')
@login_required
def remove_wheel(wheel_id):
    wheel = Wheel.query.filter_by(id=wheel_id, user_id=current_user.id).first_or_404()
    db.session.delete(wheel)
    db.session.commit()
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)