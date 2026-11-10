import asyncio
import os
import time
import httpx
from dotenv import load_dotenv

load_dotenv()

async def main():
    api_key = os.getenv("GROQ_API_KEY")
    model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    if not api_key:
        print("ERROR: GROQ_API_KEY not found.")
        return

    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": "Reply with exactly: Groq connection successful"}
        ],
        "max_completion_tokens": 200,
        "temperature": 0
    }
    headers = {"Authorization": f"Bearer {api_key}"}
    start = time.perf_counter()

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload
        )

    print("HTTP status:", response.status_code)
    print("Elapsed seconds:", round(time.perf_counter() - start, 2))

    if response.is_success:
        data = response.json()
        print("Model:", data.get("model", model))
        print("Finish reason:", data["choices"][0].get("finish_reason"))
        print("Full choice:", data["choices"][0])
        print("Usage:", data.get("usage"))
    else:
        print("API error:", response.text[:1000])

asyncio.run(main())