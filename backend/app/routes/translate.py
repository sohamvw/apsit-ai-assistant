from fastapi import APIRouter
from app.services.llm_service import model
import json

router = APIRouter()

@router.post("/translate/")
async def translate_text(req: dict):
    texts = req.get("texts")
    language = req.get("language")

    prompt = f"""
    Translate the following list into {language}.
    Return ONLY a valid JSON array.
    {texts}
    """

    response = model.generate_content(prompt)

    try:
        translations = json.loads(response.text)
    except:
        translations = texts

    return {"translations": translations}
