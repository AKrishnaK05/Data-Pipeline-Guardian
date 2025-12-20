def generate_fix_proposal(diagnosis):
    """
    Generate a PR-style fix proposal based on diagnosis.
    This function NEVER executes changes.
    """

    root_cause = diagnosis["root_cause"]
    severity = diagnosis["severity"]

    # --- Schema Change ---
    if "Schema change" in root_cause:
        return {
            "title": "Align downstream schema with upstream changes",
            "summary": (
                "A schema change was detected in upstream data. "
                "Downstream consumers may fail or drop records if schemas are misaligned."
            ),
            "diff": """
- expected_schema = v1
+ expected_schema = v2
""",
            "risk": "HIGH",
            "requires_approval": True
        }

    # --- Late Arriving Data ---
    if "Late-arriving data" in root_cause:
        return {
            "title": "Increase event-time watermark tolerance",
            "summary": (
                "Late-arriving events are exceeding the current watermark, "
                "which may cause data loss or incomplete aggregations."
            ),
            "diff": """
- watermark = 10 minutes
+ watermark = 20 minutes
""",
            "risk": "LOW",
            "requires_approval": True
        }

    # --- Null Spike ---
    if "Null ratio" in root_cause:
        return {
            "title": "Add null validation in transformation step",
            "summary": (
                "An increase in null values suggests data quality issues. "
                "Adding validation prevents downstream corruption."
            ),
            "diff": """
+ if value is NULL:
+     log warning
+     skip record
""",
            "risk": "MEDIUM",
            "requires_approval": True
        }

    # --- Volume Drop ---
    if "row count" in root_cause:
        return {
            "title": "Investigate upstream ingestion failure",
            "summary": (
                "A significant drop in row count indicates potential ingestion failures "
                "or upstream system outages."
            ),
            "diff": """
# No automatic code change suggested.
# Action required: inspect ingestion job logs.
""",
            "risk": "HIGH",
            "requires_approval": True
        }

    # --- Fallback ---
    return None

def apply_fix(fix):
    """
    Simulate fix execution by updating runtime config.
    """
    from pipeline.runtime_config import PIPELINE_CONFIG

    if "watermark" in fix["title"].lower():
        PIPELINE_CONFIG["watermark_minutes"] = 20
        print("\n✅ FIX APPLIED (SIMULATED)")
        print("Watermark updated to 20 minutes\n")
