# slack_bot/llm_engine.py

import google.generativeai as genai
import os
from utils.config import get_env

genai.configure(api_key=get_env("GEMINI_API_KEY"))

MODEL_NAME = "gemini-2.5-flash"

def generate_ai_response(text: str, tone: str = "friendly_formal"):
    tone_instruction = {
        "friendly_formal": (
            "말투는 친근하고 따뜻한 존댓말로 작성하세요."
        ),
        "soft_formal": (
            "말투는 부드럽고 공손한 직장인 말투로 작성하세요."
        ),
        "casual": (
            "말투는 편안하고 자연스러운 반말로 작성하세요."
        ),
    }.get(tone, "")
    
    try:
        prompt = f"""
당신은 사용자를 대신해 메시지를 작성하는 AI입니다. 
친절하고 사용자 의도를 잘 파악해 자연스럽게 작성하세요.
말투는 "{tone_instruction}" 입니다.

다음 메시지에 자연스럽게 한 문장으로 답변하세요:

"{text}"
"""

        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)
        return response.text.strip()

    except Exception as e:
        return f"AI Error: {str(e)}"

def generate_reply_candidates(user_text: str, tone: str = "friendly_formal"):

    tone_instruction = {
        "friendly_formal": (
            "말투는 친근하고 따뜻하지만 반드시 존댓말(~요, ~세요)을 사용하세요. "
            "반말이나 반존대는 사용하지 마세요. 너무 인터넷 은어는 자제하세요."
        ),
        "business_formal": (
            "말투는 공손하고 단정한 업무용 존댓말을 사용하세요. "
            "친근한 표현은 소폭 허용되지만, 이모지와 과한 감탄사는 최소화하세요."
        ),
        "casual_banmal": (
            "말투는 편하고 친근한 반말을 사용하세요. "
            "상대를 친구처럼 대하되, 막말이나 공격적인 표현은 절대 사용하지 마세요."
        ),
    }.get(tone, "")
    
    prompt = (
        "너는 Slack DM 답장 후보 3개를 만들어주는 비서야. "
        "각 답장은 1~2문장으로 자연스럽고 상황에 맞아야 한다.\n"
        f"{tone_instruction}"
    )

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