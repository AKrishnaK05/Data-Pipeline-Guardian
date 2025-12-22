import os
import json
import time
import requests
from google import genai
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
api_key = os.environ.get("GOOGLE_API_KEY")
gemini_client = None
if api_key:
    gemini_client = genai.Client(api_key=api_key)

def clean_json_text(text):
    """Extracts JSON from markdown code blocks if present."""
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0]
    elif "```" in text:
        text = text.split("```")[1].split("```")[0]
    return text.strip()

def call_gemini(prompt, model="gemini-2.0-flash-exp"):
    if not gemini_client:
        return None
        
    retries = 3
    backoff = 2

    for attempt in range(retries):
        try:
            response = gemini_client.models.generate_content(
                model=model, contents=prompt
            )
            text = clean_json_text(response.text)
            return json.loads(text)
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str or "503" in error_str:
                if attempt < retries - 1:
                    sleep_time = backoff * (2 ** attempt)
                    print(f"[LLM INFO] Rate limit hit (429). Retrying in {sleep_time}s...")
                    time.sleep(sleep_time)
                    continue
                else:
                    print(f"[LLM WARNING] Gemini Rate Limit Exceeded after {retries} attempts.")
            else:
                print(f"[LLM ERROR] Gemini Failed: {e}")
                break # Don't retry other errors
                
    return None

def call_ollama(prompt, model="gemma3:1b"):
    """
    Attempts to call a local Ollama instance running on port 11434.
    """
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model, 
        "prompt": prompt + "\n\nIMPORTANT: Respond with VALID JSON ONLY. Do not write any introduction or explanation.",
        "stream": False,
        "format": "json",
        "options": {
            "temperature": 0.1
        }
    }
    
    try:
        # Timeout increased to 30s to allow model loading time
        r = requests.post(url, json=payload, timeout=30)
        if r.status_code == 200:
            response_json = r.json()
            text = response_json.get("response", "")
            return json.loads(text)
    except requests.exceptions.ConnectionError:
        print("[LLM INFO] Local Ollama not reachable (Connection Refused).")
        pass
    except Exception as e:
        print(f"[LLM ERROR] Local LLM Failed: {e}")
            
    return None

def call_llm_hybrid(prompt):
    """
    Tiered LLM Strategy:
    1. Google Gemini (Cloud)
    2. Ollama (Local)
    3. Return None (Trigger hardcoded fallback)
    """
    
    # Tier 1: Gemini
    result = call_gemini(prompt)
    if result:
        return result
        
    # Tier 2: Local LLM
    print("\n[BACKUP] Switching to Local LLM (Ollama)...")
    result = call_ollama(prompt)
    if result:
        print("[SUCCESS] Local LLM responded.")
        return result
        
    print("[WARN] Local LLM failed or not running.")
    return None
