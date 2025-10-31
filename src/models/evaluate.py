"""Evaluate trained model and generate predictions."""

import json
import logging
from pathlib import Path
from typing import Dict

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline

# Constants
PROJECT_ROOT = Path(__file__).parents[2]
PROCESSED_DATA_PATH = PROJECT_ROOT / "data" / "processed_data"
MODELS_PATH = PROJECT_ROOT / "models"
METRICS_PATH = PROJECT_ROOT / "metrics"
DATA_PATH = PROJECT_ROOT / "data"

# Logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def load_test_data() -> tuple[pd.DataFrame, pd.Series]:
    """Load test data.
    
    Returns:
        Tuple of (X_test, y_test).
    """
    X_test = pd.read_csv(PROCESSED_DATA_PATH / "X_test.csv")
    y_test = pd.read_csv(PROCESSED_DATA_PATH / "y_test.csv").squeeze()
    
    logger.info(f"Loaded test data: X={X_test.shape}, y={y_test.shape}")
    return X_test, y_test


def load_pipeline(model_path: Path) -> Pipeline:
    """Load trained pipeline.
    
    Args:
        model_path: Path to the saved pipeline.
        
    Returns:
        Loaded pipeline.
    """
    logger.info(f"Loading pipeline from {model_path}")
    return joblib.load(model_path)


def calculate_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """Calculate evaluation metrics.
    
    Args:
        y_true: True target values.
        y_pred: Predicted target values.
        
    Returns:
        Dictionary of metrics.
    """
    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    
    # MAPE (Mean Absolute Percentage Error)
    mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
    
    metrics = {
        "mse": float(mse),
        "rmse": float(rmse),
        "mae": float(mae),
        "r2": float(r2),
        "mape": float(mape)
    }
    
    logger.info("Metrics calculated:")
    for key, value in metrics.items():
        logger.info(f"  {key.upper()}: {value:.4f}")
    
    return metrics


def save_predictions(X_test: pd.DataFrame, y_test: pd.Series, y_pred: np.ndarray, output_path: Path) -> None:
    """Save predictions to CSV.
    
    Args:
        X_test: Test features.
        y_test: True test targets.
        y_pred: Predicted values.
        output_path: Output file path.
    """
    predictions_df = X_test.copy()
    predictions_df["y_true"] = y_test.values
    predictions_df["y_pred"] = y_pred
    predictions_df["error"] = y_test.values - y_pred
    
    predictions_df.to_csv(output_path, index=False)
    logger.info(f"Saved predictions to {output_path}")


def save_metrics(metrics: Dict[str, float], output_path: Path) -> None:
    """Save metrics to JSON.
    
    Args:
        metrics: Dictionary of metrics.
        output_path: Output file path.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w") as f:
        json.dump(metrics, f, indent=2)
    
    logger.info(f"Saved metrics to {output_path}")


def main() -> None:
    """Main execution function."""
    # Load test data
    X_test, y_test = load_test_data()
    
    # Load pipeline
    pipeline = load_pipeline(MODELS_PATH / "best_pipeline.pkl")
    
    # Make predictions
    logger.info("Making predictions...")
    y_pred = pipeline.predict(X_test)
    
    # Calculate metrics
    metrics = calculate_metrics(y_test.values, y_pred)
    
    # Save results
    save_predictions(X_test, y_test, y_pred, DATA_PATH / "predictions.csv")
    save_metrics(metrics, METRICS_PATH / "scores.json")
    
    logger.info("Evaluation completed successfully!")


if __name__ == "__main__":
    main()
