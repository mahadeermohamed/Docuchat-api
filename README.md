# AI Chat & Document Q&A API

A FastAPI backend that lets you chat with an LLM (with conversation memory) and ask questions about your own documents. Messages and documents are stored in SQLite.

## Features
- Chat endpoint with conversation memory (last 10 messages are sent as context)
- Upload a document and ask questions answered only from its content
- Full chat history stored in SQLite
- Input validation and clean error responses (400, 404, 502, 504)

## Tech stack
Python, FastAPI, SQLite (`sqlite3`), Pydantic, Gemini API, python-dotenv, uv

## Project structure
```
main.py          # FastAPI app and endpoints
llm.py           # LLM API call and error handling
db.py            # SQLite setup and queries
.env.example     # Template for environment variables
pyproject.toml   # Dependencies
```

## Setup
1. Clone the repo
2. Copy `.env.example` to `.env` and add your Gemini API key:
   ```
   LLM_API_KEY=your_key_here
   ```
3. Install dependencies and run:
   ```bash
   uv sync
   uv run uvicorn main:app --reload
   ```
4. Open `http://localhost:8000/docs` to try the endpoints in the browser

## API endpoints

| Method | Path | Description |
|---|---|---|
| POST | `/chat` | Send a message, get a reply with conversation memory |
| GET | `/history` | Return all saved messages |
| POST | `/documents` | Save a document (max 20,000 characters) |
| POST | `/documents/{id}/ask` | Ask a question about a saved document |

### Example: chat
Request:
```json
POST /chat
{ "message": "My name is Aizen sosuke" }
```
Response:
```json
{ "reply": "Nice to meet you, Aizen sosuke! How can I help you today?" }
```

### Example: document Q&A
Save a document:
```json
POST /documents
{ "title": "Resume", "content": "Aizen sosuke knows Python, FastAPI and SQL." }
```
Response:
```json
{ "id": 1 }
```
Ask a question:
```json
POST /documents/1/ask
{ "question": "What skills does Aizen sosuke have?" }
```
Response:
```json
{ "answer": "Aizen sosuke knows Python, FastAPI and SQL." }
```
If the answer isn't in the document, the API replies: "I couldn't find that in the document."

## Error handling
| Status | Meaning |
|---|---|
| 400 | Empty message, title, content, or question; document too long |
| 404 | Document not found |
| 502 | LLM service unavailable or returned an unexpected response |
| 504 | LLM service timed out |

## Current limitations
- One shared conversation for all users (no authentication yet)
- Whole document is sent in the prompt, so very long documents are rejected

## Planned improvements
- User signup and login
- Embeddings-based search for longer documents
- Docker and live deployment

## What I learned
Building REST APIs with FastAPI, storing data with SQLite, integrating an LLM API, managing conversation memory, and grounding answers in a document.