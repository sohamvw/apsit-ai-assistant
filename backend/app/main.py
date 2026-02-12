from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.chat import router as chat_router
from app.routes.ingestion import router as ingestion_router
from app.services.vector_service import create_collection
import os

app = FastAPI(title="APSIT AI Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)
app.include_router(ingestion_router)


@app.on_event("startup")
async def startup_event():
    create_collection()


@app.get("/health")
async def health():
    return {"status": "ok"}
