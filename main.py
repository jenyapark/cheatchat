from fastapi import FastAPI
from routes import slack_oauth, slack_send, slack_events, slack_actions
from routes.ui import router as ui_router
import threading
from dm_polling import start_polling_loop
import os
from slack_bot.llm_engine import generate_reply_candidates
from fastapi.middleware.cors import CORSMiddleware

if os.environ.get("RUN_MAIN") != "true":
    pass
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def start_polling():
    print("[INFO] Polling thread starting...")
    t = threading.Thread(target=start_polling_loop, daemon=True)
    t.start()

app.include_router(ui_router)



# Slack 관련 라우터 등록
app.include_router(slack_oauth.router, prefix="/slack")
app.include_router(slack_send.router, prefix="/slack")
app.include_router(slack_events.router)
app.include_router(slack_actions.router, prefix="/slack")
@app.get("/")
def home():
    return {"message": "Slack OAuth 서버 작동 중 "}
