import asyncio

from backend.llm.llama_service import llama_service


async def main():
    print("Starting streaming test...\n")

    async for chunk in llama_service.stream_response(
        [
            {
                "role": "user",
                "content": "Explain AI in 2 sentences."
            }
        ]
    ):
        print(chunk, end="", flush=True)

    print("\n\nStreaming test completed.")


if __name__ == "__main__":
    asyncio.run(main())