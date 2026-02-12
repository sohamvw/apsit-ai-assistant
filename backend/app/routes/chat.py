from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from app.services.deep_search import deep_search
from app.services.llm_service import stream_answer

router = APIRouter(prefix="/chat", tags=["Chat"])


class ChatRequest(BaseModel):
    query: str


@router.post("/")
async def chat(req: ChatRequest):
    docs = deep_search(req.query)
    top_docs = docs[:4]

    async def generate():
        async for chunk in stream_answer(req.query, top_docs):
            yield chunk

    return StreamingResponse(generate(), media_type="text/plain")
