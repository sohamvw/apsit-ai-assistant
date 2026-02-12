from fastapi import APIRouter, BackgroundTasks
from app.services.ingestion_service import run_ingestion

router = APIRouter(prefix="/ingest", tags=["Ingestion"])


@router.post("/")
def ingest(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_ingestion)
    return {"status": "ingestion started in background"}
