import os
from dotenv import load_dotenv

def get_env(key: str):
    # ✅ 항상 main.py 기준으로 .env를 불러오도록
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    load_dotenv(dotenv_path=env_path)
    return os.getenv(key)
