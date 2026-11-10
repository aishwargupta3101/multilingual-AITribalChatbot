"""
Test Groq models BEFORE changing Tribal LearnAI.
Reads GROQ_API_KEY from your existing .env/environment and never prints it.
Run after the current rate limit has reset.
"""
import os
import time
from pathlib import Path
import httpx

try:
    from dotenv import load_dotenv
    load_dotenv()
    load_dotenv(Path.cwd() / ".env")
except ImportError:
    pass

API_KEY = os.getenv("GROQ_API_KEY", "").strip()
API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODELS_TO_TEST = ["openai/gpt-oss-20b", "openai/gpt-oss-120b"]

if not API_KEY:
    raise SystemExit(
        "GROQ_API_KEY was not found. Run this from your project root, "
        "where your private .env file is located. Do not paste your key into chat."
    )

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}
prompt = (
    "You are evaluating a model for an educational video-learning assistant. "
    "In 3 concise bullet points, explain what a variable is in Python. "
    "Use simple language and one tiny example."
)

print("Groq model smoke test. This will NOT change your app configuration.")
print("Each model uses one small API request. Run after any active rate limit resets.\n")

with httpx.Client(timeout=httpx.Timeout(60.0, connect=15.0)) as client:
    for model in MODELS_TO_TEST:
        print(f"Testing: {model}")
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
            "max_completion_tokens": 180,
            "stream": False,
        }
        started = time.perf_counter()
        try:
            response = client.post(API_URL, headers=headers, json=payload)
            elapsed = time.perf_counter() - started
            if response.is_success:
                data = response.json()
                choices = data.get("choices") or []
                message = (choices[0].get("message") or {}) if choices else {}
                content = message.get("content") or ""
                usage = data.get("usage") or {}
                print(f"  RESULT: SUCCESS | HTTP {response.status_code} | {elapsed:.2f}s")
                print(f"  Tokens: prompt={usage.get('prompt_tokens', 'n/a')}, "
                      f"completion={usage.get('completion_tokens', 'n/a')}")
                print("  Sample response:")
                print("  " + (content.strip().replace("\n", "\n  ")[:900] or "[empty response]"))
            else:
                print(f"  RESULT: FAILED | HTTP {response.status_code} | {elapsed:.2f}s")
                try:
                    body = response.json()
                    err = body.get("error", body)
                    print(f"  Error: {str(err)[:900]}")
                except ValueError:
                    print(f"  Error: {response.text[:900]}")
                for header_name in (
                    "retry-after",
                    "x-ratelimit-remaining-requests",
                    "x-ratelimit-remaining-tokens",
                    "x-ratelimit-reset-requests",
                    "x-ratelimit-reset-tokens",
                ):
                    value = response.headers.get(header_name)
                    if value is not None:
                        print(f"  {header_name}: {value}")
        except httpx.HTTPError as exc:
            print(f"  RESULT: CONNECTION ERROR | {type(exc).__name__}: {exc}")
        print()
