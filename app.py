from flask import Flask, render_template_string, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tech2027_secret_key_2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///boutique.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Produit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    prix = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(200))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

# TEMPLATE AVEC DESIGN TECH 2027
TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>TECH 2027 - Boutique</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Arial, sans-serif; 
            background: #f5f7fa; 
            color: #333;
        }
       .header {
            background: linear-gradient(135deg, #0066ff 0%, #0044cc 100%);
            color: white;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
       .header h1 { font-size: 28px; margin-bottom: 5px; }
       .header.user-info { 
            display: flex; 
            justify-content: space-between; 
            align-items: center;
            margin-top: 10px;
        }
       .header a { 
            color: #ff9900; 
            text-decoration: none; 
            font-weight: bold;
            background: rgba(255,255,255,0.2);
            padding: 8px 15px;
            border-radius: 5px;
        }
       .container { 
            max-width: 1200px; 
            margin: 30px auto; 
            padding: 0 20px;
        }
       .titre-section {
            font-size: 32px;
            margin-bottom: 20px;
            color: #0066ff;
            text-align: center;
        }
       .produits {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 25px;
        }
       .card {
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            transition: transform 0.3s, box-shadow 0.3s;
        }
       .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0,102,255,0.2);
        }
       .card h3 { 
            color: #0066ff; 
            font-size: 18px; 
            margin-bottom: 10px;
            min-height: 50px;
        }
       .card p { 
            color: #666; 
            font-size: 14px; 
            margin-bottom: 15px;
            min-height: 40px;
        }
       .prix {
            font-size: 26px;
            color: #ff6600;
            font-weight: bold;
            margin: 15px 0;
        }
       .btn {
            background: linear-gradient(135deg, #ff9900 0%, #ff6600 100%);
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
            font-size: 15px;
            width: 100%;
            transition: opacity 0.3s;
        }
       .btn:hover { opacity: 0.9; }
       .form-box {
            max-width: 400px;
            margin: 50px auto;
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
       .form-box h2 { 
            color: #0066ff; 
            margin-bottom: 20px;
text-align: center;
        }
       .form-box input {
            width: 100%;
            padding: 12px;
            margin: 8px 0 15px 0;
            border: 2px solid #ddd;
            border-radius: 6px;
            font-size: 14px;
        }
       .form-box input:focus {
            outline: none;
            border-color: #0066ff;
        }
       .logo {
            font-size: 36px;
            font-weight: 900;
            letter-spacing: -1px;
        }
       .logo span { color: #ff9900; }
    </style>
</head>
<body>
    {% if session.user_id %}
    <div class="header">
        <div class="logo">TECH <span>2027</span></div>
        <div class="user-info">
            <div>Bienvenue <b>{{ user.email.split('@')[0].upper() }}</b></div>
            <a href="/logout">Se déconnecter</a>
        </div>
    </div>
    <div class="container">
        <h2 class="titre-section">🛒 Nos Produits Tech</h2>
        <div class="produits">
            {% for p in produits %}
            <div class="card">
                <h3>{{ p.nom }}</h3>
                <p>{{ p.description }}</p>
                <div class="prix">{{ "{:,}".format(p.prix).replace(',', ' ') }} FCFA</div>
                <button class="btn">Ajouter au panier</button>
            </div>
            {% endfor %}
        </div>
    </div>
    {% else %}
    <div class="form-box">
        <div class="logo" style="text-align:center; margin-bottom:20px;">TECH <span>2027</span></div>
        {{ form_content | safe }}
    </div>
    {% endif %}
</body>
</html>
'''

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    produits = Produit.query.all()
    user = User.query.get(session['user_id'])
    return render_template_string(TEMPLATE, produits=produits, user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email, password=password).first()
        if user:
            session['user_id'] = user.id
            return redirect(url_for('index'))
        else:
            form = '''
            <h2>Connexion</h2>
            <p style="color:red;">Email ou mot de passe incorrect</p>
            <form method="POST">
                <input type="email" name="email" placeholder="Email" required>
                <input type="password" name="password" placeholder="Mot de passe" required>
                <input type="submit" value="Se connecter" class="btn">
            </form>
            <p style="text-align:center; margin-top:15px;">Pas de compte? <a href="/register" style="color:#0066ff;">S'inscrire</a></p>
            '''
            return render_template_string(TEMPLATE, form_content=form)
    
    form = '''
    <h2>Connexion</h2>
    <form method="POST">
        <input type="email" name="email" placeholder="Email" required>
        <input type="password" name="password" placeholder="Mot de passe" required>
        <input type="submit" value="Se connecter" class="btn">
    </form>
    <p style="text-align:center; margin-top:15px;">Pas de compte? <a href="/register" style="color:#0066ff;">S'inscrire</a></p>
    '''
    return render_template_string(TEMPLATE, form_content=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if User.query.filter_by(email=email).first():
            form = '''
            <h2>Inscription</h2>
            <p style="color:red;">Email déjà utilisé</p>
            <form method="POST">
                <input type="email" name="email" placeholder="Email" required>
                <input type="password" name="password" placeholder="Mot de passe" required>
<input type="submit" value="S'inscrire" class="btn">
            </form>
            <p style="text-align:center; margin-top:15px;">Déjà un compte? <a href="/login" style="color:#0066ff;">Se connecter</a></p>
            '''
            return render_template_string(TEMPLATE, form_content=form)
        new_user = User(email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    
    form = '''
    <h2>Inscription</h2>
    <form method="POST">
        <input type="email" name="email" placeholder="Email" required>
        <input type="password" name="password" placeholder="Mot de passe" required>
        <input type="submit" value="S'inscrire" class="btn">
    </form>
    <p style="text-align:center; margin-top:15px;">Déjà un compte? <a href="/login" style="color:#0066ff;">Se connecter</a></p>
    '''
    return render_template_string(TEMPLATE, form_content=form)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

with app.app_context():
    db.create_all()
    
    if User.query.filter_by(email='mikesery87@gmail.com').first() is None:
        admin = User(email='mikesery87@gmail.com', password='admin123')
        db.session.add(admin)
    
    if Produit.query.count() == 0:
        produits = [
            Produit(nom='Samsung Galaxy A16 (4/128 Go)', prix=115600, description='Smartphone Samsung 4 Go de RAM 128 Go de stockage'),
            Produit(nom='Redmi 15 (6 Go/128 Go 4G)', prix=78500, description='Xiaomi Redmi 6 Go de RAM, 128 Go de stockage, 4G'),
            Produit(nom='Ordinateur portable HP 15 (4 Go, 1 To, 15,6")', prix=209900, description='PC Portable HP 4 Go RAM 1 To Disque 15.6 pouces'),
            Produit(nom='Écouteur Bluetooth Pro', prix=10000, description='Écouteurs sans fil Bluetooth haute qualité son stéréo')
        ]
        db.session.add_all(produits)
    
    db.session.commit()
