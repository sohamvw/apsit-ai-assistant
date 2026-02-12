from google import genai
from app.core.config import get_settings

settings = get_settings()

client = genai.Client(api_key=settings.GEMINI_API_KEY)


async def stream_answer(query: str, context: list):

    formatted_context = "\n\n".join(context)

    prompt = f"""
You are the official APSIT AI Assistant.

Only use the provided context to answer.

Context:
{formatted_context}

Question:
{query}

Answer clearly and accurately.

At the end always add:
"For more queries visit the college campus or contact us."
"""

    response = client.models.generate_content(
        model="models/gemini-2.5-flash",
        contents=prompt
    )

    yield response.text
