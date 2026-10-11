# AI-Powered Chatbot

A responsive customer-support chatbot built with Flask, Python, HTML, CSS, lightweight NLP-style token matching, and SQLite conversation logs.

## Features
- FAQ-based contextual matching using normalized tokens and Jaccard similarity.
- Chat interface with input validation.
- Stores messages and responses in SQLite.
- Recent conversation history endpoint (`GET /api/history`).
- Health endpoint (`GET /health`).
- Unit tests.

## Run locally
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000

On macOS/Linux, activate with `source .venv/bin/activate`.

## Test
```bash
python -m unittest discover -s tests -v
```

## API
- `POST /api/chat` JSON: `{"message":"How do I track my order?"}`
- `GET /api/history`
- `GET /health`

## Important clarification
This starter project uses local FAQ matching, not a large language model. For a stronger AI version, add a trained NLP model or an approved hosted model API and document its requirements and privacy implications.
