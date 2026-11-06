from pydoc import doc
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typer import prompt
from llm import call_llm
from db import init_db, save_message, get_all_messages, get_last_messages, save_document, get_document
app = FastAPI()
init_db()

class ChatRequest(BaseModel):
    message: str

    # MESSAGE HISTORY
@app.post("/chat")
def chat(req: ChatRequest):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    save_message("User", req.message)

    history = get_last_messages(10)
    while history and history[0]["role"] == "model":
        history.pop(0)

    reply = call_llm(history)
    save_message("model", reply)
    return {"reply": reply}

@app.get("/history")
def history_endpoint():
    return get_all_messages()

# DOCUMENT Q&A
class DocRequest(BaseModel):
    title: str
    content: str

class AskRequest(BaseModel):
    question: str

@app.post("/documents")
def add_document(req: DocRequest):
    if not req.title.strip() or not req.content.strip():
        raise HTTPException(status_code=400, detail="Title and content cannot be empty")
    if len(req.content) > 20000:
        raise HTTPException(status_code=400, detail="Document is too long. Please upload a shorter one.")
    doc_id = save_document(req.title, req.content)
    return {"id": doc_id}

@app.post("/documents/{doc_id}/ask")
def ask_document(doc_id: int, req: AskRequest):
    if not req.question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    doc = get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    prompt = f"""Answer only using the document below.
If the answer is not in the document, say "I couldn't find that in the document."

Document:
{doc[2]}

Question: {req.question}"""
    
    reply = call_llm([{"role": "user", "text": prompt}])
    return {"answer": reply}