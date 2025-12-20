import joblib
from sklearn.ensemble import IsolationForest
from ml.feature_engineering import load_and_prepare_features
from config.config_loader import load_config

def train():
    config = load_config()

    X, df, scaler = load_and_prepare_features(config["paths"]["raw_data"])

    normal_mask = df["anomaly_type"] == "NONE"
    X_train = X[normal_mask]

    model = IsolationForest(
        n_estimators=200,
        contamination=0.08,
        random_state=42
    )

    model.fit(X_train)

    joblib.dump(model, config["paths"]["model_path"])
    joblib.dump(scaler, "ml/scaler.pkl")
    print("Isolation Forest and scaler trained and saved.")

if __name__ == "__main__":
    train()
