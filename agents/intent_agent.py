import os
import json
from pathlib import Path
from groq import Groq
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def extract_trip_details(user_message: str, conversation_context: str = "") -> dict:
    """
    Use an LLM to parse a free-text trip request into structured fields
    the recommendation pipeline needs.
    """
    prompt = f"""You are a travel planning assistant. Extract trip details from the user's message
and return ONLY a valid JSON object, nothing else — no explanation, no markdown formatting.

Conversation so far (for context, may be empty):
{conversation_context}

User's latest message: "{user_message}"

Return JSON with these exact keys (use null for anything not mentioned or not yet known):
{{
    "destination": string or null,
    "state": string or null,
    "origin_place": string or null,
    "num_days": integer or null,
    "total_budget": number or null,
    "interests": array of strings from ["nature","adventure","heritage","spiritual","family"] or empty array,
    "home_language": string or null,
    "destination_language": string or null,
    "ready_to_search": boolean (true only if destination, num_days, and total_budget are all known)
}}"""

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0,
        )
        raw = response.choices[0].message.content.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(raw)
    except Exception as e:
        return {
            "destination": None, "state": None, "origin_place": None,
            "num_days": None, "total_budget": None, "interests": [],
            "home_language": None, "destination_language": None,
            "ready_to_search": False, "parse_error": str(e),
        }


def merge_details(old: dict, new: dict) -> dict:
    """Merge newly extracted fields into what we already know, without erasing prior answers."""
    merged = dict(old)
    for key, value in new.items():
        if key == "interests":
            combined = list(set((old.get("interests") or []) + (value or [])))
            merged["interests"] = combined
        elif value not in (None, "", []):
            merged[key] = value
    return merged


def missing_fields_message(details: dict) -> str:
    """Generate a friendly follow-up question for whatever's still missing."""
    missing = []
    if not details.get("destination"):
        missing.append("where you'd like to go")
    if not details.get("num_days"):
        missing.append("how many days you're planning to travel")
    if not details.get("total_budget"):
        missing.append("your budget for entry fees")

    if not missing:
        return ""

    return "Could you tell me " + ", and ".join(missing) + "?"


if __name__ == "__main__":
    result = extract_trip_details("I want to visit Ooty for 3 days with a 5000 rupee budget, I like nature and spiritual places")
    print(json.dumps(result, indent=2))