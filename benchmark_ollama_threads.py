"""
Standalone CPU-thread benchmark for Ollama.
Does not edit chatbot files, .env, or Ollama model configuration.
Run from the project root with the project's virtual environment activated:
    python benchmark_ollama_threads.py
"""
import asyncio
import time
from backend.config.settings import settings
from ollama import AsyncClient


def ns_to_seconds(value):
    try:
        return float(value or 0) / 1_000_000_000
    except (TypeError, ValueError):
        return 0.0


async def main():
    headers = {}
    if settings.OLLAMA_PROXY_TOKEN:
        headers["Authorization"] = f"Bearer {settings.OLLAMA_PROXY_TOKEN}"
    client = AsyncClient(
        host=settings.OLLAMA_BASE_URL.rstrip("/"),
        headers=headers,
        timeout=300.0,
    )
    prompt = (
        "Explain what a vector database is and give one practical example. "
        "Use a clear, complete answer."
    )
    thread_counts = [4, 6, 8, 10, 12]
    print("=" * 72)
    print("OLLAMA CPU THREAD BENCHMARK — NO PROJECT SETTINGS ARE CHANGED")
    print("=" * 72)
    print(f"Model: {settings.LLAMA_MODEL}")
    print("Each test uses the same prompt and a maximum of 48 output tokens.")
    print("Run while the computer is otherwise idle for a fair comparison.")
    print("\nThreads | Wall sec | Prompt sec | Generate sec | Tokens/sec | Out tokens")
    print("-" * 72)
    results = []
    for threads in thread_counts:
        started = time.perf_counter()
        try:
            response = await client.chat(
                model=settings.LLAMA_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "Answer accurately and clearly. Do not add unrelated information."
                    },
                    {"role": "user", "content": prompt},
                ],
                stream=False,
                options={
                    "temperature": 0,
                    "num_predict": 48,
                    "num_thread": threads,
                },
                keep_alive="30m",
            )
            wall = time.perf_counter() - started
            prompt_sec = ns_to_seconds(getattr(response, "prompt_eval_duration", 0))
            gen_sec = ns_to_seconds(getattr(response, "eval_duration", 0))
            out_tokens = int(getattr(response, "eval_count", 0) or 0)
            rate = out_tokens / gen_sec if gen_sec > 0 else 0.0
            print(
                f"{threads:7d} | {wall:8.2f} | {prompt_sec:10.2f} | "
                f"{gen_sec:12.2f} | {rate:10.2f} | {out_tokens:10d}"
            )
            results.append((threads, wall, rate, prompt_sec, gen_sec))
        except Exception as exc:
            print(f"{threads:7d} | FAILED: {type(exc).__name__}: {exc}")
    if results:
        fastest = min(results, key=lambda item: item[1])
        fastest_gen = max(results, key=lambda item: item[2])
        print("\nInterpretation:")
        print(f"- Lowest total wall time: {fastest[0]} threads ({fastest[1]:.2f}s).")
        print(f"- Highest measured generation rate: {fastest_gen[0]} threads ({fastest_gen[2]:.2f} tokens/sec).")
        print("- Thread settings apply only to these benchmark requests; no persistent configuration changed.")
        print("- Differences can be noisy. If the top results are close, prefer the lower thread count to leave CPU resources for the UI and backend.")
    print("\nNo chatbot source files or environment variables were modified.")


if __name__ == "__main__":
    asyncio.run(main())
