from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.chat import router as chat_router
from app.routes.ingestion import router as ingestion_router




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


@app.get("/health")
async def health():
    return {"status": "ok"}




'''from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.chat import router as chat_router
from app.routes.ingestion import router as ingestion_router
from app.services.vector_service import create_collection
import asyncio

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
    print("🚀 Server starting...")
    try:
        await asyncio.to_thread(create_collection)
        print("✅ Qdrant collection ready")
    except Exception as e:
        print("❌ Failed to create collection:", str(e))


@app.get("/health")
async def health():
    return {"status": "ok"}
'''