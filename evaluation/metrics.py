import pandas as pd
from sklearn.metrics import precision_score, recall_score


def detection_metrics(df):
    if df.empty:
        return {"precision": None, "recall": None}

    y_true = (df["anomaly_type"] != "NONE").astype(int)
    y_pred = df["is_anomaly"]

    return {
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "recall": recall_score(y_true, y_pred, zero_division=0)
    }


def mean_time_to_detect(df):
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    mttd_values = []

    for anomaly_type in df["anomaly_type"].unique():
        if anomaly_type == "NONE":
            continue

        anomaly_windows = df[df["anomaly_type"] == anomaly_type]
        first_anomaly_time = anomaly_windows["timestamp"].min()

        detected_windows = anomaly_windows[anomaly_windows["is_anomaly"] == 1]
        if detected_windows.empty:
            continue

        first_detection_time = detected_windows["timestamp"].min()
        detection_delay = (
            first_detection_time - first_anomaly_time
        ).total_seconds() / 60

        mttd_values.append(detection_delay)

    return sum(mttd_values) / len(mttd_values) if mttd_values else None

if __name__ == "__main__":
    df = pd.read_csv("data/processed/anomaly_results.csv")

    metrics = detection_metrics(df)
    mttd = mean_time_to_detect(df)

    print("\nDetection Metrics")
    print(f"Precision: {metrics['precision']:.3f}")
    print(f"Recall: {metrics['recall']:.3f}")

    print("\nMean Time To Detect (minutes)")
    print(mttd)
