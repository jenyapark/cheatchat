from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse
import os, requests, json
import anyio
from slack_bot.llm_engine import generate_ai_response, generate_contextual_reply

router = APIRouter()

@router.post("/send")
def send_message(request: Request, channel: str = Query(None), tone: str = Query("friendly_formal")):
    if not os.path.exists("user_token.txt"):
        return JSONResponse({"error": "User not authenticated yet."}, status_code=401)

    with open("user_token.txt", "r") as f:
        user_id, user_token = f.read().split(":")

    # Slack DM 채널을 conv_id로 사용
    conv_id = channel
    if conv_id is None:
        return JSONResponse({"error": "channel (conv_id) is required"}, status_code=400)

    # storage.py에서 기존 대화 불러오기
    from slack_bot.storage import storage
    convo = storage.get_conversation(conv_id)["messages"]

    # 마지막 메시지가 'incoming'인지 확인
    if not convo:
        return JSONResponse({"error": "No messages in this conversation"}, status_code=400)

    # GPT에게 맥락 기반 답장 후보 생성 요청
    ai_reply = generate_contextual_reply(convo, tone=tone)

    # Slack API 호출을 위한 헤더
    headers = {
        "Authorization": f"Bearer {user_token}",
        "Content-Type": "application/json",
    }

    # Slack 전송 payload
    payload = {
        "channel": conv_id,
        "text": ai_reply if isinstance(ai_reply, str) else ai_reply[0]
    }

    # Slack에 메시지 전송
    r = requests.post("https://slack.com/api/chat.postMessage", headers=headers, json=payload)

    # outgoing 메시지 저장
    storage.save_outgoing(conv_id, payload["text"])

    return JSONResponse({
        "ok": True,
        "ai_reply": ai_reply,
        "slack_response": r.json()
    })
