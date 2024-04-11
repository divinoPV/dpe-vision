from typing import Tuple
from typing_extensions import Annotated

import joblib
import numpy as np
import pandas as pd

from zenml import pipeline, step


@step
def data_val_load() -> Annotated[pd.DataFrame, "data_val"]:
    return pd.read_csv('data/val.csv')


@step
def data_clean_pred(
    data_val: pd.DataFrame = None,
) -> Tuple[
    Annotated[pd.DataFrame, "data_val"],
    Annotated[pd.Series, "data_val_Id"],
]:
    correspondance = {'très bonne':4, 'insuffisante':1, 'bonne':3, 'moyenne':2, 0:0, 'appartement':1, 'maison':2, 'immeuble':3, 'A':6, 'B':5,
                    'C':4, 'D':3, 'E':2, 'F':1, 'G':0, 'Électricité':1, 'Bois – Bûches':2, 'GPL':3, 'Gaz naturel':4,'Fioul domestique':5,
                    'Réseau de Chauffage urbain':6,'Bois – Granulés (pellets) ou briquettes':7,"Électricité d'origine renouvelable utilisée dans le bâtiment":8,
                    'Bois – Plaquettes d’industrie':9, 'Bois – Plaquettes forestières':10,'Charbon':11, 'Propane':12, 'Butane':13, 'Réseau de Froid Urbain':14}

    colonnes_a_transformer_val = ['Qualité_isolation_plancher_bas', 'Qualité_isolation_enveloppe', 'Qualité_isolation_menuiseries',
                            'Qualité_isolation_murs', 'Qualité_isolation_plancher_haut_comble_aménagé','Qualité_isolation_plancher_haut_comble_perdu',
                            'Qualité_isolation_plancher_haut_toit_terrase', 'Type_bâtiment', 'Etiquette_GES', 'Type_énergie_n°3']

    data_val = data_val.fillna(0)
    data_val_Id = data_val['N°DPE']
    data_val[colonnes_a_transformer_val] = data_val[colonnes_a_transformer_val].replace(correspondance)

    data_val = data_val.drop(columns= ['N°DPE', 'Facteur_couverture_solaire_saisi', 'Surface_totale_capteurs_photovoltaïque', 'Facteur_couverture_solaire', 'Configuration_installation_chauffage_n°2', 'Type_générateur_froid', 'Type_émetteur_installation_chauffage_n°2',
                            'Classe_altitude', 'Code_postal_(brut)', 'Type_générateur_n°1_installation_n°2', 'Nom__commune_(Brut)',
                            "Cage_d'escalier", 'Code_INSEE_(BAN)', 'Description_générateur_chauffage_n°2_installation_n°2', 'N°_département_(BAN)'])

    return data_val, data_val_Id


@step
def predict(data_val: pd.DataFrame = None) -> Annotated[np.ndarray, "data_val"]:
    model = joblib.load('XGBoost_trained.pkl')

    return model.predict(data_val)


@step
def pred_save(pred: np.ndarray = None, data_val_Id: pd.Series = None) -> Annotated[pd.DataFrame, "data_pred"]:
    data_pred = pd.DataFrame()
    data_pred['N°DPE'] = data_val_Id
    data_pred['Etiquette_DPE'] = pred
    correspondance_val = {0:'G', 1:'F', 2:'E', 3:'D', 4:'C', 5:'B', 6:'A'}
    data_pred['Etiquette_DPE'] = data_pred['Etiquette_DPE'].replace(correspondance_val)
    data_pred.to_csv('Dpe_val.csv', index=False)

    return data_pred


@pipeline
def dpe_xgboost_pred() -> None:
    data_val = data_val_load()
    data_val, data_val_Id = data_clean_pred(data_val)
    pred = predict(data_val) 
    data_pred = pred_save(pred, data_val_Id)


if __name__ == "__main__":
    dpe_xgboost_pred()
