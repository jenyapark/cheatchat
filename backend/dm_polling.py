# dm_polling.py
import time, requests
from slack_bot.storage import storage
import itertools
from slack_bot.llm_engine import generate_reply_candidates

HEADERS = None
MY_ID = None
last_seen = storage.load_last_ts()

def load_token():
    global MY_ID, HEADERS
    try:
        with open("user_token.txt") as f:
            MY_ID, TOKEN = f.read().split(":")
        HEADERS = {"Authorization": f"Bearer {TOKEN}"}
        print("[INFO] User token loaded.")
        return True
    except FileNotFoundError:
        print("[WARN] user_token.txt not found. Polling paused.")
        return False


def fetch_dms():
    url = "https://slack.com/api/users.conversations"
    params = {
        "types": "im",
        "limit": 1000
    }
    res = requests.get(url, headers=HEADERS, params=params).json()

    if not res.get("ok"):
        print("[ERROR] users.conversations:", res)
        return []

    return [c["id"] for c in res.get("channels", [])]


def fetch_new_messages(channel):
    url = "https://slack.com/api/conversations.history"
    params = {"channel": channel, "limit": 20}
    res = requests.get(url, headers=HEADERS, params=params).json()

    if not res.get("ok"):
        print("[ERROR] conversations.history:", res)
        return []

    messages = res.get("messages", [])
    if not messages:
        return []

    # Slack은 최신 메시지가 index 0
    last_ts = float(last_seen.get(channel, 0))

    # ts는 float로 비교
    fresh = [
        m for m in messages
        if "ts" in m and float(m["ts"]) > last_ts and "user" in m
    ]

    # fresh 가 있으면 timestamp 갱신
    if fresh:
        newest_ts = max(float(m["ts"]) for m in fresh)
        last_seen[channel] = str(newest_ts)
        storage.save_last_ts(last_seen)

    return fresh


def start_polling_loop():

    while not load_token():
        time.sleep(3)
    
    dms = fetch_dms()
    dm_cycle = itertools.cycle(dms)

    while True:

        dm = next(dm_cycle)

        messages = fetch_new_messages(dm)

        if messages:
            for msg in messages:
                user = msg.get("user")
                text = msg.get("text", "")

                if user == MY_ID:
                    continue

                storage.save_incoming(dm, text)
                cands = generate_reply_candidates(text, tone="friendly_formal")
                storage.save_candidates(dm, cands)

        # 한 번에 하나의 DM만 처리함 → Rate 제한 보호
        time.sleep(2)
        