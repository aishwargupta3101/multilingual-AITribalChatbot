import requests

from api.endpoints import BASE_URL

class APIClient:
    @staticmethod
    def get(endpoint):
        response = requests.get(
            BASE_URL + endpoint,
            timeout=120
        )
        response.raise_for_status()
        return response.json()
    @staticmethod
    def post(endpoint, payload):
        response = requests.post(

            BASE_URL + endpoint,
            json=payload,
            timeout=180
        )
        response.raise_for_status()
        return response.json()
    @staticmethod
    def upload(endpoint, file, session_id):
        """
        Upload a document along with the session ID.
        """
        files = {
            "file": (
                file.name,
                file,
                file.type
            )
        }

        data = {
            "session_id": session_id
        }
        response = requests.post(
            BASE_URL + endpoint,
            files=files,
            data=data,
            timeout=120
        )
        response.raise_for_status()
        return response.json()
    @staticmethod
    def upload_audio(endpoint, audio_path):
        with open(audio_path, "rb") as audio:

            files = {
                "file": (
                    "user_audio.wav",
                    audio,
                    "audio/wav"
                )
            }
            response = requests.post(
                BASE_URL + endpoint,
                files=files,
                timeout=120
            )
            response.raise_for_status()
            return response.json()

    @staticmethod
    def speech_to_text(audio_bytes):
        files = {
            "audio": (
                "recording.wav",
                audio_bytes,
                "audio/wav"
            )
        }
        response = requests.post(
            "http://127.0.0.1:8000/api/v1/speech",
            files=files,
            timeout=120
        )
        response.raise_for_status()
        return response.json()
    @staticmethod
    def chat(question,session_id,language,document_id=None):
        payload = {
            "question":question,
            "session_id" : session_id,
            "language":language,
            "document_id":document_id
        }
        response = requests.post(
            BASE_URL+"/api/v1/chat",
            json=payload,
            timeout=180
        )
        response.raise_for_status()
        return response.json()
    @staticmethod
    def text_to_speech(text,language):
        payload ={
            "text":text,
            "language":language
        }
        response = requests.post(
            BASE_URL + "/api/v1/tts/",
            json=payload,
            timeout=180,
            stream=True
        )
        response.raise_for_status()
        return response.content