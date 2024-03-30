from zenml import pipeline

from src.zenml_predict import dpe_xgboost_pred
from src.zenml_train import dpe_xgboost_train


@pipeline
def train_and_predict() -> None:
    step_1 = dpe_xgboost_train()
    step_2 = dpe_xgboost_pred()


if __name__ == "__main__":
    train_and_predict()
