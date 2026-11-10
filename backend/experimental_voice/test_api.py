
from fastapi import FastAPI
from fastapi.testclient import TestClient
from backend.experimental_voice.api import router

app = FastAPI()
app.include_router(router)
client = TestClient(app)

response = client.post(
    "/experimental/voice/tts",
    json={
        "text": "ꯑꯥꯏ ꯑꯁꯤ ꯃꯤꯑꯣꯏꯕꯒꯤ ꯃꯊꯧ ꯇꯥꯕꯥ ꯊꯕꯛ ꯑꯃꯅꯤ।",
        "script": "meitei_mayek"
    }
)

print("Status:", response.status_code)
print("Content-Type:", response.headers.get("content-type"))
print("Audio size:", len(response.content), "bytes")

if response.status_code == 200:
    with open("experimental_outputs/manipuri_tts/api_test.wav", "wb") as f:
        f.write(response.content)
    print("Audio saved successfully")
else:
    print("Error:", response.text)