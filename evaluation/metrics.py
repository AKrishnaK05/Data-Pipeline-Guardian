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
    df = df.sort_values("timestamp")

    mttd_values = []
    
    current_incident_type = "NONE"
    incident_start_time = None
    first_detection_time = None

    for _, row in df.iterrows():
        atype = row["anomaly_type"]
        is_detected = row["is_anomaly"] == 1
        
        # Check if incident changed
        if atype != current_incident_type:
            # Close previous incident if valid
            if current_incident_type != "NONE":
                 # If detected, record the delay
                 if first_detection_time is not None:
                    delay = (first_detection_time - incident_start_time).total_seconds() / 60
                    mttd_values.append(delay)
            
            # Start new incident
            current_incident_type = atype
            if atype != "NONE":
                incident_start_time = row["timestamp"]
                first_detection_time = None
            else:
                incident_start_time = None
                first_detection_time = None
        
        # If inside an active incident, check for first detection
        if current_incident_type != "NONE":
            if is_detected and first_detection_time is None:
                 first_detection_time = row["timestamp"]
    
    # Handle edge case: File ends while incident is active
    if current_incident_type != "NONE" and first_detection_time is not None:
        delay = (first_detection_time - incident_start_time).total_seconds() / 60
        mttd_values.append(delay)

    return sum(mttd_values) / len(mttd_values) if mttd_values else 0.0

if __name__ == "__main__":
    df = pd.read_csv("data/processed/anomaly_results.csv")

    metrics = detection_metrics(df)
    mttd = mean_time_to_detect(df)

    print("\nDetection Metrics")
    print(f"Precision: {metrics['precision']:.3f}")
    print(f"Recall: {metrics['recall']:.3f}")

    print("\nMean Time To Detect (minutes)")
    print(mttd)
