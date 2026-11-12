# Docuchat API

An AI-powered backend built with **FastAPI** where users sign up, chat with an LLM that remembers the conversation, and ask questions about their own documents. Every user's chats and documents are private to their account.

**Live demo (interactive API docs):** https://docuchat-api-production-fd955261.up.railway.app/docs

> The demo runs on a hosting trial. If the link is down, follow the [local setup](#getting-started) below to run it yourself.

## Features

- **User accounts:** signup and login with bcrypt-hashed passwords (nothing is stored in plain text)
- **JWT authentication:** protected endpoints accept only valid, unexpired tokens (30-minute expiry)
- **LLM chat with memory:** every message and reply is saved in MySQL, and the last 10 messages are sent to the model as context
- **Document Q&A:** submit a text document (up to 20,000 characters) and ask questions answered only from that document
- **Per-user data isolation:** users can read only their own history and documents
- **Input validation and error handling:** username and password rules, empty-input checks, and clear 502/504 responses when the LLM service fails or times out

## Tech Stack

| Area | Tools |
|---|---|
| Framework | FastAPI, Uvicorn |
| Database | MySQL (`mysql-connector-python`) |
| Authentication | PyJWT, bcrypt |
| LLM | Gemini API (called with `requests`) |
| Configuration | python-dotenv |
| Containerization | Docker |
| Hosting | Railway (app service + managed MySQL service) |

## API Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/signup` | No | Create an account |
| POST | `/login` | No | Log in and receive a JWT access token |
| POST | `/chat` | Yes | Send a message and get the LLM's reply |
| GET | `/history` | Yes | Get all your saved messages |
| POST | `/documents` | Yes | Save a text document and get its `id` |
| POST | `/documents/{doc_id}/ask` | Yes | Ask a question about one of your documents |

### Example usage

Replace `BASE_URL` with the live link or `http://127.0.0.1:8000`.

```bash
# 1. Create an account (password must be at least 8 characters)
curl -X POST BASE_URL/signup \
  -H "Content-Type: application/json" \
  -d '{"username": "meera", "password": "strongpass123"}'

# 2. Log in (form data) and copy the access_token from the response
curl -X POST BASE_URL/login \
  -d "username=meera&password=strongpass123"

# 3. Chat (use your token)
curl -X POST BASE_URL/chat \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!"}'

# 4. Save a document, then ask about it (use the returned id)
curl -X POST BASE_URL/documents \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Notes", "content": "FastAPI is a Python web framework."}'

curl -X POST BASE_URL/documents/1/ask \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is FastAPI?"}'
```

The easiest way to try it is the `/docs` page: click **Authorize**, log in, then use **Try it out** on any endpoint.

## Project Structure

```
.
├── main.py            # FastAPI app and all endpoints
├── auth.py            # Password hashing, JWT creation, current-user dependency
├── db.py              # MySQL connection, table creation, queries
├── llm.py             # Gemini API call with timeout and error handling
├── Dockerfile         # Container build instructions
├── requirements.txt   # Python dependencies
├── pyproject.toml     # uv project file
└── .env.example       # Template for environment variables
```

## Database

Three tables are created automatically on startup:

- `users`: `id`, `username`, `password_hash`
- `messages`: `id`, `user_id`, `role`, `text`, `created_at`
- `documents`: `id`, `user_id`, `title`, `content`

`messages` and `documents` link to `users` through `user_id` (foreign key).

## Getting Started

### 1. Clone and install

```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>
```

With **uv**:

```bash
uv sync
```

Or with **pip**:

```bash
pip install -r requirements.txt
```

### 2. Create the MySQL database

The app creates the tables itself, but the database must already exist:

```sql
CREATE DATABASE ai_project;
```

### 3. Set environment variables

Copy `.env.example` to `.env` and fill in your values:

```
SECRET_KEY=your_long_random_string
LLM_API_KEY=your_gemini_api_key
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_mysql_user
DB_PASSWORD=your_mysql_password
DB_NAME=ai_project
```

Generate a secure `SECRET_KEY`:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Never commit `.env`. It is listed in `.gitignore`.

### 4. Run the server

```bash
uvicorn main:app --reload
```

Open **http://127.0.0.1:8000/docs** for the interactive API docs.

## Deployment

The app is deployed on **Railway** from this GitHub repository, with a separate managed MySQL service in the same project. The database settings, `SECRET_KEY`, and `LLM_API_KEY` are set as environment variables in the hosting dashboard and are never committed. Every push to the main branch redeploys automatically.

## Security Notes

- Passwords are hashed with bcrypt and never stored or logged in plain text
- JWT tokens expire after 30 minutes
- All database queries use parameters, which protects against SQL injection
- Documents and history are filtered by the logged-in user's id

## Possible Improvements

- Retrieval-augmented generation (embeddings and vector search) for long documents
- Refresh tokens and rate limiting
- File upload support (PDF and text files)
- Automated tests

## Author

Built by **<Mahadeer Mohamed>** as a portfolio project in Python backend development and LLM integration.

[LinkedIn](https://www.linkedin.com/in/mahadeer-mohamed/) | [GitHub](https://github.com/mahadeermohamed)