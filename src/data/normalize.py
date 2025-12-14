import pandas as pd
import logging
import yaml
from pathlib import Path
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

def get_scaler(strategy):
    if strategy == "standard": return StandardScaler()
    if strategy == "minmax": return MinMaxScaler()
    if strategy == "robust": return RobustScaler()
    raise ValueError(f"Unknown strategy: {strategy}")

def main():
    params = yaml.safe_load(open("params.yaml"))
    in_dir = Path("data/processed_data")
    
    X_train = pd.read_csv(in_dir / "X_train.csv")
    X_test = pd.read_csv(in_dir / "X_test.csv")
    
    strategy = params['preprocessing']['numerical']['strategy']
    logging.info(f"Normalizing with {strategy}...")
    
    scaler = get_scaler(strategy)
    X_train_scaled = pd.DataFrame(scaler.fit_transform(X_train), columns=X_train.columns)
    X_test_scaled = pd.DataFrame(scaler.transform(X_test), columns=X_test.columns)
    
    X_train_scaled.to_csv(in_dir / "X_train_scaled.csv", index=False)
    X_test_scaled.to_csv(in_dir / "X_test_scaled.csv", index=False)
    logging.info("Normalization done.")

if __name__ == "__main__":
    main()
