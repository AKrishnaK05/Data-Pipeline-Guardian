import os
from google import genai
from dotenv import load_dotenv
from agent.rule_engine import rule_based_diagnosis
from agent.prompts import DIAGNOSIS_PROMPT

load_dotenv()

USE_LLM = True
api_key = os.environ.get("GOOGLE_API_KEY")
client = genai.Client(api_key=api_key)

def format_context(record, baseline):
    return f"""
    Context:
    - Observed row_count: {record['row_count']} (Baseline: {baseline['row_count_mean']:.2f})
    - Observed null_ratio: {record['null_ratio']:.2f} (Baseline: {baseline['null_ratio_mean']:.2f})
    - Observed late_event_ratio: {record['late_event_ratio']:.2f} (Baseline: {baseline['late_event_ratio_mean']:.2f})
    - Schema Change: {record['schema_change_flag']}
    """

import time

def call_llm(prompt):
    max_retries = 1
    base_delay = 10
    
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash-exp", contents=prompt
            )
            text = response.text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            return json.loads(text)
        except Exception as e:
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                wait_time = base_delay * (2 ** attempt)
                print(f"[LLM WARNING] Rate limit hit. Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"[LLM ERROR] Diagnosis failed: {e}")
                return {}
    
    print("[LLM ERROR] Max retries reached.")
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
    # Fallback to rule engine if LLM fails (returns empty dict)
    merged = {
        "root_cause": llm_output.get("root_cause") or rule_result["root_cause"],
        "severity": rule_result["severity"], # Maintain rule-based severity for safety
        "explanation": llm_output.get("explanation") or rule_result["explanation"],
        "recommended_actions": llm_output.get("recommended_actions") or rule_result["recommended_actions"]
    }
    
    return merged

