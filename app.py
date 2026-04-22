from flask import Flask, request

app = Flask(__name__)

# Tes services et prix de TECH 2027
SERVICES = {
    "Formatage": 20000,
    "Réparation Écran": 45000,
    "Installation Windows": 10000,
    "Récupération Données": 35000,
    "Nettoyage Virus": 15000,
    "Formation Python": 50000
}

STYLE = """
<style>
    body { font-family: Arial; background: #f0f4f8; padding: 30px; }
   .cadre { 
        background: white; max-width: 500px; margin: auto; padding: 30px; 
        border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
    h1 { color: #0052cc; text-align: center; border-bottom: 3px solid #ff8c00; padding-bottom: 10px; }
    input, select { 
        width: 100%; padding: 10px; margin: 8px 0; border: 2px solid #ddd; 
        border-radius: 5px; box-sizing: border-box; font-size: 16px;
    }
    button { 
        background: #0052cc; color: white; padding: 12px; width: 100%; 
        border: none; border-radius: 5px; font-size: 16px; font-weight: bold; cursor: pointer; 
        margin-top: 10px;
    }
    button:hover { background: #ff8c00; }
   .btn-imprimer { background: #28a745; }
   .btn-imprimer:hover { background: #218838; }
   .facture p { font-size: 18px; line-height: 1.6; }
   .btn-retour { 
        display: inline-block; margin-top: 20px; color: #0052cc; 
        text-decoration: none; font-weight: bold;
    }
    @media print {
       .btn-imprimer,.btn-retour { display: none; }
        body { background: white; }
    }
</style>
"""

# JavaScript pour mettre le prix auto
SCRIPT = """
<script>
    function mettre_prix() {
        const service = document.getElementById('service').value;
        const prix = document.getElementById('prix');
        const tarifs = %s;
        prix.value = tarifs[service] || '';
    }
</script>
""" % str(SERVICES).replace("'", '"')

def generer_facture_web(nom_client, service, prix):
    return f"""
    {STYLE}
    <div class="cadre facture">
        <h1>TECHNOLOGIE D'USINE 2027</h1>
        <p><b>Client :</b> {nom_client}</p>
        <p><b>Service :</b> {service}</p>
        <p><b>Prix :</b> {prix} FCFA</p>
        <hr>
        <p><b>Technicien :</b> Michael Yohoua</p>
        <p><b>Contact :</b> +225 05 94 66 56 80</p>
        <h3 style="text-align:center; color:#ff8c00;">Merci et à bientôt!</h3>
        <button class="btn-imprimer" onclick="window.print()">IMPRIMER EN PDF</button>
        <br><a href="/" class="btn-retour">← Faire une autre facture</a>
    </div>
    """

@app.route("/", methods=["GET", "POST"])
def formulaire():
    if request.method == "POST":
        client = request.form["client"]
        service = request.form["service"]
        prix = request.form["prix"]
        return generer_facture_web(client, service, prix)
    
    # On crée les options du menu déroulant
    options = "".join([f'<option value="{s}">{s} - {p} FCFA</option>' for s, p in SERVICES.items()])
    
    return f'''
        {STYLE}
        {SCRIPT}
        <div class="cadre">
            <h1>TECH 2027 - Générateur de Facture</h1>
            <form method="POST">
                <label><b>Nom du client :</b></label>
                <input type="text" name="client" required>
                
                <label><b>Service rendu :</b></label>
                <select id="service" name="service" onchange="mettre_prix()" required>
                    <option value="">-- Choisis un service --</option>
                    {options}
                </select>
                
                <label><b>Prix FCFA :</b></label>
                <input type="number" id="prix" name="prix" required>
                
                <button type="submit">GÉNÉRER LA FACTURE</button>
            </form>
        </div>
    '''

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
                