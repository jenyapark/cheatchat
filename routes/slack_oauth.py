from fastapi import APIRouter
from fastapi.responses import RedirectResponse, JSONResponse
import os, requests
from utils.config import get_env

router = APIRouter()

# ✅ 환경 변수 로드
SLACK_CLIENT_ID = get_env("SLACK_CLIENT_ID")
SLACK_CLIENT_SECRET = get_env("SLACK_CLIENT_SECRET")
SLACK_REDIRECT_URI = get_env("SLACK_REDIRECT_URI")

@router.get("/oauth/start")
def oauth_start():
    url = (
        f"https://slack.com/oauth/v2/authorize"
        f"?client_id={SLACK_CLIENT_ID}"
        f"&user_scope=chat:write,users:read,identify"
        f"&redirect_uri={SLACK_REDIRECT_URI}"
    )
    return RedirectResponse(url)

@router.get("/oauth/callback")
def oauth_callback(code: str):
    r = requests.post(
        "https://slack.com/api/oauth.v2.access",
        data={
            "client_id": SLACK_CLIENT_ID,
            "client_secret": SLACK_CLIENT_SECRET,
            "code": code,
            "redirect_uri": SLACK_REDIRECT_URI,
        },
    )
    data = r.json()
    print("🔐 OAuth Response:", data)

    if not data.get("ok"):
        return JSONResponse({"error": data}, status_code=400)

    user_token = data["authed_user"]["access_token"]
    user_id = data["authed_user"]["id"]

    with open("user_token.txt", "w") as f:
        f.write(f"{user_id}:{user_token}")

    return {"message": "✅ Slack 인증 완료!", "user_id": user_id}
