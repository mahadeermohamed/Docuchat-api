from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from llm import call_llm
from auth import hash_password, check_password, create_token, get_current_user
from db import (
    init_db, create_user, get_user,
    save_message, get_all_messages, get_last_messages,
    save_document, get_document,
)

app = FastAPI()
init_db()


# AUTH
class SignupRequest(BaseModel):
    username: str
    password: str


@app.post("/signup")
def signup(req: SignupRequest):
    username = req.username.strip()
    if not username or len(username) > 50:
        raise HTTPException(status_code=400, detail="Username must be 1-50 characters")
    if len(req.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    if len(req.password.encode()) > 72:
        raise HTTPException(status_code=400, detail="Password is too long (max 72 bytes)")
    user_id = create_user(username, hash_password(req.password))
    if user_id is None:
        raise HTTPException(status_code=400, detail="Username already taken")
    return {"message": "Account created"}


@app.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends()):
    user = get_user(form.username)
    if not user or not check_password(form.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Wrong username or password")
    return {"access_token": create_token(user["username"]), "token_type": "bearer"}


# MESSAGE HISTORY
class ChatRequest(BaseModel):
    message: str


@app.post("/chat")
def chat(req: ChatRequest, user: dict = Depends(get_current_user)):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    save_message(user["id"], "user", req.message)

    history = get_last_messages(user["id"], 10)
    while history and history[0]["role"] == "model":
        history.pop(0)

    reply = call_llm(history)
    save_message(user["id"], "model", reply)
    return {"reply": reply}


@app.get("/history")
def history_endpoint(user: dict = Depends(get_current_user)):
    return get_all_messages(user["id"])


# DOCUMENT Q&A
class DocRequest(BaseModel):
    title: str
    content: str


class AskRequest(BaseModel):
    question: str


@app.post("/documents")
def add_document(req: DocRequest, user: dict = Depends(get_current_user)):
    if not req.title.strip() or not req.content.strip():
        raise HTTPException(status_code=400, detail="Title and content cannot be empty")
    if len(req.content) > 20000:
        raise HTTPException(status_code=400, detail="Document is too long. Please upload a shorter one.")
    doc_id = save_document(user["id"], req.title, req.content)
    return {"id": doc_id}


@app.post("/documents/{doc_id}/ask")
def ask_document(doc_id: int, req: AskRequest, user: dict = Depends(get_current_user)):
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    doc = get_document(doc_id, user["id"])
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    prompt = f"""Answer only using the document below.
If the answer is not in the document, say "I couldn't find that in the document."

Document:
{doc['content']}

Question: {req.question}"""

    reply = call_llm([{"role": "user", "text": prompt}])
    return {"answer": reply}