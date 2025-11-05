from fastapi import FastAPI, Request
from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv()

SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Slack PoliteBot is running!"}

@app.post("/slack/command/polite")
async def polite_command(request: Request):
    form = await request.form()
    user_name = form.get("user_name")
    text = form.get("text")

    # Slack에 바로 텍스트로 응답
    return {
        "response_type": "ephemeral",  # 채널에 보이게
        "text": f"({user_name})님이 보낸 문장: {text}\n공손하게 변환 중..."
    }
