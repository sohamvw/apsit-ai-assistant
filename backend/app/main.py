from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.chat import router as chat_router
from app.routes.ingestion import router as ingestion_router
from app.services.vector_service import create_collection
import os

app = FastAPI(title="APSIT AI Assistant")

# ----------------------------
# CORS Configuration
# ----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Later restrict to APSIT domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------
# Routers
# ----------------------------
app.include_router(chat_router)
app.include_router(ingestion_router)

# ----------------------------
# Startup Event
# ----------------------------
@app.on_event("startup")
async def startup_event():
    create_collection()

# ----------------------------
# Health Check
# ----------------------------
@app.get("/health")
async def health():
    return {"status": "ok"}

# ----------------------------
# Local Development Run
# ----------------------------
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)

@app.on_event("startup")
async def debug_qdrant():
    print("QDRANT_URL:", settings.QDRANT_URL)