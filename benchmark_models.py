
import time
import ollama

client = ollama.Client()

models = [
    "llama3:latest",
    "phi:latest",
    "gemma2:2b",
    "mistral:7b"
]

prompt = "What is artificial intelligence? Explain in two simple sentences."

for model in models:
    print(f"\nTesting {model}...")
    start = time.perf_counter()

    try:
        response = client.chat(
            model=model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            options={
                "num_predict": 100,
                "temperature": 0.2
            }
        )

        elapsed = time.perf_counter() - start
        tokens = response.get("eval_count", 0)

        print(f"Model: {model}")
        print(f"Time: {elapsed:.2f} seconds")
        print(f"Generated tokens: {tokens}")

    except Exception as error:
        print(f"Error testing {model}: {error}")