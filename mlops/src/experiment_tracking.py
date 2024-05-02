from typing import Any, Dict, Tuple, Union
from typing_extensions import Annotated

import numpy as np
import pandas as pd

import mlflow
import mlflow.sklearn
import xgboost as xgb

from mlflow.models import infer_signature
from zenml_train import data_prep, data_load, data_clean
from zenml import pipeline, step
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score


@step
def get_params() -> Annotated[Dict[str,int], "params"]:
    return {
        "objective":'multi:softmax',
        "num_class":7,
    }


@step
def get_metrics(
    params: Dict[str,Union[str,int]] = None,
    x_train: pd.DataFrame = None,
    x_test: pd.DataFrame = None,
    y_test: pd.Series = None,
    y_train: pd.Series = None,
) -> Tuple[
    Annotated[np.float64, "précision"],
    Annotated[np.float64, "F1-score"],
    Annotated[np.float64, "AUC-ROC"],
    Annotated[xgb.XGBClassifier, "model"],
]:
    model = xgb.XGBClassifier(**params)
    model.fit(x_train, y_train)
    y_pred = model.predict(x_test)
    y_pred_proba = model.predict_proba(x_test)

    return (
        accuracy_score(y_test, y_pred),
        roc_auc_score(y_test, y_pred_proba, multi_class='ovr'),
        f1_score(y_test, y_pred, average='weighted'),
        model,
    )


@step
def setup_mlflow(
    x_train: pd.DataFrame = None,
    x_test: pd.DataFrame = None,
    y_test: pd.Series = None,
    y_train: pd.Series = None,
) -> Annotated[Any, 'Model Info']:
    params = get_params()
    print(params)
    accuracy, rod_auc, f1_score_metric, model = get_metrics(params,x_train, x_test, y_train, y_test)

    mlflow.set_tracking_uri(uri="http://dpe_vision-mlops-service:8080")
    mlflow.set_experiment("MLflow Quickstart")  # Create Experiment

    # Start an MLflow run
    with mlflow.start_run():
        # Log the hyperparameters
        mlflow.log_params(params)

        # Log the loss metric
        mlflow.log_metric("accuracy", accuracy)
        mlflow.log_metric("rod_auc", rod_auc)
        mlflow.log_metric("f1_score", f1_score_metric)

        # Set a tag that we can use to remind ourselves what this run was for
        mlflow.set_tag("Training Info", "XGBoost Model on DPE dataset")

        # Infer the model signature
        signature = infer_signature(x_train, model.predict(x_train))

        # Log the model
        model_info = mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path="DPE_model",
            signature=signature,
            input_example=x_train,
            registered_model_name="tracking-quickstart",
        )

        loaded_model = mlflow.pyfunc.load_model(model_info.model_uri)

    return loaded_model


@pipeline
def run_mlflow_server() -> None:
    data = data_load()
    x, y = data_clean(data)
    x_train, x_test, y_train, y_test = data_prep(x,y)
    setup_mlflow(x_train, x_test, y_train, y_test)


if __name__ == "__main__":
    run_mlflow_server()
