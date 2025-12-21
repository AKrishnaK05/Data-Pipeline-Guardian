from google import genai
import json
import os
from dotenv import load_dotenv
from agent.prompts import FIX_PROMPT

load_dotenv()

# Configure Gemini
api_key = os.environ.get("GOOGLE_API_KEY")
client = genai.Client(api_key=api_key)

import time

def call_llm(prompt):
    max_retries = 1
    base_delay = 10

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash-exp", contents=prompt
            )
            # Handle potential markdown formatting from LLM (```json ... ```)
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
                print(f"[LLM ERROR] Failed to generate fix: {e}")
                return None
    
    print("[LLM ERROR] Max retries reached.")
    return None

def generate_fix_proposal(diagnosis):
    """
    Generate a fix using Google Gemini LLM.
    """
    prompt = FIX_PROMPT.format(
        root_cause=diagnosis["root_cause"],
        severity=diagnosis["severity"]
    )
    
    # print(f"[DEBUG] Asking Gemini for fix...")
    fix_proposal = call_llm(prompt)

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
