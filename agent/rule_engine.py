def rule_based_diagnosis(record, baseline):
    actions = []
    explanation = ""
    severity = "low"

    row_drop_ratio = record["row_count"] / baseline["row_count_mean"]
    null_increase = record["null_ratio"] - baseline["null_ratio_mean"]
    late_increase = record["late_event_ratio"] - baseline["late_event_ratio_mean"]

    late_increase = record["late_event_ratio"] - baseline["late_event_ratio_mean"]


    if record["schema_change_flag"] == 1:
        explanation = "Schema change detected in incoming data."
        actions = [
            "Verify upstream schema changes",
            "Check compatibility with downstream consumers"
        ]
        severity = "high"

    elif row_drop_ratio < 0.6:
        explanation = "Significant relative drop in row count detected."
        actions = [
            "Check upstream ingestion job",
            "Verify source system availability"
        ]
        severity = "high"

    elif null_increase > 0.08:
        explanation = "Null ratio increased significantly compared to baseline."
        actions = [
            "Inspect recent transformations",
            "Validate source data fields"
        ]
        severity = "medium"

    elif late_increase > 0.5:
        explanation = "Late-arriving data increased significantly."
        actions = [
            "Check event-time watermark configuration",
            "Inspect upstream delays"
        ]
        severity = "medium"

    elif record["anomaly_score"] < -0.2:
        explanation = "Multivariate anomaly detected with no single dominant metric."
        actions = ["Perform focused manual inspection"]
        severity = "low"

    else:
        explanation = "Anomaly detected, but root cause is unclear."
        actions = ["Perform manual inspection"]

    return {
        "root_cause": explanation,
        "explanation": explanation,
        "recommended_actions": actions,
        "severity": severity,
        "confidence": 0.7 if severity != "low" else 0.5
    }
