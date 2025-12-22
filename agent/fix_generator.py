import json
import os
from dotenv import load_dotenv
from agent.prompts import FIX_PROMPT

load_dotenv()

from agent.llm_client import call_llm_hybrid

def generate_fix_proposal(diagnosis):
    """
    Generate a fix using Google Gemini LLM.
    """
    prompt = FIX_PROMPT.format(
        root_cause=diagnosis["root_cause"],
        severity=diagnosis["severity"]
    )
    
    # print(f"[DEBUG] Asking Gemini for fix...")
    fix_proposal = call_llm_hybrid(prompt)

    if fix_proposal:
        return fix_proposal
    
    # Fallback if LLM fails (e.g. Rate Limits)
    print("\n[WARN] LLM Generation failed. Using fallback fix strategy.")
    rc = diagnosis.get("root_cause", "").lower()
    
    if "late" in rc or "watermark" in rc:
        return {
            "title": "Increase Watermark (Fallback)",
            "explanation": "Simulated fix due to LLM unavailability. Increasing watermark to 20m.",
            "risk": "medium",
            "diff": "PIPELINE_CONFIG['watermark_minutes'] = 20"
        }
    
    return None

def apply_fix(fix):
    """
    Simulate fix execution by updating runtime config.
    """
    from pipeline.runtime_config import PIPELINE_CONFIG

    if "watermark" in fix["title"].lower():
        PIPELINE_CONFIG["watermark_minutes"] = 20
        print("\n[SUCCESS] FIX APPLIED (SIMULATED)")
        print("Watermark updated to 20 minutes\n")
