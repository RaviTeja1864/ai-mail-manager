# ============================================================
#   services/ai_processor.py
#   Local ollama call per email — returns category, summary
#   and draft reply all at once
#   This keeps the app offline and avoids external API usage
# ============================================================

import json
import os
import re
import subprocess
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import OLLAMA_ARGS, OLLAMA_BINARY, OLLAMA_MODEL, CATEGORY_COLORS


def _run_local_model(prompt: str) -> str:
    try:
        completed = subprocess.run(
            [OLLAMA_BINARY, "run", *OLLAMA_ARGS, OLLAMA_MODEL, prompt],
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        stderr = exc.stderr.strip() if exc.stderr else ""
        raise RuntimeError(f"ollama failed: {stderr or exc}") from exc

    return completed.stdout.strip()


def process_email(sender: str, subject: str, body: str) -> dict:
    """
    Local ollama model call that returns category, summary and draft reply.
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

    raw = _run_local_model(prompt)

    # Remove any markdown or terminal control sequences, then normalize whitespace.
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    raw = re.sub(r"\x1B[@-_][0-?]*[ -/]*[@-~]", "", raw)
    raw = raw.replace("\r", " ").replace("\n", " ").strip()

    try:
        result = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid JSON from ollama: {exc}; raw output: {raw[:500]}") from exc

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
