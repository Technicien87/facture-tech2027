from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tech2027_secret_key_change_moi'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///boutique.db'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# TABLE CLIENTS
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    nom = db.Column(db.String(100))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# PAGE ACCUEIL BOUTIQUE
@app.route('/')
def home():
    if current_user.is_authenticated:
        return f"""
        <h1>Bienvenue {current_user.nom}</h1>
        <p><a href='/logout'>Se déconnecter</a></p>
        <h2>TECH 2027 BOUTIQUE</h2>
        <p>Compte: {current_user.email}</p>
        <p><b>Produits bientôt disponibles...</b></p>
        """
    return redirect(url_for('login'))

# PAGE INSCRIPTION
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        nom = request.form['nom']
        
        if User.query.filter_by(email=email).first():
            return "Email déjà utilisé. <a href='/login'>Se connecter</a>"
        
        new_user = User(email=email, password=password, nom=nom)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    
    return '''
        <h2>Inscription TECH 2027</h2>
        <form method="post">
            Nom: <input name="nom" required><br><br>
            Email: <input name="email" type="email" required><br><br>
            Mot de passe: <input name="password" type="password" required><br><br>
            <input type="submit" value="Créer mon compte">
        </form>
        <p><a href="/login">Déjà un compte ? Se connecter</a></p>
    '''

# PAGE CONNEXION
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('home'))
        return "Email ou mot de passe incorrect. <a href='/login'>Réessayer</a>"
    
    return '''
        <h2>Connexion TECH 2027</h2>
        <form method="post">
            Email: <input name="email" type="email" required><br><br>
            Mot de passe: <input name="password" type="password" required><br><br>
            <input type="submit" value="Se connecter">
        </form>
        <p><a href="/register">Pas de compte ? S'inscrire</a></p>
    '''

# DECONNEXION
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

with app.app_context():
    db.create_all()

if __name == '__main__':
    app.run(debug=True)
