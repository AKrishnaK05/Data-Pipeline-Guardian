import json
from agent.rule_engine import rule_based_diagnosis

USE_LLM = False

def run_guardian_agent(anomaly_record, baseline):
    """
    anomaly_record: dict with keys
    - row_count
    - null_ratio
    - late_event_ratio
    - schema_change_flag
    - anomaly_score
    
    baseline: dict with keys
    - row_count_mean
    - null_ratio_mean
    - late_event_ratio_mean
    """

    rule_result = rule_based_diagnosis(anomaly_record, baseline)

    if not USE_LLM:
        return rule_result

    # full_prompt = DIAGNOSIS_PROMPT + format_context(anomaly_record)
    # llm_response = call_local_llm(full_prompt)
    # merged_result = merge(rule_result,llm_response)
    # return merged_result

    return rule_result

