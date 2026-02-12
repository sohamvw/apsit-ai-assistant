import google.generativeai as genai
from app.core.config import get_settings

settings = get_settings()
genai.configure(api_key=settings.GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-1.5-pro")


async def stream_answer(query: str, context: list):
    prompt = f"""
    You are the official APSIT AI assistant.
    Only use the provided context.

    Context:
    {context}

    Question:
    {query}
    """

    response = model.generate_content(prompt, stream=True)

    for chunk in response:
        if chunk.text:
            yield chunk.text
