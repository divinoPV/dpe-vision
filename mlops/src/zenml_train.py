from typing import Tuple
from typing_extensions import Annotated

import joblib
import numpy as np
import pandas as pd
import xgboost as xgb

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    roc_auc_score,
)
from zenml import (
    ArtifactConfig,
    log_artifact_metadata,
    pipeline,
    step,
)


@step
def data_load() -> Annotated[pd.DataFrame, "data"]:
    """_summary_

    Returns:
        _type_: _description_
    """
    return pd.read_csv("data/train.csv")


# Charger vos données depuis un fichier CSV, par exemple
@step
def data_clean(data: pd.DataFrame = None) -> Tuple[
    Annotated[pd.DataFrame, "features"],
    Annotated[pd.Series, "target"],
]:
    """_summary_
    
    Step to clean data by transforming and labeling
    
    Returns:
        _type_:_Tuple_
    """
    correspondance = {'très bonne':4, 'insuffisante':1, 'bonne':3, 'moyenne':2, 0:0,
                      'appartement':1, 'maison':2, 'immeuble':3, 'A':6, 'B':5,'C':4,
                      'D':3, 'E':2, 'F':1, 'G':0, 'Électricité':1, 'Bois – Bûches':2,
                      'GPL':3, 'Gaz naturel':4,'Fioul domestique':5,
                      'Réseau de Chauffage urbain':6,'Bois – Granulés (pellets) ou briquettes':7,
                      "Électricité d'origine renouvelable utilisée dans le bâtiment":8,
                      'Bois – Plaquettes d’industrie':9, 'Bois – Plaquettes forestières':10,
                      'Charbon':11, 'Propane':12, 'Butane':13, 'Réseau de Froid Urbain':14}

    colonnes_a_transformer = ['Qualité_isolation_plancher_bas', 'Qualité_isolation_enveloppe',
                              'Qualité_isolation_menuiseries','Qualité_isolation_murs',
                              'Qualité_isolation_plancher_haut_comble_aménagé',
                              'Qualité_isolation_plancher_haut_comble_perdu',
                              'Qualité_isolation_plancher_haut_toit_terrase', 'Type_bâtiment',
                              'Etiquette_GES', 'Type_énergie_n°3', 'Etiquette_DPE']

    data = data.fillna(0)
    data[colonnes_a_transformer] = data[colonnes_a_transformer].replace(correspondance)

    data = data.drop(columns= ['Unnamed: 0','N°DPE', 'Configuration_installation_chauffage_n°2',
                               'Type_générateur_froid', 'Type_émetteur_installation_chauffage_n°2',
                               'Classe_altitude', 'Code_postal_(brut)',
                               'Type_générateur_n°1_installation_n°2', 'Nom__commune_(Brut)',
                               "Cage_d'escalier", 'Code_INSEE_(BAN)',
                               'Description_générateur_chauffage_n°2_installation_n°2',
                               'N°_département_(BAN)','Surface_totale_capteurs_photovoltaïque', 
                               'Facteur_couverture_solaire_saisi', 'Facteur_couverture_solaire'])

    # Séparer les caractéristiques (X) de la cible (y)
    return data.drop(columns=['Etiquette_DPE']), data['Etiquette_DPE']


@step
def data_prep(
    x: pd.DataFrame = None,
    y: pd.Series = None,
) -> Tuple[
    Annotated[pd.DataFrame, "features_train"],
    Annotated[pd.DataFrame, "features_test"],
    Annotated[pd.Series, "target_train"],
    Annotated[pd.Series, "target_test"],
]:
    """_summary_
    Args:
        x : pd.DataFrame -> None
        y : pd.Series -> None
    Returns:
        Tuple: _Tuple_
    """
    # Séparez les données en ensembles d'apprentissage et de test
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)

    return x_train, x_test, y_train, y_test


@step
def train_model(
    x_test: pd.DataFrame = None,
    x_train: pd.DataFrame = None,
    y_train: pd.Series = None,
    y_test: pd.Series = None,
) -> Annotated[
    xgb.XGBClassifier,
    ArtifactConfig(name="my_model", tags=["XGBoost", "trained"]),
]:
    """_summary_
    Args:
        x_test: pd.DataFrame -> None
        x_train: pd.DataFrame -> None
        y_train: pd.Series -> None
        y_test: pd.Series -> None
    Returns:
        _type_: _description_
    """
    # Créez un modèle XGBoost
    model = xgb.XGBClassifier(objective='multi:softmax', num_class=7)

    # Entraînez le modèle sur l'ensemble d'apprentissage
    model.fit(x_train, y_train)

    #Prédictions sur l'ensemble de test
    y_pred = model.predict(x_test)
    y_pred_proba = model.predict_proba(x_test)
    # Mesurez la performance du modèle
    accuracy = accuracy_score(y_test, y_pred)
    roc = roc_auc_score(y_test, y_pred_proba, multi_class='ovr')
    conf_matrix = confusion_matrix(y_test, y_pred)
    conf_matrix = conf_matrix.tolist()
    f1 = f1_score(y_test, y_pred, average='weighted')

    log_artifact_metadata(
        # Artifact name can be omitted if step returns only one output
        artifact_name="my_model",
        # Metadata should be a dictionary of JSON-serializable values
        metadata = {
            "metrics": {
                "accuracy": float(accuracy),
                "roc": float(roc),
                "conf_matrix": conf_matrix,
                "f1": float(f1),
            },
        }
        # A dictionary of dictionaries can also be passed to group metadata
        # in the dashboard
        # metadata = {"metrics": {"accuracy": accuracy}}
    )

    joblib.dump(model, "XGBoost_trained.pkl")

    return model


@step
def test_model(
    x_test: pd.DataFrame = None,
    y_test: pd.Series = None,
    model: xgb.XGBClassifier = None,
) -> Tuple[
    Annotated[np.float64, "précision"],
    Annotated[np.float64, "F1-score"],
    Annotated[np.float64, "AUC-ROC"],
    Annotated[np.ndarray, "conf_matrice"],
]:
    """_summary_
    Step pour predire sur la dataset test
    Returns:
        _type_: _Tuple_
    """
    #Prédictions sur l'ensemble de test
    y_pred = model.predict(x_test)
    y_pred_proba = model.predict_proba(x_test)

    # Mesurez la performance du modèle
    return (
        accuracy_score(y_test, y_pred),
        roc_auc_score(y_test, y_pred_proba, multi_class='ovr'),
        f1_score(y_test, y_pred, average='weighted'),
        confusion_matrix(y_test, y_pred),
    )


@pipeline
def dpe_xgboost_train() -> None:
    """_summary_
    Pipeline pour préparer, entrainer, et predire
    """
    data = data_load()
    x, y = data_clean(data)
    x_train, x_test, y_train, y_test = data_prep(x, y)
    model = train_model(x_test, x_train, y_train, y_test)
    # test_model(X_test, y_test, model)


if __name__ == "__main__":
    dpe_xgboost_train()
