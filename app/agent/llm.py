from groq import Groq
from app.config import settings

def call_llm(prompt: str) -> str:
    if not settings.groq_api_key:
        raise RuntimeError("GROQ_API_KEY is required to make LLM calls.")

    client = Groq(api_key=settings.groq_api_key)

    response = client.chat.completions.create(
        model=settings.groq_model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    return response.choices[0].message.content