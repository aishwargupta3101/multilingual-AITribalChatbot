
import asyncio
import logging
from ollama import AsyncClient

logging.basicConfig(level=logging.INFO)

async def test_ollama():
    client = AsyncClient(
        host="http://127.0.0.1:11434",
        timeout=300.0
    )

    messages = [
        {
            "role": "system",
            "content": "You are a helpful multilingual AI assistant for a Tribal AI chatbot."
        },
        {
            "role": "user",
            "content": """
You are Tribal AI, a professional multilingual AI assistant.

Answer the user's question accurately, clearly, and helpfully.
Do not fabricate facts.
Generate the answer ONLY in English.

USER QUESTION:
what is ai

FINAL ANSWER:
"""
        }
    ]

    try:
        print("Sending request to Ollama...")

        response = await client.chat(
            model="llama3:latest",
            messages=messages,
            stream=False,
            options={
                "temperature": 0.2,
                "top_p": 0.9,
                "num_predict": 128
            }
        )

        print("\nSUCCESS")
        print(response.message.content)

    except Exception as error:
        print("\nFAILED")
        print(type(error).__name__)
        print(repr(error))

if __name__ == "__main__":
    asyncio.run(test_ollama())