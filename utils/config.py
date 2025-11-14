import os
from dotenv import load_dotenv

def get_env(key: str):
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    load_dotenv(dotenv_path=env_path)
    return os.getenv(key)
