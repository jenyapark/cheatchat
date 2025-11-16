import requests
from utils.config import USER_TOKEN

def send_message_as_user(channel_id: str, text: str):
    url = "https://slack.com/api/chat.postMessage"
    headers = {"Authorization": f"Bearer {USER_TOKEN}"}
    payload = {"channel": channel_id, "text": text, "as_user": True}
    response = requests.post(url, headers=headers, json=payload)
    return response.json()
