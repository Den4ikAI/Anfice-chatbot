import requests


class ChatClient:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.token = token

    def process_user_message(self, user_id):
        url = f"{self.base_url}/process_user_message"
        payload = {"token": self.token, "user_id": user_id}
        response = requests.post(url, json=payload)
        response = response.json()['message']
        return response

    def add_user_message(self, user_id, message):
        url = f"{self.base_url}/add_user_message"
        payload = {"token": self.token, "user_id": user_id, "message": message}
        response = requests.post(url, json=payload)
        response = response.json()['message']
        return response

    def add_bot_message(self, user_id, message):
        url = f"{self.base_url}/add_bot_message"
        payload = {"token": self.token, "user_id": user_id, "message": message}
        response = requests.post(url, json=payload)
        response = response.json()['message']
        return response

    def set_system_prompt(self, user_id, prompt):
        url = f"{self.base_url}/set_system_prompt"
        payload = {"token": self.token, "user_id": user_id, "prompt": prompt}
        response = requests.post(url, json=payload)
        response = response.json()['message']
        return response

    def get_last_bot_message(self, user_id):
        url = f"{self.base_url}/get_last_bot_message"
        params = {"token": self.token, "user_id": user_id}
        response = requests.get(url, json=params)
        response = response.json()['message']
        return response

    def get_last_user_message(self, user_id):
        url = f"{self.base_url}/get_last_user_message"
        params = {"token": self.token, "user_id": user_id}
        response = requests.get(url, json=params)
        response = response.json()['message']
        return response

    def get_dialog(self, user_id):
        url = f"{self.base_url}/get_dialog"
        params = {"token": self.token, "user_id": user_id}
        response = requests.get(url, json=params)
        response = response.json()['message']
        return response

    def clear_context(self, user_id):
        url = f"{self.base_url}/clear_context"
        params = {"token": self.token, "user_id": user_id}
        response = requests.get(url, json=params)
        response = response.json()['message']
        return response
