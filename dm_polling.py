# dm_polling.py
import time, requests
from slack_bot.storage import storage
from slack_bot.llm_engine import generate_reply_candidates

HEADERS = None
MY_ID = None
last_seen = {} 

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
    params = {"channel": channel, "limit": 5}
    res = requests.get(url, headers=HEADERS, params=params).json()

    messages = res.get("messages", [])

    last = last_seen.get(channel, "0")

    new_msgs = [m for m in messages if m["ts"] > last and "user" in m]

    if messages:
        last_seen[channel] = messages[0]["ts"]

    return new_msgs

last_ts_map = {}
def start_polling_loop():

    while not load_token():
        time.sleep(3)

    while True:
        dms = fetch_dms()

        for dm in dms:
            last_ts = last_ts_map.get(dm, "0")
            messages = fetch_new_messages(dm)

            fresh_msgs = [
                m for m in messages
                if float(m.get("ts", 0)) > float(last_ts)
            ]
            if fresh_msgs:
                last_ts_map[dm] = fresh_msgs[-1]["ts"]

            for msg in fresh_msgs:
                user = msg.get("user")
                text = msg.get("text", "")

                # 내 메시지는 무시
                if user == MY_ID:
                    continue

                storage.save_incoming(dm, text)
                cands = generate_reply_candidates(text)
                storage.save_candidates(dm, cands)

        time.sleep(2)
