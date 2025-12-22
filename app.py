# app.py
from flask import Flask, render_template, request, jsonify
from model_service import build_default_model

app = Flask(__name__)

cascade = build_default_model()  # entraîne les modèles au démarrage

@app.get("/")
def home():
    return render_template("index.html")

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

    preds = cascade.predict(diametre=diametre, hauteur=hauteur, eau=eau, no3=no3)
    return jsonify(preds)

if __name__ == "__main__":
    app.run(debug=True)
