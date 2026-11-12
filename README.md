# AI Chat & Document Q&A API

A backend API built with **FastAPI** that lets users sign up, log in, chat with an LLM (with saved conversation history), and ask questions about documents they upload. Each user's chats and documents are private to their account.

## Features

- **User accounts:** signup and login with bcrypt-hashed passwords
- **JWT authentication:** protected endpoints accept only valid, unexpired tokens (30-minute expiry)
- **LLM chat with memory:** every message and reply is saved in MySQL, and the last 10 messages are sent to the model as context
- **Document Q&A:** upload a text document and ask questions answered only from that document
- **Per-user data isolation:** users can only read their own history and documents
- **Clean error handling:** input validation, plus clear 502/504 errors when the LLM service fails or times out

## Tech Stack

| Area | Tools |
|---|---|
| Framework | FastAPI, Uvicorn |
| Database | MySQL (`mysql-connector-python`) |
| Auth | PyJWT, bcrypt |
| LLM | Gemini API (called with `requests`) |
| Config | python-dotenv |
| Package manager | uv |

## Project Structure

```
.
├── main.py      # FastAPI app and all endpoints
├── auth.py      # Password hashing, JWT creation, current-user dependency
├── db.py        # MySQL connection, table creation, queries
├── llm.py       # Gemini API call with error handling
├── .env         # Secrets (never committed)
└── pyproject.toml
```

## Getting Started

### 1. Clone and install dependencies

```bash
git clone <your-repo-url>
cd <your-repo-folder>
uv sync
```

Starting from scratch instead? Install the packages directly:

```bash
uv add fastapi uvicorn mysql-connector-python python-dotenv bcrypt pyjwt python-multipart requests
```

### 2. Create the MySQL database

The app creates the tables automatically, but the database itself must exist. In MySQL Workbench or the MySQL shell, run:

```sql
CREATE DATABASE ai_project;
```

### 3. Configure environment variables

Create a `.env` file in the project root:

```
SECRET_KEY=your_long_random_string
LLM_API_KEY=your_gemini_api_key
DB_HOST=localhost
DB_USER=your_mysql_user
DB_PASSWORD=your_mysql_password
DB_NAME=ai_project
```

Generate a secure `SECRET_KEY` with:

```bash
uv run python -c "import secrets; print(secrets.token_hex(32))"
```

Never commit `.env` to GitHub. Make sure it is listed in `.gitignore`.

### 4. Run the server

```bash
uv run uvicorn main:app --reload
```

Open the interactive API docs at **http://127.0.0.1:8000/docs**.

## API Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/signup` | No | Create an account |
| POST | `/login` | No | Log in and receive a JWT access token |
| POST | `/chat` | Yes | Send a message and get the LLM's reply |
| GET | `/history` |