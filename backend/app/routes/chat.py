from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from app.services.deep_search import deep_search
from app.services.llm_service import stream_answer

router = APIRouter(prefix="/chat", tags=["Chat"])

# Simple in-memory session storage
SESSION_MEMORY = {}
MAX_HISTORY = 5


class ChatRequest(BaseModel):
    query: str
    session_id: str


@router.post("/")
async def chat(req: ChatRequest):

    history = SESSION_MEMORY.get(req.session_id, [])

    docs = deep_search(req.query)
    top_docs = docs[:6]

    history.append({"role": "user", "content": req.query})
    SESSION_MEMORY[req.session_id] = history[-MAX_HISTORY:]

    async def generate():
        async for chunk in stream_answer(req.query, top_docs):
            yield chunk

    return StreamingResponse(generate(), media_type="text/plain")
