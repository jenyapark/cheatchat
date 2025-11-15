# slack_bot/llm_engine.py

import google.generativeai as genai
import os
from utils.config import get_env

genai.configure(api_key=get_env("GEMINI_API_KEY"))

MODEL_NAME = "gemini-2.5-flash"

def generate_ai_response(text: str, tone: str = "friendly"):
    try:
        prompt = f"""
당신은 사용자를 대신해 메시지를 작성하는 AI입니다.
말투는 "{tone}" 입니다.

다음 메시지에 자연스럽게 한 문장으로 답변하세요:

"{text}"
"""

        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)
        return response.text.strip()

    except Exception as e:
        return f"AI Error: {str(e)}"

def generate_reply_candidates(user_text: str, tone: str = "friendly"):

    try:
        prompt = f"""
상대방이 다음과 같은 메시지를 보냈습니다:

"{user_text}"

선택된 말투는 "{tone}" 입니다.
이 말투에 맞추어 **답장 후보 3개**를 만들어 주세요.

조건:
- 각 답장은 1~2문장
- 너무 길지 않게
- 번호를 붙여 출력

출력 형식 예시:
1) 첫 번째 답장
2) 두 번째 답장
3) 세 번째 답장
"""

        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)

        raw = response.text.strip()

        lines = raw.split("\n")
        candidates = [line[line.index(")")+1:].strip()
                      for line in lines if ")" in line]

        return candidates[:3]

    except Exception as e:
        print("[LLM ERROR]", e)
        return []