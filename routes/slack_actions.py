# routes/slack_actions.py
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import json, os, requests

router = APIRouter()

SETTINGS_FILE = "user_settings.json"

def save_user_tone(user_id, tone):
    settings = {}
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            settings = json.load(f)

    if user_id not in settings:
        settings[user_id] = {}

    settings[user_id]["tone"] = tone

    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=2)

@router.post("/actions")
async def slack_actions(request: Request):

    form = await request.form()
    data = json.loads(form["payload"])

    action = data["actions"][0]
    action_id = action["action_id"]
    user_id = data["user"]["id"]
    channel = data["channel"]["id"]

    if not os.path.exists("user_token.txt"):
        return JSONResponse({"ok": False})

    with open("user_token.txt", "r") as f:
        MY_USER_ID, USER_TOKEN = f.read().strip().split(":")


    if action_id in ["tone_friendly", "tone_polite"]:
        tone = "friendly" if action_id == "tone_friendly" else "polite"
        save_user_tone(user_id, tone)
        return JSONResponse({"ok": True})


    selected_text = action.get("value")  # 후보 텍스트

    if not selected_text:
        return JSONResponse({"ok": True})  # 방어 코드

    url = "https://slack.com/api/chat.postMessage"

    headers = {
        "Authorization": f"Bearer {USER_TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {
        "channel": channel,
        "text": selected_text
    }

    requests.post(url, headers=headers, json=payload)

    return JSONResponse({"ok": True})