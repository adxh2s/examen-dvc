import yaml, joblib, logging
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import GridSearchCV

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

def get_model(name):
    if name == "RandomForest": return RandomForestRegressor()
    if name == "GradientBoosting": return GradientBoostingRegressor()
    raise ValueError(f"Unknown model: {name}")

def main():
    config = yaml.safe_load(open("params.yaml"))
    X_train = pd.read_csv("data/processed_data/X_train_scaled.csv")
    y_train = pd.read_csv("data/processed_data/y_train.csv").values.ravel()
    
    best_score = -np.inf
    best_res = None
    
    for m in config['models']:
        logging.info(f"GridSearching {m['name']}...")
        grid = GridSearchCV(get_model(m['name']), m['params'], **config['grid_search'])
        grid.fit(X_train, y_train)
        
        if grid.best_score_ > best_score:
            best_score = grid.best_score_
            best_res = {"model_name": m['name'], "best_params": grid.best_params_}
            
    Path("models").mkdir(exist_ok=True)
    joblib.dump(best_res, "models/best_params.pkl")
    logging.info(f"Best model: {best_res['model_name']}")

if __name__ == "__main__":
    main()
