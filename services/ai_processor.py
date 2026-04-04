# ============================================================
#   services/ai_processor.py
#   Single API call per email — returns category, summary
#   and draft reply all at once
#   This reduces API calls from 3 per email to 1 per email
#   60 calls → 20 calls for all 20 emails
# ============================================================

from google import genai
import json
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import GEMINI_API_KEY, MODEL, CATEGORY_COLORS

client = genai.Client(api_key=GEMINI_API_KEY)

def process_email(sender: str, subject: str, body: str) -> dict:
    """
    Single API call that returns category, summary and draft reply.
    Returns a dict with keys: category, summary, draft_reply
    """

    prompt = f"""You are an AI email assistant. Analyze the email below and respond with ONLY a valid JSON object — no explanation, no markdown, no code block.

The JSON must have exactly these 3 keys:
1. "category": one word only — spam, urgent, work, personal, or newsletter
2. "summary": exactly 2 sentences — what the email is about and what action is needed
3. "draft_reply": a short polite reply of 3-5 sentences. Use empty string "" if category is spam.

Email:
From: {sender}
Subject: {subject}
Body: {body}

Respond with only the JSON object:"""

    response = client.models.generate_content(model=MODEL, contents=prompt)
    raw = response.text.strip()

    # Clean up markdown code blocks if model wraps in them
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    result = json.loads(raw)

    # Validate category
    if result.get("category") not in CATEGORY_COLORS:
        result["category"] = "unknown"

    # Ensure all keys exist
    result.setdefault("summary", "")
    result.setdefault("draft_reply", "")

    # No draft reply for spam
    if result["category"] == "spam":
        result["draft_reply"] = ""

    return result


if __name__ == "__main__":
    test = process_email(
        "boss@company.com",
        "Urgent meeting today",
        "Please join the call at 3 PM today regarding the client demo."
    )
    print(json.dumps(test, indent=2))
