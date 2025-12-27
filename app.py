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

# ===== PAGE 2 : TABLEAU / PRÉDICTION =====
@app.get("/tableau")
def tableau():
    return render_template("index.html")  # page avec formulaire + tableau/prédiction

# ===== API : PRÉDICTION =====
@app.post("/predict")
def predict():
    data = request.get_json(force=True) or {}

    def to_float(x):
        # accepte "12,3" ou "12.3" ou espaces
        return float(str(x).strip().replace(",", "."))

    try:
        diametre = to_float(data.get("diametre", ""))
        hauteur  = to_float(data.get("hauteur", ""))
        eau      = to_float(data.get("eau", ""))
        no3      = to_float(data.get("no3", ""))
    except (ValueError, TypeError):
        return jsonify({"error": "Entrées invalides. Mets uniquement des nombres."}), 400

    preds = cascade.predict(
        diametre=diametre,
        hauteur=hauteur,
        eau=eau,
        no3=no3
    )

    return jsonify(preds), 200


if __name__ == "__main__":
    app.run(debug=True)
