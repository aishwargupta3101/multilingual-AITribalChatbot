
import asyncio
import time
from ollama import AsyncClient
from backend.config.settings import settings

async def main():
    client = AsyncClient(
        host=settings.OLLAMA_BASE_URL.rstrip("/"),
        timeout=300.0
    )
    model = settings.LLAMA_MODEL
    messages = [
        {"role": "user", "content": "Explain photosynthesis in detail, including its stages and importance. Use clear headings and examples."}
    ]
    for threads in (None, 10):
        options = {"temperature": 0.3, "num_predict": 512}
        if threads is not None:
            options["num_thread"] = threads
        start = time.perf_counter()
        response = await client.chat(
            model=model,
            messages=messages,
            stream=False,
            options=options,
            keep_alive="30m"
        )
        elapsed = time.perf_counter() - start
        print(f"\nThreads: {threads or 'default'}")
        print(f"Elapsed: {elapsed:.2f}s")
        print(f"Prompt tokens: {response.prompt_eval_count}")
        print(f"Generated tokens: {response.eval_count}")
        print(f"Generation speed: {response.eval_count / (response.eval_duration / 1e9):.2f} tokens/sec")
        print(f"Answer preview: {response.message.content[:200]}")
    await client.close()

if __name__ == "__main__":
    asyncio.run(main())
