import requests

from api.endpoints import BASE_URL
class APIClient:
    @staticmethod
    def get(endpoint):
        response = requests.get(
            BASE_URL + endpoint,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    @staticmethod
    def post(endpoint, payload):
        response = requests.post(
            BASE_URL + endpoint,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        return response.json()