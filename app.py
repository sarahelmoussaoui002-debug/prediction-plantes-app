from flask import Flask, render_template, request, jsonify
import os
import pandas as pd

# Si tu utilises model_service.py pour la prédiction
# (garde cet import si ton code l'utilise)
try:
    from model_service import predict_from_inputs
except Exception:
    predict_from_inputs = None

app = Flask(__name__)


@app.get("/")
def home():
    return render_template("index.html")


@app.post("/predict")
def predict():
    data = request.get_json(force=True)

    no3 = data.get("no3")
    eau = data.get("eau")
    diametre = data.get("diametre")
    hauteur = data.get("hauteur")

    # Si tu as un service modèle
    if predict_from_inputs:
        result = predict_from_inputs(no3, eau, diametre, hauteur)
        return jsonify({"prediction": result})

    # Sinon, réponse placeholder (à remplacer par ton code modèle)
    return jsonify({"prediction": "OK (branche modèle non connectée)"})


@app.get("/table")
def table():
    # Excel à la racine du projet (même niveau que app.py)
    excel_path = os.path.join(
        os.path.dirname(__file__),
        "tableau_final_corrige_model_based.xlsx"
    )

    if not os.path.exists(excel_path):
        return f"Fichier Excel introuvable: {excel_path}", 404

    df = pd.read_excel(excel_path)
    table_html = df.to_html(index=False, classes="data-table")

    return render_template("table.html", table_html=table_html)


if __name__ == "__main__":
    app.run(debug=True)
