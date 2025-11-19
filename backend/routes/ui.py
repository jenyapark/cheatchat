# routes/ui.py

from fastapi import APIRouter, Request, Query
from slack_bot.llm_engine import generate_reply_candidates
import requests, os, time, json
from slack_bot.storage import storage

router = APIRouter()


@router.post("/ui/set_alias")
def set_alias(data: dict):
    conv_id = data["id"]
    alias = data["alias"]
    storage.set_alias(conv_id, alias)
    return {"ok": True}

def format_relative(ts):
    diff = time.time() - ts
    if diff < 60:
        return f"{int(diff)}초 전"
    elif diff < 3600:
        return f"{int(diff/60)}분 전"
    elif diff < 86400:
        return f"{int(diff/3600)}시간 전"
    else:
        return f"{int(diff/86400)}일 전"

@router.post("/ui/mark_read")
def mark_read(data: dict):
    conv_id = data["id"]
    storage.mark_read(conv_id)
    return {"ok": True}



@router.post("/ui/set_alias")
def set_alias(data: dict):
    conv_id = data["id"]
    alias = data["alias"]

    from slack_bot.storage import storage
    storage.set_alias(conv_id, alias)

    return {"ok": True}

@router.get("/ui/messages")
def list_messages():
    conv_ids = storage.get_conversations()

    conversations = []
    for conv_id in conv_ids:
        convo = storage.get_conversation(conv_id)
        messages = convo["messages"]

        if len(messages) > 0:
            last = messages[-1]
            prefix = "상대" if last["direction"] == "incoming" else "나"
            preview = f"{prefix}: {last['text']}"
            time_label = format_relative(last["ts"])
        else:
            preview = ""
            time_label = ""

        alias = storage.get_alias(conv_id)
        if alias:
            display_name = alias
        else:
            display_name = conv_id
        
        unread_count = storage.get_unread_count(conv_id)

        conversations.append({
            "id": conv_id,
            "name": display_name,
            "preview": preview,
            "time": time_label,
            "unreadCount": unread_count

        })

    return {"conversations": conversations}

@router.get("/ui/messages/{conv_id}")
def get_message(conv_id: str, tone: str = Query("friendly_formal")):
    data = storage.get_conversation(conv_id)
    messages = data.get("messages", [])
    #candidates = generate_contextual_reply(messages, tone=tone)


    return {
        "messages": messages,
        #"candidates": candidates,
    }

@router.get("/ui/tone_options/{conv_id}")
def get_tone_options(conv_id: str):
    user_id = storage.get_user_id(conv_id)
    storage.save_user_id(conv_id, user_id)
    if user_id is None:
        return {
            "relationship": "acquaintance",
            "tone_options": []
        }

    relationship = storage.get_relationship(user_id)

    with open("tone_presets.json", "r") as f:
        presets = json.load(f)

    tone_options = presets.get(relationship, presets.get("acquaintance", []))

    return {
        "relationship": relationship,
        "tone_options": tone_options
    }


@router.post("/ui/set_relationship")
def set_relationship(payload: dict):
    conv_id = payload["conv_id"]
    relationship = payload["relationship"]

    user_id = storage.get_user_id(conv_id)
    if not user_id:
        return {"ok": False, "error": "user_id_not_found"}

    storage.set_relationship(user_id, relationship)
    return {"ok": True}


@router.post("/ui/send")
def send_message(payload: dict):
    conv_id = payload["conversation_id"]
    text = payload["text"]
    tone = payload.get("tone")

    with open("user_token.txt") as f:
        my_id, token = f.read().split(":")

    url = "https://slack.com/api/chat.postMessage"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    body = {"channel": conv_id, "text": text}

    r = requests.post(url, json=body, headers=headers).json()

    storage.save_outgoing(conv_id, text)

    return r



@router.get("/ui/debug/usernames")
def debug_usernames():
    from slack_bot.storage import storage
    return storage.usernames


@router.post("/ui/generate_candidates")
def generate_candidates(payload: dict):
    conv_id = payload["conv_id"]
    tone = payload["tone"]

    # 대화 전체 불러오기
    data = storage.get_conversation(conv_id)
    messages = data.get("messages", [])

    # LLM 후보 생성
    candidates = generate_reply_candidates(messages, tone)

    return {"candidates": candidates}
