from flask import Flask, request, redirect, url_for, session, flash, render_template_string
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tech2027-v2-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tech2027.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# MODELES
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    nom = db.Column(db.String(100), default='')
    adresse = db.Column(db.String(200), default='')
    telephone = db.Column(db.String(20), default='')

class Categorie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    icone = db.Column(db.String(50), default='📦')

class Produit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    prix = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(300))
    categorie_id = db.Column(db.Integer, db.ForeignKey('categorie.id'))
    stock = db.Column(db.Integer, default=10)
    description = db.Column(db.Text, default='')

class Commande(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    total = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    statut = db.Column(db.String(50), default='En cours')

# TEMPLATES
BASE_STYLE = """
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Segoe UI',sans-serif;background:#f5f5f5}
header{background:linear-gradient(90deg,#0A2540,#1E90FF);color:white;padding:12px 20px;position:sticky;top:0;z-index:100}
.topbar{display:flex;justify-content:space-between;align-items:center;max-width:1400px;margin:auto}
.logo{font-size:24px;font-weight:bold}.logo span{color:#FF6A00}
.search{flex:1;max-width:500px;margin:0 20px}.search input{width:100%;padding:10px;border-radius:5px;border:none}
.nav-btns a{color:white;text-decoration:none;background:#FF6A00;padding:8px 15px;border-radius:5px;margin-left:8px;font-size:14px}
.nav-btns.panier-count{background:red;color:white;border-radius:50%;padding:2px 6px;font-size:11px;margin-left:3px}
.container{max-width:1400px;margin:20px auto;padding:0 20px;display:flex;gap:20px}
.sidebar{width:250px;background:white;border-radius:10px;padding:15px;height:fit-content;box-shadow:0 2px 8px rgba(0,0,0,0.1)}
.sidebar h3{color:#0A2540;margin-bottom:10px;font-size:16px}
.sidebar a{display:block;padding:10px;color:#333;text-decoration:none;border-radius:5px;margin:5px 0}
.sidebar a:hover{background:#f0f2f5;color:#1E90FF}
.main{flex:1}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:15px}
.card{background:white;border-radius:10px;padding:12px;box-shadow:0 2px 8px rgba(0,0,0,0.1);transition:0.3s}
.card:hover{transform:translateY(-5px);box-shadow:0 4px 12px rgba(0,0,0,0.15)}
.card img{width:100%;height:180px;object-fit:cover;border-radius:8px;background:#eee}
.card h4{margin:8px 0 4px;color:#0A2540;font-size:15px;height:40px}
.card.prix{color:#FF6A00;font-size:18px;font-weight:bold;margin:5px 0}
.card button{background:#1E90FF;color:white;border:none;padding:10px;width:100%;border-radius:5px;cursor:pointer;font-weight:bold}
.card button:hover{background:#0A2540}
.box{background:white;padding:30px;border-radius:10px;box-shadow:0 2px 8px rgba(0,0,0,0.1);max-width:500px;margin:50px auto}
.box h2{color:#1E90FF;margin-bottom:20px;text-align:center}
.box input,.box textarea{width:100%;padding:12px;margin:8px 0;border:1px solid #ddd;border-radius:5px}

.box button{width:100%;padding:12px;background:#FF6A00;color:white;border:none;border-radius:5px;font-weight:bold;cursor:pointer}
.flash{color:red;margin-bottom:10px;text-align:center}
table{width:100%;background:white;border-radius:10px;overflow:hidden}
th,td{padding:12px;text-align:left}th{background:#0A2540;color:white}
tr:nth-child(even){background:#f9f9f9}
</style>
"""

LOGIN_PAGE = """<!doctype html><html><head><link rel="manifest" href="/manifest.json"><meta name="theme-color" content="#1E90FF"><title>TECH 2027</title>"""+BASE_STYLE+"""</head><body><div class="box"><h1 class="logo">TECH<span>2027</span></h1><h2>Connexion</h2>{% with messages = get_flashed_messages() %}{% if messages %}<div class="flash">{{ messages[0] }}</div>{% endif %}{% endwith %}<form method="post"><input name="email" type="email" placeholder="Email" required><input name="password" type="password" placeholder="Mot de passe" required><button type="submit">Se connecter</button></form><p style="text-align:center;margin-top:15px">Pas de compte? <a href="{{ url_for('register') }}" style="color:#1E90FF">S'inscrire</a></p></div></body></html>"""<form method="post"><input name="email" type="email" placeholder="Email" required><input name="password" type="password" placeholder="Mot de passe" required><button type="submit">Se connecter</button></form><p style="text-align:center;margin-top:15px">Pas de compte? <a href="{{ url_for('register') }}" style="color:#1E90FF">S'inscrire</a></p></div></body></html>"""

REGISTER_PAGE = """<!doctype html><html><head><title>TECH 2027</title>"""+BASE_STYLE+"""</head><body>
<div class="box"><h1 class="logo">TECH<span>2027</span></h1><h2>Inscription</h2>
{% with messages = get_flashed_messages() %}{% if messages %}<div class="flash">{{ messages[0] }}</div>{% endif %}{% endwith %}
<form method="post"><input name="email" type="email" placeholder="Email" required>
<input name="password" type="password" placeholder="Mot de passe" required>
<button type="submit">S'inscrire</button></form>
<p style="text-align:center;margin-top:15px">Déjà un compte? <a href="{{ url_for('login') }}" style="color:#1E90FF">Se connecter</a></p></div></body></html>"""

DASHBOARD = """<!doctype html><html><head><title>TECH 2027 - Boutique</title>"""+BASE_STYLE+"""</head><body>
<header><div class="topbar"><div class="logo">TECH<span>2027</span></div>
<div class="search"><input type="text" placeholder="Rechercher un produit..."></div>
<div class="nav-btns">
<a href="{{ url_for('profil') }}">👤 Profil</a>
<a href="{{ url_for('commandes') }}">📦 Commandes</a>
<a href="{{ url_for('panier') }}">🛒 Panier {% if panier_count > 0 %}<span class="panier-count">{{ panier_count }}</span>{% endif %}</a>
<a href="/logout">Déconnexion</a></div></div></header>
<div class="container">
<div class="sidebar"><h3>Catégories</h3>
<a href="/?cat=all">🌟 Tous les produits</a>
{% for cat in categories %}<a href="/?cat={{ cat.id }}">{{ cat.icone }} {{ cat.nom }}</a>{% endfor %}
{% if user.email == 'admin@tech2027.com' %}<hr><a href="{{ url_for('admin') }}" style="color:#FF6A00">⚙️ Admin</a>{% endif %}
</div>
<div class="main"><h2 style="margin-bottom:15px;color:#0A2540">{{ titre_cat }}</h2><div class="grid">
{% for p in produits %}<div class="card">
<img src="{{ p.image or 'https://via.placeholder.com/250x180/0A2540/FFFFFF?text=TECH2027' }}">
<h4>{{ p.nom }}</h4><div class="prix">{{ "%.0f"|format(p.prix) }} FCFA</div>
<div style="font-size:12px;color:#666;margin:5px 0">Stock: {{ p.stock }}</div>
<form method="post" action="{{ url_for('add_panier', produit_id=p.id) }}"><button type="submit">Ajouter au panier</button></form>
</div>{% endfor %}</div></div></div></body></html>"""

PANIER_PAGE = """<!doctype html><html><head><title>TECH 2027 - Panier</title>"""+BASE_STYLE+"""</head><body>
<header><div class="topbar"><div class="logo">TECH<span>2027</span></div>
<div class="nav-btns"><a href="/">🏠 Accueil</a><a href="{{ url_for('profil') }}">👤 Profil</a></div></div></header>
<div class="container"><div class="main" style="width:100%">
<h2 style="margin-bottom:15px">Mon Panier</h2>
{% if panier_items %}
<table><tr><th>Produit</th><th>Prix</th><th>Qté</th><th>Sous-total</th><th></th></tr>
{% for item in panier_items %}<tr>
<td>{{ item.nom }}</td><td>{{ "%.0f"|format(item.prix) }} FCFA</td><td>{{ item.qte }}</td>

<td>{{ "%.0f"|format(item.prix * item.qte) }} FCFA</td>
<td><a href="{{ url_for('del_panier', produit_id=item.id) }}" style="color:red">Retirer</a></td></tr>{% endfor %}
</table><div style="text-align:right;margin-top:20px;font-size:22px;font-weight:bold;color:#0A2540">Total: {{ "%.0f"|format(total) }} FCFA</div>
<div style="text-align:right;margin-top:20px">
<a href="{{ url_for('commander') }}" style="background:#25D366;color:white;padding:12px 25px;border-radius:5px;text-decoration:none;font-weight:bold">💬 Commander via WhatsApp</a>
</div>
{% else %}<div class="box" style="margin:20px 0"><p style="text-align:center">Ton panier est vide.</p><a href="/" class="box button">Voir les produits</a></div>{% endif %}
</div></div></body></html>"""

PROFIL_PAGE = """<!doctype html><html><head><title>TECH 2027 - Profil</title>"""+BASE_STYLE+"""</head><body>
<header><div class="topbar"><div class="logo">TECH<span>2027</span></div>
<div class="nav-btns"><a href="/">🏠 Accueil</a><a href="{{ url_for('panier') }}">🛒 Panier</a></div></div></header>
<div class="box"><h2>Mon Profil</h2>
{% with messages = get_flashed_messages() %}{% if messages %}<div class="flash" style="color:green">{{ messages[0] }}</div>{% endif %}{% endwith %}
<form method="post"><input name="nom" placeholder="Nom complet" value="{{ user.nom }}">
<input name="email" type="email" value="{{ user.email }}" disabled>
<input name="telephone" placeholder="Téléphone Wave/OM" value="{{ user.telephone }}">
<textarea name="adresse" placeholder="Adresse de livraison">{{ user.adresse }}</textarea>
<button type="submit">Enregistrer</button></form></div></body></html>"""

ADMIN_PAGE = """<!doctype html><html><head><title>TECH 2027 - Admin</title>"""+BASE_STYLE+"""</head><body>
<header><div class="topbar"><div class="logo">TECH<span>2027</span> Admin</div>
<div class="nav-btns"><a href="/">🏠 Voir Site</a><a href="/logout">Déconnexion</a></div></div></header>
<div class="box" style="max-width:800px"><h2>Ajouter un Produit</h2>
<form method="post" action="{{ url_for('admin_add') }}">
<input name="nom" placeholder="Nom du produit" required>
<input name="prix" type="number" placeholder="Prix FCFA" required>
<input name="image" placeholder="URL Image" required>
<select name="categorie_id" style="width:100%;padding:12px;margin:8px 0;border:1px solid #ddd;border-radius:5px">
{% for cat in categories %}<option value="{{ cat.id }}">{{ cat.nom }}</option>{% endfor %}</select>
<input name="stock" type="number" placeholder="Stock" value="10">
<textarea name="description" placeholder="Description"></textarea>
<button type="submit">Ajouter Produit</button></form></div></body></html>"""

# ROUTES
@app.route('/')
def index():
    if 'user_id' not in session: return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if not user: session.clear(); return redirect(url_for('login'))

    cat_id = request.args.get('cat', 'all')
    categories = Categorie.query.all()
    if cat_id == 'all':
        produits = Produit.query.all()
        titre_cat = "Tous les produits"
    else:
        produits = Produit.query.filter_by(categorie_id=int(cat_id)).all()
        cat = Categorie.query.get(int(cat_id))
        titre_cat = cat.nom if cat else "Produits"

    panier = session.get('panier', {})
    panier_count = sum(panier.values())
    return render_template_string(DASHBOARD, user=user, produits=produits, categories=categories, panier_count=panier_count, titre_cat=titre_cat)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user and check_password_hash(user.password, request.form['password']):
            session['user_id'] = user.id
            session['panier'] = {}
            return redirect(url_for('index'))
        flash('Email ou mot de passe incorrect')
    return render_template_string(LOGIN_PAGE)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if User.query.filter_by(email=request.form['email']).first():
            flash('Cet email existe déjà'); return redirect(url_for('register'))
        new_user = User(email=request.form['email'], password=generate_password_hash(request.form['password']))
        db.session.add(new_user); db.session.commit()
        flash('Inscription réussie! Connecte-toi'); return redirect(url_for('login'))
    return render_template_string(REGISTER_PAGE)

@app.route('/add_panier/<int:produit_id>', methods=['POST'])
def add_panier(produit_id):
    if 'user_id' not in session: return redirect(url_for('login'))
    panier = session.get('panier', {})
    panier[str(produit_id)] = panier.get(str(produit_id), 0) + 1
    session['panier'] = panier
    return redirect(request.referrer or url_for('index'))

@app.route('/del_panier/<int:produit_id>')
def del_panier(produit_id):
    panier = session.get('panier', {})
    panier.pop(str(produit_id), None)
    session['panier'] = panier
    return redirect(url_for('panier'))

@app.route('/panier')
def panier():
    if 'user_id' not in session: return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    panier = session.get('panier', {})
    panier_items = []
    total = 0
    for pid, qte in panier.items():
        p = Produit.query.get(int(pid))
        if p:
            panier_items.append({'id': p.id, 'nom': p.nom, 'prix': p.prix, 'qte': qte})
            total += p.prix * qte
    return render_template_string(PANIER_PAGE, user=user, panier_items=panier_items, total=total)

@app.route('/profil', methods=['GET', 'POST'])
def profil():
    if 'user_id' not in session: return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        user.nom = request.form['nom']
        user.telephone = request.form['telephone']
        user.adresse = request.form['adresse']
        db.session.commit()
        flash('Profil mis à jour!')
    return render_template_string(PROFIL_PAGE, user=user)

@app.route('/commander')
def commander():
    if 'user_id' not in session: return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    panier = session.get('panier', {})
    if not panier: return redirect(url_for('panier'))

    total = 0
    msg = "Bonjour TECH2027! Je veux commander:%0A"
    for pid, qte in panier.items():
        p = Produit.query.get(int(pid))
        if p:
            msg += f"- {p.nom} x{qte} = {int(p.prix*qte)} FCFA%0A"
            total += p.prix * qte
    msg += f"%0ATotal: {int(total)} FCFA%0ANom: {user.nom}%0ATel: {user.telephone}%0AAdresse: {user.adresse}"

    new_cmd = Commande(user_id=user.id, total=total)
    db.session.add(new_cmd); db.session.commit()
    session['panier'] = {}

    # Remplace 225XXXXXXXX par ton numero WhatsApp
    return redirect(f"https://wa.me/2250700000000?text={msg}")

@app.route('/commandes')
def commandes():
    if 'user_id' not in session: return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    cmds = Commande.query.filter_by(user_id=user.id).order_by(Commande.date.desc()).all()
    html = BASE_STYLE + "<header><div class='topbar'><div class='logo'>TECH<span>2027</span></div><div class='nav-btns'><a href='/'>🏠 Accueil</a></div></div></header>"
    html += "<div class='container'><div class='main' style='width:100%'><h2>Mes Commandes</h2><table><tr><th>ID</th><th>Date</th><th>Total</th><th>Statut</th></tr>"
    for c in cmds: html += f"<tr><td>#{c.id}</td><td>{c.date.strftime('%d/%m/%Y')}</td><td>{int(c.total)} FCFA</td><td>{c.statut}</td></tr>"
    html += "</table></div></div>"
    return html

@app.route('/admin')
def admin():
    if 'user_id' not in session: return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if user.email!= 'admin@tech2027.com': return "Accès refusé", 403
    categories = Categorie.query.all()
    return render_template_string(ADMIN_PAGE, categories=categories)

@app.route('/admin/add', methods=['POST'])
def admin_add():
    if 'user_id' not in session: return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if user.email!= 'admin@tech2027.com': return "Accès refusé", 403
    new_p = Produit(nom=request.form['nom'], prix=float(request.form['prix']), image=request.form['image'],
                    categorie_id=int(request.form['categorie_id']), stock=int(request.form['stock']), description=request.form['description'])
    db.session.add(new_p); db.session.commit()
    return redirect(url_for('admin'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# INIT DB
with app.app_context():
    db.create_all()
    if Categorie.query.count() == 0:
        cats = [
            Categorie(nom='Téléphones', icone='📱'),
            Categorie(nom='Ordinateurs', icone='💻'),
            Categorie(nom='Électroménager', icone='🏠'),
            Categorie(nom='Mode & Sacs', icone='👜'),
            Categorie(nom='Audio', icone='🎧')
        ]
        db.session.add_all(cats); db.session.commit()

        prods = [
            Produit(nom='iPhone 15 Pro 256Go', prix=750000, image='https://images.unsplash.com/photo-1695048133142-1a20484d256a?w=400', categorie_id=1),
            Produit(nom='Samsung S24 Ultra', prix=720000, image='https://images.unsplash.com/photo-1706600796603-4a457f60f03f?w=400', categorie_id=1),
            Produit(nom='MacBook Air M3 13"', prix=950000, image='https://images.unsplash.com/photo-1611186871348-b1ce696e52c9?w=400', categorie_id=2),
            Produit(nom='HP Pavilion i5', prix=450000, image='https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400', categorie_id=2),
            Produit(nom='Congélateur 300L Hisense', prix=280000, image='https://images.unsplash.com/photo-1571175443880-49e1d25b2bc5?w=400', categorie_id=3),
            Produit(nom='Mixeur Moulinex 500W', prix=35000, image='https://images.unsplash.com/photo-1570222094114-d054a817e56b?w=400', categorie_id=3),
            Produit(nom='Machine à Laver LG 8Kg', prix=320000, image='https://images.unsplash.com/photo-1626806787461-102c1bfaaea1?w=400', categorie_id=3),
            Produit(nom='Sac à Dos Nike', prix=25000, image='https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=400', categorie_id=4),
            Produit(nom='Sac à Main Cuir Femme', prix=45000, image='https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=400', categorie_id=4),
            Produit(nom='AirPods Pro 2', prix=180000, image='https://images.unsplash.com/photo-1600294037681-c80b4cb5b434?w=400', categorie_id=5),
            Produit(nom='Casque JBL Bluetooth', prix=65000, image='https://images.unsplash.com/photo-1545127398-14699f92334b?w=400', categorie_id=5),
            Produit(nom='TV Samsung 55" 4K', prix=420000, image='https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?w=400', categorie_id=3),
        ]
        db.session.add_all(prods); db.session.commit()
@app.route('/manifest.json')
def manifest():
    return {
        "name": "TECH2027",
        "short_name": "TECH2027",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#0A2540",
        "theme_color": "#1E90FF",
        "description": "La boutique e-commerce TECH2027",
        "icons": [
            {
                "src": "https://cdn-icons-png.flaticon.com/512/891419.png",
                "sizes": "512x512",
                "type": "image/png"
            }
        ]
    }

@app.route('/sw.js')
def service_worker():
    return '''
    self.addEventListener('install', function(e) {
      e.waitUntil(caches.open('tech2027').then(function(cache) {
        return cache.addAll(['/']);
      }));
    });
    self.addEventListener('fetch', function(e) {
      e.respondWith(fetch(e.request).catch(() => caches.match(e.request)));
    });
    ''', 200, {'Content-Type': 'application/javascript'}

@app.route('/manifest.json')
def manifest():
    return '''{
  "name": "TECH2027 Facture",
  "short_name": "TECH2027",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#121212",
  "theme_color": "#1E90FF",
  "icons": []
}''', 200, {'Content-Type': 'application/manifest+json'}

if __name__ == '__main__':
    app.run(debug=True)
