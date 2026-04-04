# ============================================================
#   reset_emails.py
#   Resets all AI fields in emails.json back to null
#   Run this anytime you want to reprocess all emails fresh
#
#   Usage:
#       python reset_emails.py
# ============================================================

import json

EMAILS_FILE = "data/emails.json"

with open(EMAILS_FILE, "r") as f:
    emails = json.load(f)

for email in emails:
    email["category"]    = None
    email["summary"]     = None
    email["draft_reply"] = None
    email["status"]      = "unread"

with open(EMAILS_FILE, "w") as f:
    json.dump(emails, f, indent=2)

print(f"Reset complete — {len(emails)} emails cleared and ready to process!")
