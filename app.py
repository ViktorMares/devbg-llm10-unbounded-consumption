from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from agent import run_agent
import time

app = FastAPI()

class ChatRequest(BaseModel):
    prompt: str

@app.post("/chat")
def chat(req: ChatRequest):
    start = time.time()
    try:
        response = run_agent(req.prompt)
        status = "ok"
    except Exception:
        response = (
            "The system ran into an internal error. "
            "This usually happens under heavy load."
        )
        status = "error"

    return {
        "status": status,
        "response": response,
        "elapsed_ms": int((time.time() - start) * 1000),
    }

app.mount("/", StaticFiles(directory="static", html=True), name="static")
