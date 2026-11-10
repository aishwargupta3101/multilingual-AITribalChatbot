
import asyncio
from langchain_core.messages import HumanMessage
from backend.llm.groq_client import GroqLLM
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env", override=True)
async def main():
    llm = GroqLLM()
    try:
        response = await llm.ainvoke([
            HumanMessage(content="Reply with exactly: Groq connection successful")
        ])
        print("Invoke:", response.content)

        chunks = []
        async for chunk in llm.astream([
            HumanMessage(content="Count from one to three.")
        ]):
            if chunk.content:
                chunks.append(chunk.content)
        print("Stream:", "".join(chunks))
    finally:
        await llm.client.aclose()

if __name__ == "__main__":
    asyncio.run(main())
