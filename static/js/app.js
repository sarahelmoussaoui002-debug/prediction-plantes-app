function lancer() {
  document.getElementById("resultat").textContent = "Calcul en cours...";

  fetch("/predict", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      no3: document.getElementById("no3").value,
      eau: document.getElementById("eau").value,
      diametre: document.getElementById("diametre").value,
      hauteur: document.getElementById("hauteur").value
    })
  })
  .then(response => response.json())
  .then(data => {
    document.getElementById("resultat").textContent =
      "PDS A F : " + data.pds_af + "\n" +
      "PDS A S : " + data.pds_as + "\n" +
      "PDS R F : " + data.pds_rf + "\n" +
      "PDS R S : " + data.pds_rs + "\n" +
      "NBR F   : " + data.nbr_f + "\n" +
      "SF      : " + data.sf;
  })
  .catch(() => {
    document.getElementById("resultat").textContent =
      "Erreur : le modèle n’a pas répondu.";
  });
}
