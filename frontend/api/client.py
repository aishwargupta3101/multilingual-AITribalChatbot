from http.client import responses

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
    def upload(endpoint,file):
        files={
            "file":(
                file.name,
                file,
                file.type
            )
        }
        response = requests.post(
            BASE_URL+ endpoint,
            files=files,
            timeout =120
        )
        response.raise_for_status()
        return response.json()
    @staticmethod
    def upload_audio(endpoint, audio_path):
        with open(audio_path,"rb") as audio:
            files ={
                "file":(
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