from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.chat import router as chat_router
from app.services.vector_service import create_collection

app = FastAPI(title="APSIT AI Assistant")

# CORS (so website can call backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # later restrict to APSIT domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/chat")


@app.on_event("startup")
async def startup_event():
    create_collection()


@app.get("/health")
async def health():
    return {"status": "ok"}
