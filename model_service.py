# model_service.py
from __future__ import annotations
import os
import numpy as np
import pandas as pd
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split

COLS_RENAME = {
    "DIAM": "diametre",
    "HAUTE": "hauteur",
    "PDS A F": "pds_af",
    "PDS A S": "pds_as",
    "PDS R F": "pds_rf",
    "PDS R S": "pds_rs",
    "NBR F": "nbr_f",
    "SF": "sf",
    "eau consommé par individue": "eau",
    "NO3- consommé par individue": "no3",
}

COLS_ALL = [
    "diametre", "hauteur", "eau", "no3",
    "pds_af", "pds_as", "pds_rf", "pds_rs",
    "nbr_f", "sf"
]

def make_model(seed: int = 42) -> XGBRegressor:
    return XGBRegressor(
        n_estimators=300,
        max_depth=3,
        learning_rate=0.05,
        subsample=0.9,
        colsample_bytree=0.9,
        objective="reg:squarederror",
        random_state=seed
    )

class CascadeModel:
    def __init__(self, excel_path: str):
        self.excel_path = excel_path
        self.model1 = self.model2 = self.model3 = None
        self.model4 = self.model5 = self.model6 = None
        self._train()

    def _load_data(self) -> pd.DataFrame:
        df = pd.read_excel(self.excel_path)
        df.columns = df.columns.str.strip()
        df = df.rename(columns=COLS_RENAME)

        missing = [c for c in COLS_ALL if c not in df.columns]
        if missing:
            raise ValueError(f"Colonnes manquantes : {missing}\nColonnes dispo : {list(df.columns)}")

        for c in COLS_ALL:
            df[c] = df[c].astype(str).str.strip().str.replace(",", ".", regex=False)
            df[c] = pd.to_numeric(df[c], errors="coerce")

        return df[COLS_ALL].dropna().reset_index(drop=True)

    def _train(self) -> None:
        df = self._load_data()
        idx = np.arange(len(df))
        train_idx, test_idx = train_test_split(idx, test_size=0.20, random_state=42)
        train = df.iloc[train_idx].copy()
        test = df.iloc[test_idx].copy()

        X1 = ["diametre", "hauteur", "eau", "no3"]
        self.model1 = make_model()
        self.model1.fit(train[X1], train["pds_af"])
        train["pds_af_pred"] = self.model1.predict(train[X1])
        test["pds_af_pred"] = self.model1.predict(test[X1])

        X2 = ["pds_af_pred", "diametre", "hauteur", "eau", "no3"]
        self.model2 = make_model()
        self.model2.fit(train[X2], train["pds_as"])
        train["pds_as_pred"] = self.model2.predict(train[X2])
        test["pds_as_pred"] = self.model2.predict(test[X2])

        X3 = ["pds_af_pred", "pds_as_pred", "diametre", "hauteur", "eau", "no3"]
        self.model3 = make_model()
        self.model3.fit(train[X3], train["pds_rf"])
        train["pds_rf_pred"] = self.model3.predict(train[X3])
        test["pds_rf_pred"] = self.model3.predict(test[X3])

        X4 = ["pds_af_pred", "pds_as_pred", "pds_rf_pred", "diametre", "hauteur", "eau", "no3"]
        self.model4 = make_model()
        self.model4.fit(train[X4], train["pds_rs"])
        train["pds_rs_pred"] = self.model4.predict(train[X4])
        test["pds_rs_pred"] = self.model4.predict(test[X4])

        X5 = ["pds_af_pred", "pds_as_pred", "pds_rf_pred", "pds_rs_pred",
              "diametre", "hauteur", "eau", "no3"]
        self.model5 = make_model()
        self.model5.fit(train[X5], train["nbr_f"])
        train["nbr_f_pred"] = self.model5.predict(train[X5])
        test["nbr_f_pred"] = self.model5.predict(test[X5])

        X6 = ["pds_af_pred", "pds_as_pred", "pds_rf_pred", "pds_rs_pred", "nbr_f_pred",
              "diametre", "hauteur", "eau", "no3"]
        self.model6 = make_model()
        self.model6.fit(train[X6], train["sf"])

    def predict(self, diametre: float, hauteur: float, eau: float, no3: float) -> dict:
        X = pd.DataFrame([{"diametre": float(diametre), "hauteur": float(hauteur),
                           "eau": float(eau), "no3": float(no3)}])

        pds_af = float(self.model1.predict(X[["diametre", "hauteur", "eau", "no3"]])[0])
        X["pds_af_pred"] = pds_af

        pds_as = float(self.model2.predict(X[["pds_af_pred", "diametre", "hauteur", "eau", "no3"]])[0])
        X["pds_as_pred"] = pds_as

        pds_rf = float(self.model3.predict(X[["pds_af_pred", "pds_as_pred", "diametre", "hauteur", "eau", "no3"]])[0])
        X["pds_rf_pred"] = pds_rf

        pds_rs = float(self.model4.predict(X[["pds_af_pred", "pds_as_pred", "pds_rf_pred",
                                              "diametre", "hauteur", "eau", "no3"]])[0])
        X["pds_rs_pred"] = pds_rs

        nbr_f = float(self.model5.predict(X[["pds_af_pred", "pds_as_pred", "pds_rf_pred", "pds_rs_pred",
                                             "diametre", "hauteur", "eau", "no3"]])[0])
        X["nbr_f_pred"] = nbr_f

        sf = float(self.model6.predict(X[["pds_af_pred", "pds_as_pred", "pds_rf_pred", "pds_rs_pred",
                                          "nbr_f_pred", "diametre", "hauteur", "eau", "no3"]])[0])

        return {"pds_af": pds_af, "pds_as": pds_as, "pds_rf": pds_rf, "pds_rs": pds_rs, "nbr_f": nbr_f, "sf": sf}

def build_default_model() -> CascadeModel:
    here = os.path.dirname(os.path.abspath(__file__))
    excel_path = os.path.join(here, "tableau_final_corrige_model_based.xlsx")
    return CascadeModel(excel_path=excel_path)
