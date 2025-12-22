import pandas as pd
import time
from ml.detect_anomaly import detect_single
from agent.guardian_agent import run_guardian_agent
from pipeline.incident_state import IncidentState
from agent.fix_generator import generate_fix_proposal

WINDOW_DELAY_SECONDS = 1

def stream_simulation(input_path):
    df = pd.read_csv(input_path)
    BASELINE_WINDOWS = 5  

    baseline_df = df.iloc[:BASELINE_WINDOWS]

    baseline = {
    "row_count_mean": baseline_df["row_count"].mean(),
    "null_ratio_mean": baseline_df["null_ratio"].mean(),
    "late_event_ratio_mean": baseline_df["late_event_ratio"].mean()
    }

    incident = IncidentState()

    for _, row in df.iterrows():
        record = row.to_dict()

        # Dynamic Simulation Logic:
        # If the user applied the fix (watermark > 10), then re-evaluate "lateness".
        # In a real system, this would happen at ingestion. Here, we simulate it by
        # dropping the late_ratio to 0 if the config is updated.
        from pipeline.runtime_config import PIPELINE_CONFIG
        if PIPELINE_CONFIG["watermark_minutes"] > 10:
             if record["late_event_ratio"] > 0:
                 print(f"    [SIMULATION] Fix active! Adjusting late_ratio {record['late_event_ratio']:.2f} -> 0.0")
                 record["late_event_ratio"] = 0.0

        anomaly = detect_single(record)

        if anomaly["is_anomaly"]:

            # OPTIMIZATION: Only use heavy LLM agent for NEW incidents
            if not incident.active:
                diagnosis = run_guardian_agent(anomaly, baseline)
                incident.open(record["timestamp"], diagnosis)

                print("INCIDENT OPENED")
                print(f"Root cause: {diagnosis['root_cause']}")
                if "explanation" in diagnosis:
                     print(f"Explanation: {diagnosis['explanation']}")
                print(f"Severity: {diagnosis['severity']}")
                print("-" * 50)

                from agent.fix_generator import apply_fix
                fix = generate_fix_proposal(diagnosis)
                
                if fix:
                    print("\nFIX PROPOSAL")
                    print(f"Title: {fix['title']}")
                    print(f"Risk: {fix['risk']}")
                    print("\nDiff:")
                    print(fix["diff"])

                    # Interactive Approval
                    # We use a try/except block to handle non-interactive environments cleanly
                    try:
                        choice = input("\nApprove fix? (y/n): ").strip().lower()
                    except EOFError:
                        choice = "n"

                    if choice == "y":
                        apply_fix(fix)
                    else:
                        print("\nFix rejected by user\n")
            else:
                # For existing incidents, just update severity using fast rules (No LLM)
                from agent.rule_engine import rule_based_diagnosis
                diagnosis = rule_based_diagnosis(anomaly, baseline)
                incident.update(diagnosis)
                print(f"   [Active Incident] Severity: {diagnosis['severity']} | Root Cause: {incident.root_cause}")

        else:
            if incident.active:
                print("INCIDENT RESOLVED")
                
                from pipeline.runtime_config import PIPELINE_CONFIG
                if PIPELINE_CONFIG["watermark_minutes"] > 10:
                    print("  -> Reason: Fix applied (Watermark Increased)")
                else:
                    print("  -> Reason: Data stream recovered naturally (Transient Anomaly)")

                print(
                    f"Resolved after {incident.recovery_windows} consecutive healthy windows "
                    f"({incident.recovery_windows * 5} minutes of stability)"
                )
                print("-" * 50)
                incident.close()

        time.sleep(WINDOW_DELAY_SECONDS)

if __name__ == "__main__":
    stream_simulation("data/scenarios/single_late_data_incident.csv")
