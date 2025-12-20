import pandas as pd
import json
from agent.guardian_agent import run_guardian_agent

SAVE_TO_CSV = False  # default OFF

def run():
    df = pd.read_csv("data/processed/anomaly_results.csv")
    anomalies = df[df["is_anomaly"] == 1]

    print(f"\nDetected {len(anomalies)} anomalies\n")

    baseline = {
        "row_count_mean": df["row_count"].mean(),
        "null_ratio_mean": df["null_ratio"].mean(),
        "late_event_ratio_mean": df["late_event_ratio"].mean()
    }

    summary = {
        "total": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
        "by_root_cause": {}
    }

    results = []
    for idx, row in anomalies.iterrows():
        anomaly_record = {
            "row_count": row["row_count"],
            "null_ratio": row["null_ratio"],
            "late_event_ratio": row["late_event_ratio"],
            "schema_change_flag": row["schema_change_flag"],
            "anomaly_score": row["anomaly_score"]
        }

        diagnosis = run_guardian_agent(anomaly_record, baseline)

        results.append(diagnosis)

        summary["total"] += 1
        summary[diagnosis["severity"]] += 1

        rc = diagnosis["root_cause"]
        summary["by_root_cause"][rc] = summary["by_root_cause"].get(rc, 0) + 1

        print("Anomaly Detected")
        print(json.dumps(diagnosis, indent=2))
        print("-" * 50)

    if SAVE_TO_CSV:
        pd.DataFrame(results).to_csv(
            "data/processed/guardian_diagnosis.csv",
            index=False
        )

    print("\nGuardian Summary")
    print(f"Total anomalies: {summary['total']}")
    print(f"High severity: {summary['high']}")
    print(f"Medium severity: {summary['medium']}")
    print(f"Low severity: {summary['low']}")

    print("\nRoot cause breakdown:")
    for k, v in summary["by_root_cause"].items():
        print(f"- {k}: {v}")

if __name__ == "__main__":
    run()
