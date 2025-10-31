"""Split raw data into train and test sets."""

import logging
from pathlib import Path
from typing import Tuple

import pandas as pd
import yaml
from sklearn.model_selection import train_test_split

# Constants
PROJECT_ROOT = Path(__file__).parents[2]
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw_data"
PROCESSED_DATA_PATH = PROJECT_ROOT / "data" / "processed_data"
PARAMS_PATH = PROJECT_ROOT / "params.yaml"

# Logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def load_params() -> dict:
    """Load parameters from params.yaml.
    
    Returns:
        Dictionary containing configuration parameters.
    """
    with open(PARAMS_PATH, "r") as f:
        return yaml.safe_load(f)


def load_raw_data(file_path: Path) -> pd.DataFrame:
    """Load raw CSV data.
    
    Args:
        file_path: Path to the raw CSV file.
        
    Returns:
        DataFrame containing the raw data.
        
    Raises:
        FileNotFoundError: If the CSV file doesn't exist.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Raw data file not found: {file_path}")
    
    logger.info(f"Loading raw data from {file_path}")
    return pd.read_csv(file_path)


def split_features_target(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
    """Split dataframe into features and target.
    
    Args:
        df: Input dataframe with target as last column.
        
    Returns:
        Tuple of (features_df, target_series).
    """
    X = df.iloc[:, :-1]
    y = df.iloc[:, -1]
    
    logger.info(f"Features shape: {X.shape}, Target shape: {y.shape}")
    return X, y


def split_train_test(
    X: pd.DataFrame,
    y: pd.Series,
    test_size: float,
    random_state: int,
    stratify: bool
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """Split data into train and test sets.
    
    Args:
        X: Feature dataframe.
        y: Target series.
        test_size: Proportion of data for test set.
        random_state: Random seed for reproducibility.
        stratify: Whether to stratify split by target.
        
    Returns:
        Tuple of (X_train, X_test, y_train, y_test).
    """
    stratify_param = y if stratify else None
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=test_size,
        random_state=random_state,
        stratify=stratify_param
    )
    
    logger.info(f"Train set size: {len(X_train)}, Test set size: {len(X_test)}")
    return X_train, X_test, y_train, y_test


def save_splits(
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    y_train: pd.Series,
    y_test: pd.Series,
    output_dir: Path
) -> None:
    """Save train/test splits to CSV files.
    
    Args:
        X_train: Training features.
        X_test: Test features.
        y_train: Training target.
        y_test: Test target.
        output_dir: Directory to save the files.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    X_train.to_csv(output_dir / "X_train.csv", index=False)
    X_test.to_csv(output_dir / "X_test.csv", index=False)
    y_train.to_csv(output_dir / "y_train.csv", index=False, header=True)
    y_test.to_csv(output_dir / "y_test.csv", index=False, header=True)
    
    logger.info(f"Saved splits to {output_dir}")


def main() -> None:
    """Main execution function."""
    # Load parameters
    params = load_params()
    split_params = params["split"]
    
    # Find CSV file in raw data directory
    csv_files = list(RAW_DATA_PATH.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {RAW_DATA_PATH}")
    
    raw_file = csv_files[0]
    logger.info(f"Using raw data file: {raw_file.name}")
    
    # Load and split data
    df = load_raw_data(raw_file)
    X, y = split_features_target(df)
    
    X_train, X_test, y_train, y_test = split_train_test(
        X, y,
        test_size=split_params["test_size"],
        random_state=split_params["random_state"],
        stratify=split_params["stratify"]
    )
    
    # Save splits
    save_splits(X_train, X_test, y_train, y_test, PROCESSED_DATA_PATH)
    
    logger.info("Data split completed successfully!")


if __name__ == "__main__":
    main()
