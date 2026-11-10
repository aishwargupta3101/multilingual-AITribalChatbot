
import asyncio
import time
from langchain_core.messages import HumanMessage
from backend.llm.ollama_client import llm

async def test_streaming():
    messages = [
        HumanMessage(
            content="Explain artificial intelligence in 5 simple sentences."
        )
    ]

    print("\n🌿 Testing Llama 3 streaming...\n")

    start_time = time.time()
    first_token_time = None
    full_response = ""

    async for chunk in llm.astream(messages):
        if chunk.content:
            if first_token_time is None:
                first_token_time = time.time() - start_time
                print(f"\n⏱️ First token received in {first_token_time:.2f} seconds\n")

            print(chunk.content, end="", flush=True)
            full_response += chunk.content

    total_time = time.time() - start_time

    print("\n\n========== STREAMING RESULTS ==========")
    print(f"First token time: {first_token_time:.2f} seconds")
    print(f"Total response time: {total_time:.2f} seconds")
    print(f"Response length: {len(full_response)} characters")
    print("=======================================\n")

if __name__ == "__main__":
    asyncio.run(test_streaming())