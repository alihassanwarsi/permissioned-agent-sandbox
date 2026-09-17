from groq import Groq
from app.config import settings

client = Groq(api_key=settings.groq_api_key)

def call_llm(prompt: str) -> str:

    response = client.chat.completions.create(
        model=settings.groq_model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    return response.choices[0].message.content