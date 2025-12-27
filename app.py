# app.py
from __future__ import annotations
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

MODEL = None
MODEL_ERROR = None
NO3_DEFAULT = 0.5

def get_model():
    global MODEL, MODEL_ERROR
    if MODEL is not None or MODEL_ERROR is not None:
        return MODEL

    try:
        from model_service import build_default_model
        MODEL = build_default_model()
        return MODEL
    except Exception as e:
        MODEL_ERROR = str(e)
        return None

@app.get("/")
def index():
    return render_template("index.html")

@app.get("/plant")
def plant():
    return render_template("plant.html")

@app.get("/simulate")
def simulate():
    plant_name = request.args.get("plant", "basilic")
    return render_template("simulate.html", plant=plant_name)

@app.post("/predict")
def predict():
    model = get_model()
    if model is None:
        return jsonify({"error": f"Modèle non chargé: {MODEL_ERROR}"}), 500

    data = request.get_json(force=True) or {}
    try:
        eau = float(data.get("eau"))
        diametre = float(data.get("diametre"))
        hauteur = float(data.get("hauteur"))
    except Exception:
        return jsonify({"error": "Entrées invalides. Vérifie eau/diametre/hauteur."}), 400

    result = model.predict(diametre=diametre, hauteur=hauteur, eau=eau, no3=NO3_DEFAULT)
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
