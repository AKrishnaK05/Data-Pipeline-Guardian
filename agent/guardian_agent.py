import os
from dotenv import load_dotenv
from agent.rule_engine import rule_based_diagnosis
from agent.prompts import DIAGNOSIS_PROMPT

load_dotenv()

USE_LLM = True

def format_context(record, baseline):
    return f"""
    Context:
    - Observed row_count: {record['row_count']} (Baseline: {baseline['row_count_mean']:.2f})
    - Observed null_ratio: {record['null_ratio']:.2f} (Baseline: {baseline['null_ratio_mean']:.2f})
    - Observed late_event_ratio: {record['late_event_ratio']:.2f} (Baseline: {baseline['late_event_ratio_mean']:.2f})
    - Schema Change: {record['schema_change_flag']}
    """

from agent.llm_client import call_llm_hybrid

def run_guardian_agent(anomaly_record, baseline):
    """
    Combines rule-based severity with LLM-based root cause explanation.
    """
    rule_result = rule_based_diagnosis(anomaly_record, baseline)

    if not USE_LLM:
        return rule_result

    full_prompt = DIAGNOSIS_PROMPT + format_context(anomaly_record, baseline)
    llm_output = call_llm_hybrid(full_prompt)

    if not llm_output:
        return rule_result

    # Merge: Rule engine is trusted for severity, LLM for explanation/root cause nuances
    # Fallback to rule engine if LLM fails (returns empty dict)
    merged = {
        "root_cause": llm_output.get("root_cause") or rule_result["root_cause"],
        "severity": rule_result["severity"], # Maintain rule-based severity for safety
        "explanation": llm_output.get("explanation") or rule_result["explanation"],
        "recommended_actions": llm_output.get("recommended_actions") or rule_result["recommended_actions"]
    }
    
    return merged

