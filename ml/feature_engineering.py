import pandas as pd
from sklearn.preprocessing import StandardScaler

FEATURE_COLUMNS = [
    "row_count",
    "null_ratio",
    "late_event_ratio",
    "schema_change_flag"
]

def load_and_prepare_features(csv_path):
    df = pd.read_csv(csv_path, parse_dates=["timestamp"])

    X = df[FEATURE_COLUMNS]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    return X_scaled, df, scaler
