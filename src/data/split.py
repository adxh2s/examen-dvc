import yaml
import pandas as pd
import logging
from pathlib import Path
from sklearn.model_selection import train_test_split

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)

def main():
    params = yaml.safe_load(open("params.yaml"))
    
    # Load
    raw_path = Path(params['data']['raw_file'])
    logger.info(f"Loading data from {raw_path}")
    df = pd.read_csv(raw_path)
    
    # Clean
    if 'date' in df.columns: df = df.drop(columns=['date'])
    
    # Split
    X = df.iloc[:, :-1]
    y = df.iloc[:, -1]
    cfg = params['split']
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=cfg['test_size'],
        random_state=cfg['random_state'],
        stratify=y if cfg['stratify'] else None
    )
    
    # Save
    out = Path("data/processed_data")
    out.mkdir(parents=True, exist_ok=True)
    X_train.to_csv(out / "X_train.csv", index=False)
    X_test.to_csv(out / "X_test.csv", index=False)
    y_train.to_csv(out / "y_train.csv", index=False)
    y_test.to_csv(out / "y_test.csv", index=False)
    logger.info("Split completed.")

if __name__ == "__main__":
    main()
