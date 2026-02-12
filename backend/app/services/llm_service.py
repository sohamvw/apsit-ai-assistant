from google import genai
from app.core.config import get_settings

settings = get_settings()
client = genai.Client(api_key=settings.GEMINI_API_KEY)


async def stream_answer(query: str, docs: list):

    context = "\n\n".join([d["text"] for d in docs])

    prompt = f"""
You are APSIT AI Assistant.

STRICT RULES:
1. Use ONLY the provided context.
2. If answer not found in context, say:
   "Information not available on APSIT website."
3. Answer clearly and precisely.
4. Do not make assumptions.

Answer format:

<Answer>

For more queries visit the college campus or contact us.

Context:
{context}

Question:
{query}
"""

    response = client.models.generate_content_stream(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    for chunk in response:
        if chunk.text:
            yield chunk.text







'''from google import genai
from app.core.config import get_settings

settings = get_settings()
client = genai.Client(api_key=settings.GEMINI_API_KEY)


async def stream_answer(query: str, docs: list):

    context = "\n\n".join([d["text"] for d in docs])

    prompt = f"""
You are APSIT AI Assistant.

Use ONLY the provided context to answer.

Context:
{context}

Question:
{query}
"""

    response = client.models.generate_content_stream(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    for chunk in response:
        if chunk.text:
            yield chunk.text
'''