import google.generativeai as genai
import json
import os
from agent.prompts import FIX_PROMPT

# Configure Gemini
# In production, use os.environ["GOOGLE_API_KEY"]
api_key = "AIzaSyA5D5b08MQ5OcMFt25kv7_kIl8uLVpfAyA"
genai.configure(api_key=api_key)

def call_llm(prompt):
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        # Handle potential markdown formatting from LLM (```json ... ```)
        text = response.text
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        return json.loads(text)
    except Exception as e:
        print(f"[LLM ERROR] Failed to generate fix: {e}")
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
    return call_llm(prompt)

def apply_fix(fix):
    """
    Simulate fix execution by updating runtime config.
    """
    from pipeline.runtime_config import PIPELINE_CONFIG

    if "watermark" in fix["title"].lower():
        PIPELINE_CONFIG["watermark_minutes"] = 20
        print("\n[SUCCESS] FIX APPLIED (SIMULATED)")
        print("Watermark updated to 20 minutes\n")
