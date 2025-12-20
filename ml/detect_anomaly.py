import joblib
from ml.feature_engineering import load_and_prepare_features
from config.config_loader import load_config

def detect():
    config = load_config()

    model = joblib.load(config["paths"]["model_path"])

    X, df, _ = load_and_prepare_features(config["paths"]["raw_data"])

    df["anomaly_score"] = model.decision_function(X)
    df["is_anomaly"] = (model.predict(X) == -1).astype(int)

    df.to_csv(config["paths"]["processed_data"], index=False)
    print("Anomaly detection completed.")

def detect_single(record):
    import joblib
    import pandas as pd
    from ml.feature_engineering import FEATURE_COLUMNS

    model = joblib.load("ml/isolation_forest.pkl")
    scaler = joblib.load("ml/scaler.pkl")

    X = pd.DataFrame([record])[FEATURE_COLUMNS]
    X_scaled = scaler.transform(X)

    score = model.decision_function(X_scaled)[0]
    is_anomaly = model.predict(X_scaled)[0] == -1

    record["anomaly_score"] = score
    record["is_anomaly"] = int(is_anomaly)

    return record

if __name__ == "__main__":
    detect()
