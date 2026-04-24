from flask import Flask, request, redirect, url_for, session, flash, render_template_string
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tech2027-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tech2027.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Produit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    prix = db.Column(db.Float, nullable=False)

# TEMPLATES DANS LE CODE
LOGIN_PAGE = """
<!doctype html><html><head><title>TECH 2027</title>
<style>body{font-family:sans-serif;background:#f0f2f5;display:flex;justify-content:center;align-items:center;height:100vh;margin:0}
.box{background:white;padding:40px;border-radius:10px;box-shadow:0 4px 12px rgba(0,0,0,0.1);width:320px;text-align:center}
h1{color:#0A2540;margin:0}h1 span{color:#FF6A00}h2{color:#1E90FF;margin:10px 0 20px}
input{width:100%;padding:12px;margin:8px 0;border:1px solid #ddd;border-radius:5px;box-sizing:border-box}
button{width:100%;padding:12px;background:#FF6A00;color:white;border:none;border-radius:5px;font-weight:bold;cursor:pointer}
a{color:#1E90FF;text-decoration:none}.flash{color:red;margin-bottom:10px}</style></head>
<body><div class="box"><h1>TECH<span>2027</span></h1><h2>Connexion</h2>
{% with messages = get_flashed_messages() %}{% if messages %}<div class="flash">{{ messages[0] }}</div>{% endif %}{% endwith %}
<form method="post"><input name="email" type="email" placeholder="Email" required>
<input name="password" type="password" placeholder="Mot de passe" required>
<button type="submit">Se connecter</button></form>
<p>Pas de compte? <a href="{{ url_for('register') }}">S'inscrire</a></p></div></body></html>
"""

REGISTER_PAGE = """
<!doctype html><html><head><title>TECH 2027</title>
<style>body{font-family:sans-serif;background:#f0f2f5;display:flex;justify-content:center;align-items:center;height:100vh;margin:0}
.box{background:white;padding:40px;border-radius:10px;box-shadow:0 4px 12px rgba(0,0,0,0.1);width:320px;text-align:center}
h1{color:#0A2540;margin:0}h1 span{color:#FF6A00}h2{color:#1E90FF;margin:10px 0 20px}
input{width:100%;padding:12px;margin:8px 0;border:1px solid #ddd;border-radius:5px;box-sizing:border-box}
button{width:100%;padding:12px;background:#FF6A00;color:white;border:none;border-radius:5px;font-weight:bold;cursor:pointer}
a{color:#1E90FF;text-decoration:none}.flash{color:red;margin-bottom:10px}</style></head>
<body><div class="box"><h1>TECH<span>2027</span></h1><h2>Inscription</h2>
{% with messages = get_flashed_messages() %}{% if messages %}<div class="flash">{{ messages[0] }}</div>{% endif %}{% endwith %}
<form method="post"><input name="email" type="email" placeholder="Email" required>
<input name="password" type="password" placeholder="Mot de passe" required>
<button type="submit">S'inscrire</button></form>
<p>Déjà un compte? <a href="{{ url_for('login') }}">Se connecter</a></p></div></body></html>
"""

DASHBOARD = """
<!doctype html><html><head><title>TECH 2027 - Dashboard</title>
<style>body{font-family:sans-serif;background:#f0f2f5;margin:0}
header{background:linear-gradient(90deg,#0A2540,#1E90FF);color:white;padding:20px;text-align:center}
header h1{margin:0}header h1 span{color:#FF6A00}
.container{padding:20px;max-width:900px;margin:auto}
.logout{float:right;color:white;text-decoration:none;background:#FF6A00;padding:8px 15px;border-radius:5px}
</style></head>
<body><header><a href="/logout" class="logout">Déconnexion</a><h1>TECH<span>2027</span></h1></header>
<div class="container"><h2>Bienvenue {{ user.email }}</h2><p>Le site fonctionne! On ajoute les produits après.</p></div>
</body></html>
"""
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('login'))
    return render_template_string(DASHBOARD, user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('index'))
        else:
            flash('Email ou mot de passe incorrect')
    return render_template_string(LOGIN_PAGE)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if User.query.filter_by(email=email).first():
            flash('Cet email existe déjà')
            return redirect(url_for('register'))
        hashed_password = generate_password_hash(password)
        new_user = User(email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Inscription réussie! Connecte-toi')
        return redirect(url_for('login'))
    return render_template_string(REGISTER_PAGE)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
