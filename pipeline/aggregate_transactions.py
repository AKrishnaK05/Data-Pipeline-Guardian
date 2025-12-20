import pandas as pd

WINDOW_SIZE = "5min"
# LATE_THRESHOLD_MINUTES = 10
from pipeline.runtime_config import PIPELINE_CONFIG

def is_late(event_time, ingestion_time):
    threshold = PIPELINE_CONFIG["watermark_minutes"]
    return (ingestion_time - event_time).total_seconds() / 60 > threshold

def aggregate_transactions(input_path, output_path):
    print("Aggregating raw supermarket transactions...")
    df = pd.read_csv(input_path)

    # Parse timestamps
    df["event_time"] = pd.to_datetime(df["event_time"])
    df["ingestion_time"] = pd.to_datetime(df["ingestion_time"])

    # Late event flag
    # df["is_late"] = (
    #     (df["ingestion_time"] - df["event_time"])
    #     .dt.total_seconds() / 60
    #     > LATE_THRESHOLD_MINUTES
    # )
    df["is_late"] = df.apply(
        lambda r: is_late(r["event_time"], r["ingestion_time"]),
        axis=1
    )

    # Null check on critical fields
    critical_fields = ["transaction_id", "event_time", "store_id", "amount"]
    df["has_null"] = df[critical_fields].isnull().any(axis=1)

    # Assign 5-minute event-time windows
    df["window_start"] = df["event_time"].dt.floor(WINDOW_SIZE)

    # Aggregate
    agg = (
        df.groupby("window_start")
        .agg(
            row_count=("transaction_id", "count"),
            null_ratio=("has_null", "mean"),
            late_event_ratio=("is_late", "mean")
        )
        .reset_index()
    )

    # Schema change not simulated
    agg["schema_change_flag"] = 0

    # Rename for consistency
    agg = agg.rename(columns={"window_start": "timestamp"})

    # Save
    agg.to_csv(output_path, index=False)

    print("Aggregation complete")
    print(f"Output written to: {output_path}")
    print("\nPreview:")
    print(agg)


if __name__ == "__main__":
    aggregate_transactions()
