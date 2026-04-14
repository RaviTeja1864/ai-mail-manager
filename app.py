# ============================================================
#   app.py — Flask backend
#   AI Email Manager (Academic Project)
# ============================================================

import json
import os
import time
from flask import Flask, render_template, request, redirect, url_for, flash

from config import DEBUG, PORT, EMAILS_FILE, REPLIES_FILE, CATEGORY_COLORS
from services.ai_processor import process_email

app = Flask(__name__)
app.secret_key = "ai-email-manager-secret-2026"

# ── How many emails to process per click ─────────────────────
BATCH_SIZE = 3

# ── Helper: load / save JSON ─────────────────────────────────

def load_emails():
    with open(EMAILS_FILE, "r") as f:
        return json.load(f

def save_emails(emails):
    with open(EMAILS_FILE, "w") as f:
        json.dump(emails, f, indent=2)

def load_replies():
    if not os.path.exists(REPLIES_FILE):
        return []
    with open(REPLIES_FILE, "r") as f:
        return json.load(f)

def save_replies(replies):
    with open(REPLIES_FILE, "w") as f:
        json.dump(replies, f, indent=2)

# ── Route 1: Inbox Dashboard ─────────────────────────────────

@app.route("/")
def inbox():
    emails = load_emails()

    total      = len(emails)
    unread     = sum(1 for e in emails if e["status"] == "unread")
    processed  = sum(1 for e in emails if e["category"] is not None)
    spam_count = sum(1 for e in emails if e["category"] == "spam")
    pending    = sum(1 for e in emails if e["category"] is None)

    stats = {
        "total"    : total,
        "unread"   : unread,
        "processed": processed,
        "spam"     : spam_count,
        "pending"  : pending,
    }

    return render_template(
        "index.html",
        emails=emails,
        stats=stats,
        category_colors=CATEGORY_COLORS
    )

# ── Route 2: Single Email Detail ─────────────────────────────

@app.route("/email/<int:email_id>")
def email_detail(email_id):
    emails = load_emails()
    email  = next((e for e in emails if e["id"] == email_id), None)

    if not email:
        flash("Email not found.", "error")
        return redirect(url_for("inbox"))

    if email["status"] == "unread":
        email["status"] = "read"
        save_emails(emails)

    return render_template(
        "email.html",
        email=email,
        category_colors=CATEGORY_COLORS
    )

# ── Route 3: Process Next 3 Emails with AI ───────────────────

@app.route("/process", methods=["POST"])
def process_all():
    emails = load_emails()
    processed_count = 0

    # Get only unprocessed emails
    pending_emails = [e for e in emails if e["category"] is None]

    if not pending_emails:
        flash("All emails are already processed!", "info")
        return redirect(url_for("inbox"))

    # Only process next BATCH_SIZE emails
    batch = pending_emails[:BATCH_SIZE]

    for email in batch:
        try:
            result = process_email(
                email["from"],
                email["subject"],
                email["body"]
            )

            email["category"]    = result["category"]
            email["summary"]     = result["summary"]
            email["draft_reply"] = result["draft_reply"]

            processed_count += 1
            print(f"✅ Email {email['id']} → {result['category']}")

        except Exception as e:
            email["category"]    = "unknown"
            email["summary"]     = f"Could not process: {str(e)}"
            email["draft_reply"] = ""
            print(f"❌ Email {email['id']} error: {str(e)}")

        # Save after every email
        save_emails(emails)

        # Wait between emails to respect rate limit
        time.sleep(5)

    remaining = sum(1 for e in emails if e["category"] is None)

    if remaining > 0:
        flash(f"✅ Processed {processed_count} emails. {remaining} emails still pending — click Run AI again!", "success")
    else:
        flash(f"✅ All emails processed successfully!", "success")

    return redirect(url_for("inbox"))

# ── Route 4: Approve Draft Reply ─────────────────────────────

@app.route("/approve/<int:email_id>", methods=["POST"])
def approve_reply(email_id):
    emails  = load_emails()
    replies = load_replies()

    email = next((e for e in emails if e["id"] == email_id), None)

    if email and email.get("draft_reply"):
        replies.append({
            "email_id"   : email_id,
            "to"         : email["from"],
            "subject"    : "Re: " + email["subject"],
            "reply_body" : email["draft_reply"],
            "status"     : "approved"
        })
        save_replies(replies)
        flash("Reply approved and saved!", "success")
    else:
        flash("No draft reply found to approve.", "error")

    return redirect(url_for("email_detail", email_id=email_id))

# ── Route 5: Reject Draft Reply ──────────────────────────────

@app.route("/reject/<int:email_id>", methods=["POST"])
def reject_reply(email_id):
    emails = load_emails()
    email  = next((e for e in emails if e["id"] == email_id), None)

    if email:
        email["draft_reply"] = None
        save_emails(emails)
        flash("Draft reply rejected.", "info")
    else:
        flash("Email not found.", "error")

    return redirect(url_for("email_detail", email_id=email_id))

# ── Run ──────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=DEBUG, port=PORT)
