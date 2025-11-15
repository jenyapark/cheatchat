# slack_bot/storage.py
import json
import os, time

ALIAS_FILE = "aliases.json"
LAST_TS_FILE = "last_ts.json"

class MemoryStorage:
    def __init__(self):
        self.messages = {}    
        self.candidates = {} 
        self.usernames = {}  
        self.alias = {}
        self.last_read = {}

    @staticmethod
    def load_last_ts():
        if not os.path.exists(LAST_TS_FILE):
            return {}
        try:
            with open(LAST_TS_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    @staticmethod
    def save_last_ts(map_data):
        with open(LAST_TS_FILE, "w") as f:
            json.dump(map_data, f)

    def mark_read(self, conv_id):
        self.last_read[conv_id] = time.time()

    def is_unread(self, conv_id):
        msgs = self.messages.get(conv_id, [])
        if not msgs:
            return False

        last_msg_ts = msgs[-1]["ts"]
        last_read_ts = self.last_read.get(conv_id, 0)

        return last_msg_ts > last_read_ts
    
    def get_unread_count(self, conv_id):
        last_read = self.last_read.get(conv_id, 0)
        msgs = self.messages.get(conv_id, [])

        return sum(1 for m in msgs if m["ts"] > last_read)


    def load_aliases(self):
        if os.path.exists(ALIAS_FILE):
            with open(ALIAS_FILE, "r", encoding="utf-8") as f:
                self.alias = json.load(f)
        else:
            self.alias = {}
 
    def save_aliases(self):
        with open(ALIAS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.alias, f, ensure_ascii=False, indent=2)
    
    def set_alias(self, conv_id, alias):
        self.alias[conv_id] = alias
        self.save_aliases()   # 파일에 저장

    def get_alias(self, conv_id):
        return self.alias.get(conv_id, None)

    def save_user(self, conv_id, username):
        print(f"[SAVE USER] {conv_id} -> {username}")
        self.usernames[conv_id] = username
    
    def get_user(self, conv_id):
        return self.usernames.get(conv_id, conv_id)

    def save_incoming(self, conv_id, text):
        self.messages.setdefault(conv_id, [])
        self.messages[conv_id].append({"text": text, "direction": "incoming", "ts" : time.time()})
        print(f"[INCOMING] {conv_id} - {text}")



    def save_candidates(self, conv_id, cands):
        self.candidates[conv_id] = cands
        print(f"[CANDIDATES] for {conv_id}: {cands}")

    def save_outgoing(self, conv_id, text):
        self.messages.setdefault(conv_id, [])
        self.messages[conv_id].append({"text": text, "direction": "outgoing", "ts": time.time()})

    def get_conversations(self):
        return list(self.messages.keys())

    def get_conversation(self, conv_id):
        return {
            "messages": self.messages.get(conv_id, []),
            "candidates": self.candidates.get(conv_id, [])
        }


storage = MemoryStorage()
storage.load_aliases()

