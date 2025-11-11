from fastapi import FastAPI
from routes import slack_oauth, slack_send

app = FastAPI()

# ✅ Slack 관련 라우터 등록
app.include_router(slack_oauth.router, prefix="/slack")
app.include_router(slack_send.router, prefix="/slack")

@app.get("/")
def home():
    return {"message": "Slack OAuth 서버 작동 중 ✅"}
