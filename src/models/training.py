"""Train ML models using scikit-learn Pipelines with GridSearchCV."""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List

import joblib
import pandas as pd
import yaml
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

# Constants
PROJECT_ROOT = Path(__file__).parents[2]
PROCESSED_DATA_PATH = PROJECT_ROOT / "data" / "processed"
MODELS_PATH = PROJECT_ROOT / "models"
PARAMS_PATH = PROJECT_ROOT / "params.yaml"

# Logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def load_params() -> dict:
    """Load parameters from params.yaml."""
    with open(PARAMS_PATH, "r") as f:
        return yaml.safe_load(f)


def load_train_data() -> tuple[pd.DataFrame, pd.Series]:
    """Load training data.
    
    Returns:
        Tuple of (X_train, y_train).
    """
    X_train = pd.read_csv(PROCESSED_DATA_PATH / "X_train.csv")
    y_train = pd.read_csv(PROCESSED_DATA_PATH / "y_train.csv").squeeze()
    
    logger.info(f"Loaded training data: X={X_train.shape}, y={y_train.shape}")
    return X_train, y_train


def identify_column_types(X: pd.DataFrame) -> tuple[List[str], List[str]]:
    """Identify numerical and categorical columns.
    
    Args:
        X: Feature dataframe.
        
    Returns:
        Tuple of (numerical_columns, categorical_columns).
    """
    numerical_cols = X.select_dtypes(include=["int64", "float64"]).columns.tolist()
    categorical_cols = X.select_dtypes(include=["object", "category"]).columns.tolist()
    
    logger.info(f"Numerical columns: {len(numerical_cols)}, Categorical: {len(categorical_cols)}")
    return numerical_cols, categorical_cols


def create_preprocessor(numerical_cols: List[str], categorical_cols: List[str]) -> ColumnTransformer:
    """Create preprocessing pipeline.
    
    Args:
        numerical_cols: List of numerical column names.
        categorical_cols: List of categorical column names.
        
    Returns:
        ColumnTransformer for preprocessing.
    """
    transformers = []
    
    if numerical_cols:
        transformers.append(("num", StandardScaler(), numerical_cols))
    
    if categorical_cols:
        transformers.append((
            "cat",
            OneHotEncoder(drop="first", sparse_output=False, handle_unknown="ignore"),
            categorical_cols
        ))
    
    return ColumnTransformer(transformers=transformers, remainder="passthrough")


def get_model_configs(params: dict) -> List[Dict[str, Any]]:
    """Get model configurations from params.
    
    Args:
        params: Parameters dictionary.
        
    Returns:
        List of model configurations.
    """
    model_mapping = {
        "RandomForest": RandomForestRegressor,
        "GradientBoosting": GradientBoostingRegressor,
    }
    
    configs = []
    for model_config in params["models"]:
        model_name = model_config["name"]
        if model_name in model_mapping:
            configs.append({
                "name": model_name,
                "estimator": model_mapping[model_name],
                "params": model_config["params"]
            })
    
    return configs


def train_with_gridsearch(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    preprocessor: ColumnTransformer,
    model_configs: List[Dict[str, Any]],
    grid_params: dict
) -> tuple[Pipeline, Dict[str, Any]]:
    """Train models with GridSearchCV and return best pipeline.
    
    Args:
        X_train: Training features.
        y_train: Training target.
        preprocessor: Preprocessing pipeline.
        model_configs: List of model configurations.
        grid_params: GridSearch parameters.
        
    Returns:
        Tuple of (best_pipeline, best_results).
    """
    best_score = float("-inf")
    best_pipeline = None
    best_results = {}
    
    for config in model_configs:
        logger.info(f"\nTraining {config['name']}...")
        
        # Create pipeline
        pipeline = Pipeline([
            ("preprocessor", preprocessor),
            ("regressor", config["estimator"](random_state=42))
        ])
        
        # Prepare parameter grid with pipeline prefixes
        param_grid = {
            f"regressor__{key}": value
            for key, value in config["params"].items()
        }
        
        # GridSearch
        grid_search = GridSearchCV(
            pipeline,
            param_grid,
            cv=grid_params["cv"],
            scoring=grid_params["scoring"],
            n_jobs=grid_params["n_jobs"],
            verbose=grid_params["verbose"]
        )
        
        grid_search.fit(X_train, y_train)
        
        logger.info(f"{config['name']} - Best score: {-grid_search.best_score_:.4f}")
        logger.info(f"{config['name']} - Best params: {grid_search.best_params_}")
        
        if grid_search.best_score_ > best_score:
            best_score = grid_search.best_score_
            best_pipeline = grid_search.best_estimator_
            best_results = {
                "model_name": config["name"],
                "best_score": float(-best_score),
                "best_params": {
                    key.replace("regressor__", ""): value
                    for key, value in grid_search.best_params_.items()
                }
            }
    
    return best_pipeline, best_results


def save_pipeline(pipeline: Pipeline, results: Dict[str, Any], output_dir: Path) -> None:
    """Save trained pipeline and results.
    
    Args:
        pipeline: Trained pipeline.
        results: Training results.
        output_dir: Output directory.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save pipeline
    pipeline_path = output_dir / "best_pipeline.pkl"
    joblib.dump(pipeline, pipeline_path)
    logger.info(f"Saved pipeline to {pipeline_path}")
    
    # Save results
    results_path = output_dir / "best_params.json"
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    logger.info(f"Saved results to {results_path}")


def main() -> None:
    """Main execution function."""
    params = load_params()
    
    # Load data
    X_train, y_train = load_train_data()
    
    # Identify column types
    numerical_cols, categorical_cols = identify_column_types(X_train)
    
    # Create preprocessor
    preprocessor = create_preprocessor(numerical_cols, categorical_cols)
    
    # Get model configurations
    model_configs = get_model_configs(params)
    
    # Train with GridSearch
    best_pipeline, results = train_with_gridsearch(
        X_train, y_train,
        preprocessor,
        model_configs,
        params["grid_search"]
    )
    
    # Save results
    save_pipeline(best_pipeline, results, MODELS_PATH)
    
    logger.info(f"\nTraining completed! Best model: {results['model_name']}")


if __name__ == "__main__":
    main()
