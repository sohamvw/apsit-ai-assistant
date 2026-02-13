from google import genai
from app.core.config import get_settings

settings = get_settings()
client = genai.Client(api_key=settings.GEMINI_API_KEY)


async def stream_answer(query: str, docs: list):

    context = "\n\n".join([d["text"] for d in docs])

    prompt = f"""
You are APSIT AI Assistant.

STRICT RULES:
1.  Answer ONLY using the provided context.
2. Do NOT add external knowledge.
3. If answer is not found, say politely that information is not available on the official website.
4. Detect the language of the user's question and reply in the SAME language.
5. At the end of every answer, add a polite footer line in the SAME language meaning:
   "For more queries visit the college campus or contact us at 91XXXXXXXX.

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