from fastapi import FastAPI
from app.routes.chat import router as chat_router

app = FastAPI(title="APSIT AI Assistant")

app.include_router(chat_router, prefix="/chat")


@app.get("/health")
async def health():
    return {"status": "ok"}
