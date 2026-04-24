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
    image = db.Column(db.String(200))

# TEMPLATES
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
<!doctype html><html><head><title>TECH 2027 - Boutique</title>
<style>body{font-family:sans-serif;background:#f0f2f5;margin:0}
header{background:linear-gradient(90deg,#0A2540,#1E90FF);color:white;padding:15px 20px;display:flex;justify-content:space-between;align-items:center}
header h1{margin:0;font-size:24px}header h1 span{color:#FF6A00}
.btn{color:white;text-decoration:none;background:#FF6A00;padding:8px 15px;border-radius:5px;margin-left:10px}
.container{padding:20px;max-width:1200px;margin:auto}

> Michael:
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:20px;margin-top:20px}
.card{background:white;border-radius:10px;padding:15px;box-shadow:0 2px 8px rgba(0,0,0,0.1);text-align:center}
.card img{width:100%;height:150px;object-fit:cover;border-radius:5px;background:#eee}
.card h3{margin:10px 0 5px;color:#0A2540}
.card.prix{color:#FF6A00;font-size:18px;font-weight:bold;margin:5px 0}
.card button{background:#1E90FF;color:white;border:none;padding:10px;width:100%;border-radius:5px;cursor:pointer;font-weight:bold}
.panier-count{background:red;color:white;border-radius:50%;padding:2px 6px;font-size:12px;margin-left:5px}
</style></head>
<body><header><h1>TECH<span>2027</span></h1><div>
<a href="{{ url_for('panier') }}" class="btn">Panier {% if panier_count > 0 %}<span class="panier-count">{{ panier_count }}</span>{% endif %}</a>
<a href="/logout" class="btn">Déconnexion</a></div></header>
<div class="container"><h2>Bienvenue {{ user.email }}</h2>
<div class="grid">
{% for p in produits %}
<div class="card">
<img src="{{ p.image or 'https://via.placeholder.com/250x150/0A2540/FFFFFF?text=TECH2027' }}" alt="{{ p.nom }}">
<h3>{{ p.nom }}</h3><div class="prix">{{ "%.0f"|format(p.prix) }} FCFA</div>
<form method="post" action="{{ url_for('add_panier', produit_id=p.id) }}"><button type="submit">Ajouter au panier</button></form>
</div>
{% endfor %}
</div></div></body></html>
"""

PANIER_PAGE = """
<!doctype html><html><head><title>TECH 2027 - Panier</title>
<style>body{font-family:sans-serif;background:#f0f2f5;margin:0}
header{background:linear-gradient(90deg,#0A2540,#1E90FF);color:white;padding:15px 20px}
header h1{margin:0}header h1 span{color:#FF6A00}
.btn{color:white;text-decoration:none;background:#FF6A00;padding:8px 15px;border-radius:5px}
.container{padding:20px;max-width:800px;margin:auto;background:white;margin-top:20px;border-radius:10px}
table{width:100%;border-collapse:collapse}th,td{padding:12px;text-align:left;border-bottom:1px solid #ddd}
.total{font-size:20px;font-weight:bold;text-align:right;margin-top:20px;color:#0A2540}
.actions{margin-top:20px;text-align:right}
</style></head>
<body><header><h1>TECH<span>2027</span> - Panier</h1></header>
<div class="container">
{% if panier_items %}
<table><tr><th>Produit</th><th>Prix</th><th>Quantité</th><th>Sous-total</th></tr>
{% for item in panier_items %}
<tr><td>{{ item.nom }}</td><td>{{ "%.0f"|format(item.prix) }} FCFA</td><td>{{ item.qte }}</td><td>{{ "%.0f"|format(item.prix * item.qte) }} FCFA</td></tr>
{% endfor %}</table>
<div class="total">Total: {{ "%.0f"|format(total) }} FCFA</div>
<div class="actions"><a href="/" class="btn">Continuer achats</a></div>
{% else %}<p>Ton panier est vide.</p><a href="/" class="btn">Voir les produits</a>{% endif %}
</div></body></html>
"""

# ROUTES
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('login'))
    
    produits = Produit.query.all()
    panier = session.get('panier', {})
    panier_count = sum(panier.values())
    return render_template_string(DASHBOARD, user=user, produits=produits, panier_count=panier_count)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['panier'] = {}
            return redirect(url_for('index'))
        else:
            flash('Email ou mot de passe incorrect')
    return render_template_string(LOGIN_PAGE)

> Michael:
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

@app.route('/add_panier/<int:produit_id>', methods=['POST'])
def add_panier(produit_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    panier = session.get('panier', {})
    panier[str(produit_id)] = panier.get(str(produit_id), 0) + 1
    session['panier'] = panier
    return redirect(url_for('index'))

@app.route('/panier')
def panier():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    panier = session.get('panier', {})
    panier_items = []
    total = 0
    for pid, qte in panier.items():
        p = Produit.query.get(int(pid))
        if p:
            panier_items.append({'nom': p.nom, 'prix': p.prix, 'qte': qte})
            total += p.prix * qte
    return render_template_string(PANIER_PAGE, user=user, panier_items=panier_items, total=total)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# CREER DB + PRODUITS DE TEST
with app.app_context():
    db.create_all()
    if Produit.query.count() == 0:
        db.session.add_all([
            Produit(nom='iPhone 15 Pro', prix=750000, image='https://images.unsplash.com/photo-1695048133142-1a20484d256a?w=400'),
            Produit(nom='MacBook Air M3', prix=950000, image='https://images.unsplash.com/photo-1611186871348-b1ce696e52c9?w=400'),
            Produit(nom='AirPods Pro 2', prix=180000, image='https://images.unsplash.com/photo-1600294037681-c80b4cb5b434?w=400'),
            Produit(nom='Samsung S24 Ultra', prix=720000, image='https://images.unsplash.com/photo-1706600796603-4a457f60f03f?w=400')
        ])
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)
