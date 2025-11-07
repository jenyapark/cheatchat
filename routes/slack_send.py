from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse
import os, requests

router = APIRouter()

@router.post("/send")
async def send_message(request: Request, channel: str = Query(None)):
    if not os.path.exists("user_token.txt"):
        return JSONResponse({"error": "User not authenticated yet."}, status_code=401)

    with open("user_token.txt", "r") as f:
        user_id, user_token = f.read().split(":")

    headers = {
        "Authorization": f"Bearer {user_token}",
        "Content-Type": "application/json",
    }

    data = await request.json()
    text = data.get("text", "👋 기본 메시지입니다!")

    target = channel or f"@{user_id}"
    body = {"channel": target, "text": text}

    r = requests.post("https://slack.com/api/chat.postMessage", headers=headers, json=body)
    print("💬 chat.postMessage:", r.text)

    return JSONResponse({"ok": True, "slack_response": r.json()})
