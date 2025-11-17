from fastapi import APIRouter
from fastapi.responses import RedirectResponse, JSONResponse
import os, requests, json
from utils.config import get_env

router = APIRouter()

# 환경 변수 로드
SLACK_CLIENT_ID = get_env("SLACK_CLIENT_ID")
SLACK_CLIENT_SECRET = get_env("SLACK_CLIENT_SECRET")
SLACK_REDIRECT_URI = get_env("SLACK_REDIRECT_URI")

@router.get("/oauth/start")
def oauth_start():
    url = (
        "https://slack.com/oauth/v2/authorize"
        f"?client_id={SLACK_CLIENT_ID}"
        f"&user_scope="
        "identify,"
        "users:read,"
        "chat:write,"
        "im:read,"
        "im:history,"
        "mpim:read,"
        "groups:read,"
        "channels:read"
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
    
    user = data["authed_user"]
    user_id = user["id"]
    user_token = user["access_token"]

    # 사용자별 디렉토리 생성
    base_dir = f"data/{user_id}"
    os.makedirs(base_dir, exist_ok=True)

    # 개인 토큰 저장
    with open(f"{base_dir}/user_token.txt", "w") as f:
        f.write(user_token)

    # 프로필 저장
    with open(f"{base_dir}/profile.json", "w") as f:
        json.dump(user, f, indent=2)

    # 초기 conversations / aliases 파일 생성
    if not os.path.exists(f"{base_dir}/conversations.json"):
        with open(f"{base_dir}/conversations.json", "w") as f:
            f.write("{}")

    if not os.path.exists(f"{base_dir}/aliases.json"):
        with open(f"{base_dir}/aliases.json", "w") as f:
            f.write("{}")

    return {
        "message": "Slack 인증 완료!",
        "user_id": user_id,
        "folder": base_dir,
        "note": "이제부터 이 사용자의 DM을 polling하고, UI에서 사용 가능함.",
    }