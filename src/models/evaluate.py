import yaml, joblib, json, logging
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

def compute_metrics(y_true, y_pred, metrics):
    res = {}
    if "mse" in metrics: res["mse"] = mean_squared_error(y_true, y_pred)
    if "rmse" in metrics: res["rmse"] = np.sqrt(mean_squared_error(y_true, y_pred))
    if "mae" in metrics: res["mae"] = mean_absolute_error(y_true, y_pred)
    if "r2" in metrics: res["r2"] = r2_score(y_true, y_pred)
    if "mape" in metrics: 
        mask = y_true != 0
        res["mape"] = np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100
    return res

def main():
    cfg = yaml.safe_load(open("params.yaml"))
    model = joblib.load("models/model.pkl")
    
    X_test = pd.read_csv("data/processed_data/X_test_scaled.csv")
    y_test = pd.read_csv("data/processed_data/y_test.csv")
    y_true = y_test.values.ravel()
    
    logging.info("Predicting...")
    pred = model.predict(X_test)
    
    scores = compute_metrics(y_true, pred, cfg['evaluation']['metrics'])
    
    Path("metrics").mkdir(exist_ok=True)
    with open("metrics/scores.json", "w") as f: json.dump(scores, f, indent=4)
        
    out = X_test.copy()
    out['target_real'] = y_true
    out['target_pred'] = pred
    out.to_csv("data/predictions.csv", index=False)
    logging.info(f"Evaluation done. Scores: {scores}")

if __name__ == "__main__":
    main()
