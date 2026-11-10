import requests
import json
import time

url = "http://127.0.0.1:8000/api/v1/chat/stream"
payload = {
    "session_id": "test-stream-session-001",
    "question": "Explain artificial intelligence in simple English.",
    "language": "english"
}

start_time = time.time()
first_token = None

with requests.post(
    url,
    json=payload,
    stream=True,
    timeout=(10, 600)
) as response:

    print("Status:", response.status_code)

    if response.status_code != 200:
        print("Status:", response.status_code)
        print("Validation error:", response.text)
        exit()

    print("Connected successfully!")
    for line in response.iter_lines(decode_unicode=True):

        if not line or not line.startswith("data: "):
            continue

        event = json.loads(line[6:])

        if event["type"] == "token":
            if first_token is None:
                first_token = time.time()
                print(
                    f"\nFirst token received in "
                    f"{first_token - start_time:.2f} seconds\n"
                )

            print(event["content"], end="", flush=True)

        elif event["type"] == "complete":
            print("\n\nChat completed successfully.")

        elif event["type"] == "error":
            print("\n\nError:", event["message"])

print(f"\nTotal time: {time.time() - start_time:.2f} seconds")