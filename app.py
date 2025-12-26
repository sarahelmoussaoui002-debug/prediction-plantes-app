# app.py
from flask import Flask, render_template, request, jsonify
from model_service import build_default_model

app = Flask(__name__)

# Entraînement / chargement du modèle au démarrage
cascade = build_default_model()

# ===== PAGE 1 : ACCUEIL =====
@app.get("/")
def home():
    return render_template("home.html")

# ===== PAGE 2 : TABLEAU / CARTE =====
@app.get("/tableau")
def tableau():
    return render_template("index.html")

# ===== API : PRÉDICTION =====
@app.post("/predict")
def predict():
    data = request.get_json(force=True) or {}
    try:
        diametre = float(str(data.get("diametre", "")).replace(",", "."))
        hauteur  = float(str(data.get("hauteur", "")).replace(",", "."))
        eau      = float(str(data.get("eau", "")).replace(",", "."))
        no3      = float(str(data.get("no3", "")).replace(",", "."))
    except ValueError:
        return jsonify({"error": "Entrées invalides. Mets uniquement des nombres."}), 400

    preds = cascade.predict(
        diametre=diametre,
        hauteur=hauteur,
        eau=eau,
        no3=no3
    )
    return jsonify(preds)

if __name__ == "__main__":
    app.run(debug=True)
