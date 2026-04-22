from flask import Flask, render_template_string, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tech2027_secret_key_2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///boutique.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# MODELE PRODUIT - DOIT ÊTRE AVANT LE RESTE
class Produit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    prix = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(200))

# MODELE USER
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    produits = Produit.query.all()
    user = User.query.get(session['user_id'])
    
    html = '''
    <h1>Bienvenue {{ user.email.split('@')[0].upper() }}</h1>
    <a href="/logout">Se déconnecter</a>
    <h2>TECH 2027 BOUTIQUE</h2>
    <p>Compte: {{ user.email }}</p>
    <hr>
    {% if produits %}
        {% for p in produits %}
            <div style="border:1px solid #ccc; padding:10px; margin:10px;">
                <h3>{{ p.nom }}</h3>
                <p>{{ p.description }}</p>
                <b>{{ p.prix }} FCFA</b><br><br>
                <button>Ajouter au panier</button>
            </div>
        {% endfor %}
    {% else %}
        <b>Produits bientôt disponibles...</b>
    {% endif %}
    '''
    return render_template_string(html, produits=produits, user=user)

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
            return 'Email ou mot de passe incorrect <a href="/login">Réessayer</a>'
    
    return '''
    <h2>Connexion TECH 2027</h2>
    <form method="POST">
        Email: <input type="email" name="email" required><br><br>
        Mot de passe: <input type="password" name="password" required><br><br>
        <input type="submit" value="Se connecter">
    </form>
    <p>Pas de compte? <a href="/register">S'inscrire</a></p>
    '''

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if User.query.filter_by(email=email).first():
            return 'Email déjà utilisé <a href="/register">Réessayer</a>'
        new_user = User(email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    
    return '''
    <h2>Inscription TECH 2027</h2>
    <form method="POST">
        Email: <input type="email" name="email" required><br><br>
        Mot de passe: <input type="password" name="password" required><br><br>
        <input type="submit" value="S'inscrire">
    </form>
    <p>Déjà un compte? <a href="/login">Se connecter</a></p>
    '''

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

# CREATION DB + TES 4 PRODUITS
with app.app_context():
    db.create_all()
    if Produit.query.count() == 0:
        produits = [
            Produit(nom='Samsung Galaxy A16 (4/128 Go)', prix=115600, description='Smartphone Samsung 4Go RAM 128Go Stockage'),
            Produit(nom='Redmi 15 (6Go/128Go 4G)', prix=78500, description='Xiaomi Redmi 6Go RAM 128Go 4G'),
            Produit(nom='HP Notebook 15 (4GB, 1TB, 15.6")', prix=209900, description='PC Portable HP 4Go RAM 1To Disque 15.6 pouces'),
            Produit(nom='Écouteur Bluetooth Pro', prix=10000, description='Écouteurs sans fil Bluetooth haute qualité')
        ]
        db.session.add_all(produits)
        db.session.commit()
