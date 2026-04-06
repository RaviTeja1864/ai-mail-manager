# ============================================================
#   config.py — API key & app settings
#   AI Email Manager (Academic Project)
# ============================================================

# ── Local ollama model settings ────────────────────────────
OLLAMA_BINARY = "ollama"
OLLAMA_MODEL  = "qwen2.5-coder:3b-instruct-q4_K_M"
OLLAMA_ARGS   = ["--hidethinking", "--format", "json"]

# ── Flask settings ───────────────────────────────────────────
DEBUG = True
PORT  = 5000

# ── File paths ───────────────────────────────────────────────
EMAILS_FILE  = "data/emails.json"
REPLIES_FILE = "data/replies.json"

# ── Email categories & their badge colours (used in UI) ──────
CATEGORY_COLORS = {
    "spam"        : "red",
    "urgent"      : "orange",
    "work"        : "blue",
    "personal"    : "green",
    "newsletter"  : "purple",
    "unknown"     : "gray",
}
