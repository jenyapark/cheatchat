import os
from dotenv import load_dotenv

def get_env(key: str):
    root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    env_path = os.path.join(root_path, ".env")

    load_dotenv(env_path)

    return os.getenv(key)
