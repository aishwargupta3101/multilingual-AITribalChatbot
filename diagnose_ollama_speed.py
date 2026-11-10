"""
Read-only Ollama performance diagnostic for the Tribal AI Chatbot.
This script does NOT edit project files or change application settings.
Run from the project root with the project's virtual environment activated:
    python diagnose_ollama_speed.py
It sends one short benchmark request to the configured Ollama model.
"""
import asyncio
import time
from backend.config.settings import settings
from ollama import AsyncClient


def seconds_from_ns(value):
    try:
        return float(value or 0) / 1_000_000_000
    except (TypeError, ValueError):
        return 0.0


async def main():
    base_url = settings.OLLAMA_BASE_URL.rstrip("/")
    headers = {}
    if settings.OLLAMA_PROXY_TOKEN:
        headers["Authorization"] = f"Bearer {settings.OLLAMA_PROXY_TOKEN}"

    client = AsyncClient(host=base_url, headers=headers, timeout=300.0)
    print("=" * 64)
    print("TRIBAL AI CHATBOT — READ-ONLY OLLAMA DIAGNOSTIC")
    print("=" * 64)
    print(f"Ollama endpoint : {base_url}")
    print(f"Configured model: {settings.LLAMA_MODEL}")
    print("Application files/settings will not be modified.")
    print("\nChecking model metadata...")

    try:
        info = await client.show(settings.LLAMA_MODEL)
        details = getattr(info, "details", None)
        model_info = getattr(info, "model_info", None)
        if details:
            for key in ("format", "family", "parameter_size", "quantization_level"):
                value = details.get(key) if isinstance(details, dict) else getattr(details, key, None)
                if value:
                    print(f"{key:20}: {value}")
        if isinstance(model_info, dict):
            context_values = [
                (key, value) for key, value in model_info.items()
                if "context_length" in key.lower()
            ]
            for key, value in context_values[:3]:
                print(f"{key:20}: {value}")
    except Exception as exc:
        print(f"Could not read model metadata: {type(exc).__name__}: {exc}")
        print("Confirm Ollama is running and the configured model exists.")
        return
    print("\nRunning one short baseline request (maximum 32 output tokens)...")
    start = time.perf_counter()
    try:
        response = await client.chat(
            model=settings.LLAMA_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "Answer clearly and accurately. Be concise for this diagnostic."
                },
                {
                    "role": "user",
                    "content": "In two sentences, explain what a vector database is."
                },
            ],
            stream=False,
            options={
                "temperature": 0,
                "num_predict": 32,
            },
            keep_alive="30m",
        )
        elapsed = time.perf_counter() - start
        print("\nRESULTS")
        print("-" * 64)
        print(f"Wall-clock time      : {elapsed:.2f} seconds")
        prompt_tokens = getattr(response, "prompt_eval_count", 0) or 0
        output_tokens = getattr(response, "eval_count", 0) or 0
        prompt_seconds = seconds_from_ns(getattr(response, "prompt_eval_duration", 0))
        output_seconds = seconds_from_ns(getattr(response, "eval_duration", 0))
        total_seconds = seconds_from_ns(getattr(response, "total_duration", 0))
        print(f"Prompt tokens        : {prompt_tokens}")
        print(f"Output tokens        : {output_tokens}")
        print(f"Prompt evaluation    : {prompt_seconds:.2f} seconds")
        print(f"Output generation    : {output_seconds:.2f} seconds")
        print(f"Ollama total         : {total_seconds:.2f} seconds")
        if output_seconds > 0 and output_tokens:
            print(f"Generation speed     : {output_tokens / output_seconds:.2f} tokens/sec")
        print("\nSample answer:")
        print(getattr(getattr(response, "message", None), "content", "") or "(empty)")
        print("\nInterpretation:")
        print("- Slow prompt evaluation even for this short request suggests a model/hardware/runtime bottleneck.")
        print("- Fast short-request timing but very slow app requests points toward the full prompt/context or app path.")
        print("- This is a baseline test, not a full end-to-end chat benchmark.")
    except Exception as exc:
        print(f"Benchmark request failed: {type(exc).__name__}: {exc}")
        print("Check the Ollama endpoint, model name, and whether Ollama is responsive.")


if __name__ == "__main__":
    asyncio.run(main())
