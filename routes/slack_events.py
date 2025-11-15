# routes/slack_events.py


from fastapi import APIRouter, Request, BackgroundTasks
from slack_bot.storage import storage
from slack_bot.llm_engine import generate_reply_candidates
import requests
import json

router = APIRouter()

processed_events = set()

def fetch_username(user_id, token):
    url = f"https://slack.com/api/users.info?user={user_id}"
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.get(url, headers=headers).json()
    if res.get("ok"):
        return res["user"]["profile"]["real_name"]
    return user_id

def process_event(event):
    with open("user_token.txt") as f:
        my_id, token = f.read().split(":")

    # 봇 메시지 거르기
    if event.get("subtype") is not None:
        return

    if event.get("user") == my_id:
        return
    
    user = event.get("user")
    text = event.get("text")
    conv_id = event.get("channel")

    # 이름 저장
    username = fetch_username(user, token)
    storage.save_user(conv_id, username)

    # 메시지 저장
    storage.save_incoming(conv_id, text)

    # 후보 생성
    cands = generate_reply_candidates(text)
    storage.save_candidates(conv_id, cands)


@router.post("/slack/events")
async def slack_events(request: Request, background_tasks: BackgroundTasks):
    if request.headers.get("X-Slack-Retry-Num"):
        return {"ok": True}
    
    body = await request.json()

    if "challenge" in body:
        return body["challenge"]
    
    event_id = body.get("event_id")

    if event_id in processed_events:
        return {"ok": True}
    
    processed_events.add(event_id)

    event = body.get("event", {})
    background_tasks.add_task(process_event, event)
    return {"ok": True}
