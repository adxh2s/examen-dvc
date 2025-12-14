import yaml, joblib, logging
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

def main():
    config = yaml.safe_load(open("params.yaml"))
    best = joblib.load("models/best_params.pkl")
    
    X_train = pd.read_csv("data/processed_data/X_train_scaled.csv")
    y_train = pd.read_csv("data/processed_data/y_train.csv").values.ravel()
    
    logging.info(f"Training final {best['model_name']}...")
    if best['model_name'] == "RandomForest":
        model = RandomForestRegressor(**best['best_params'], random_state=config['split']['random_state'])
    else:
        model = GradientBoostingRegressor(**best['best_params'], random_state=config['split']['random_state'])
        
    model.fit(X_train, y_train)
    joblib.dump(model, "models/model.pkl")
    logging.info("Model saved.")

if __name__ == "__main__":
    main()
