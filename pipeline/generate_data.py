import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

ANOMALY_TYPES = [
    "VOLUME_DROP",
    "VOLUME_SPIKE",
    "NULL_SPIKE",
    "LATE_DATA",
    "SCHEMA_CHANGE"
]

def generate_pipeline_data(
    num_windows=500,
    anomaly_ratio=0.08
):
    data = []
    start_time = datetime.now()

    base_row_count = 10000
    
    for i in range(num_windows):
        timestamp = start_time + timedelta(minutes=5 * i)

        row_count = int(np.random.normal(base_row_count, 1.5))
        null_ratio = max(0, np.random.normal(0.0, 0.001))
        late_ratio = max(0, np.random.normal(0.0, 0.001))
        schema_flag = 0
        anomaly_type = "NONE"

        if random.random() < anomaly_ratio:
            anomaly_type = random.choice(ANOMALY_TYPES)

            if anomaly_type == "VOLUME_DROP":
                row_count = int(base_row_count * np.random.uniform(0.3, 0.6))

            elif anomaly_type == "VOLUME_SPIKE":
                row_count = int(base_row_count * np.random.uniform(1.5, 2.2))

            elif anomaly_type == "NULL_SPIKE":
                null_ratio = np.random.uniform(0.15, 0.35)

            elif anomaly_type == "LATE_DATA":
                late_ratio = np.random.uniform(0.2, 0.4)

            elif anomaly_type == "SCHEMA_CHANGE":
                schema_flag = 1

        data.append([
            timestamp,
            row_count,
            null_ratio,
            late_ratio,
            schema_flag,
            anomaly_type
        ])

    columns = [
        "timestamp",
        "row_count",
        "null_ratio",
        "late_event_ratio",
        "schema_change_flag",
        "anomaly_type"
    ]

    return pd.DataFrame(data, columns=columns)


if __name__ == "__main__":
    df = generate_pipeline_data()
    df.to_csv("data/raw/pipeline_metrics.csv", index=False)
    print("Synthetic pipeline data generated.")
