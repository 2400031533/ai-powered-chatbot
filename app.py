
from datetime import datetime, timezone
from pathlib import Path
from contextlib import contextmanager
import json
import re
import sqlite3

from flask import Flask, jsonify, render_template, request

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "chatbot.db"

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False

FAQS = [
    {"question": "What are your business hours?", "answer": "Our support team is available Monday to Friday, 9:00 AM to 5:00 PM."},
    {"question": "How can I reset my password?", "answer": "Open the sign-in page and choose 'Forgot password'. If that option is unavailable, contact support."},
    {"question": "How do I contact support?", "answer": "You can contact support at support@example.com. Replace this demo address with your organization's real contact."},
    {"question": "How can I track my order?", "answer": "Sign in to your account and open the Orders page to see the latest status."},
    {"question": "What is your refund policy?", "answer": "Refund eligibility depends on the product and purchase date. Please contact support with your order number."},
    {"question": "Can I change my account email?", "answer": "Open Account Settings and update your email address. You may need to verify the new address."},
    {"question": "How do I create an account?", "answer": "Choose Sign Up on the website, enter the requested details, and follow the on-screen instructions."},
]

STOP_WORDS = {
    "a", "an", "the", "is", "are", "i", "me", "my", "you", "your",
    "to", "for", "of", "and", "how", "can", "do", "what", "please",
    "in", "on", "it", "with"
}


@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_message TEXT NOT NULL,
                bot_response TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)


def tokens(text):
    return {
        word
        for word in re.findall(r"[a-z0-9]+", text.lower())
        if word not in STOP_WORDS
    }


def find_answer(message):
    """Match the message against FAQ questions using token overlap."""
    message_tokens = tokens(message)

    if not message_tokens:
        return "Please type a little more detail so I can find the closest FAQ."

    best_faq, best_score = None, 0.0

    for faq in FAQS:
        faq_tokens = tokens(faq["question"] + " " + faq["answer"])
        union = message_tokens | faq_tokens
        score = (
            len(message_tokens & faq_tokens) / len(union)
            if union else 0.0
        )

        if score > best_score:
            best_faq, best_score = faq, score

    if best_faq and best_score >= 0.12:
        return best_faq["answer"]

    return (
        "I couldn't find a confident answer in my FAQs. Please contact "
        "support@example.com or try asking about hours, orders, refunds, "
        "account creation, or password help."
    )


def save_conversation(user_message, bot_response):
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO conversations
            (user_message, bot_response, created_at)
            VALUES (?, ?, ?)
            """,
            (
                user_message,
                bot_response,
                datetime.now(timezone.utc).isoformat()
            )
        )


@app.route("/")
def index():
    return render_template("index.html")


@app.post("/api/chat")
def chat():
    payload = request.get_json(silent=True) or {}
    message = str(payload.get("message", "")).strip()

    if not message:
        return jsonify({"error": "Please enter a message."}), 400

    if len(message) > 1000:
        return jsonify({
            "error": "Please keep messages under 1,000 characters."
        }), 400

    response = find_answer(message)
    save_conversation(message, response)

    return jsonify({"response": response})


@app.get("/api/history")
def history():
    with get_db() as conn:
        rows = conn.execute(
            """
            SELECT user_message, bot_response, created_at
            FROM conversations
            ORDER BY id DESC
            LIMIT 20
            """
        ).fetchall()

    return jsonify({"history": [dict(row) for row in rows]})


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


init_db()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
