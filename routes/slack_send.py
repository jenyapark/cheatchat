from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse
import os, requests, json
import anyio
from slack_bot.llm_engine import generate_ai_response

router = APIRouter()

@router.post("/send")
def send_message(request: Request, channel: str = Query(None)):
    if not os.path.exists("user_token.txt"):
        return JSONResponse({"error": "User not authenticated yet."}, status_code=401)

    with open("user_token.txt", "r") as f:
        user_id, user_token = f.read().split(":")

    headers = {
        "Authorization": f"Bearer {user_token}",
        "Content-Type": "application/json",
    }

    raw_body = anyio.from_thread.run(request.body)
    if raw_body is None:
        raw_body = request.stream().read()
    
    try:
        data = json.loads(raw_body) if raw_body else {}
    except Exception:
        data = {}

    user_text = data.get("text", "👋 기본 메시지입니다!")

    ai_reply = generate_ai_response(user_text)

    target = channel or f"@{user_id}"
    payload = {"channel": target, "text": ai_reply}

    r = requests.post("https://slack.com/api/chat.postMessage", headers=headers, json=payload)
    print("💬 chat.postMessage:", r.text)

    return JSONResponse({"ok": True, "ai_reply": ai_reply, "slack_response": r.json()})
