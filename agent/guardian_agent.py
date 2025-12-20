import json
import google.generativeai as genai
from agent.rule_engine import rule_based_diagnosis
from agent.prompts import DIAGNOSIS_PROMPT

USE_LLM = True
api_key = "AIzaSyA5D5b08MQ5OcMFt25kv7_kIl8uLVpfAyA"
genai.configure(api_key=api_key)

def format_context(record, baseline):
    return f"""
    Context:
    - Observed row_count: {record['row_count']} (Baseline: {baseline['row_count_mean']:.2f})
    - Observed null_ratio: {record['null_ratio']:.2f} (Baseline: {baseline['null_ratio_mean']:.2f})
    - Observed late_event_ratio: {record['late_event_ratio']:.2f} (Baseline: {baseline['late_event_ratio_mean']:.2f})
    - Schema Change: {record['schema_change_flag']}
    """

def call_llm(prompt):
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        text = response.text
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        return json.loads(text)
    except Exception as e:
        print(f"[LLM ERROR] Diagnosis failed: {e}")
        return {}

def run_guardian_agent(anomaly_record, baseline):
    """
    Combines rule-based severity with LLM-based root cause explanation.
    """
    rule_result = rule_based_diagnosis(anomaly_record, baseline)

    if not USE_LLM:
        return rule_result

    full_prompt = DIAGNOSIS_PROMPT + format_context(anomaly_record, baseline)
    llm_output = call_llm(full_prompt)

    # Merge: Rule engine is trusted for severity, LLM for explanation/root cause nuances
    merged = {
        "root_cause": llm_output.get("root_cause", rule_result["root_cause"]),
        "severity": rule_result["severity"], # Maintain rule-based severity for safety
        "explanation": llm_output.get("explanation", "Analysis failed"),
        "recommended_actions": llm_output.get("recommended_actions", [])
    }
    
    return merged

