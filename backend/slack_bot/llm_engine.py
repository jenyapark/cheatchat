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


def generate_reply_candidates(messages, tone: str, relationship: str):
    try:
        if messages and messages[-1].get("direction") == "outgoing":
            return ["(내가 보낸 메시지이므로 답장을 생성하지 않습니다.)"]
        recent = messages[-3:]
        context = "\n".join([f"{m['direction']}: {m['text']}" for m in recent])
        last = recent[-1]["text"]

        prompt = f"""
대화 내용:
{context}

마지막 메시지:
"{last}"

선택된 말투: "{tone}"
대화 상대와의 관계: "{relationship}"

조건:
- 1~2문장
- 자연스럽게
- 답장 후보 3개 생성
- 1), 2), 3) 또는 1. 2. 3. 아무 형식도 허용
"""

        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)
        raw = response.text.strip()

        lines = raw.split("\n")

        candidates = []
        for line in lines:
            line = line.strip()
            if line.startswith(("1)", "1.", "1 )")):
                candidates.append(line.split(")",1)[-1].split(".",1)[-1].strip())
            elif line.startswith(("2)", "2.", "2 )")):
                candidates.append(line.split(")",1)[-1].split(".",1)[-1].strip())
            elif line.startswith(("3)", "3.", "3 )")):
                candidates.append(line.split(")",1)[-1].split(".",1)[-1].strip())

        # 혹시 번호 못 찾았으면 그냥 전체 문장에서 문장 단위 분리
        if not candidates:
            sentences = [s.strip() for s in raw.split("\n") if len(s.strip()) > 5]
            candidates = sentences[:3]

        return candidates[:3]

    except Exception as e:
        print("[LLM ERROR]", e)
        return []


    
def generate_contextual_reply(conversation: list, tone: str = "friendly_formal", limit: int = 8):

    tone_instruction = {
        "friendly_formal": "친근하고 따뜻한 존댓말(~요)으로 자연스럽게.",
        "soft_formal": "부드럽고 공손한 직장인 말투(~습니다)로 간결하게.",
        "casual": "친근하고 자연스러운 반말로.",
    }.get(tone, "")

    if not conversation:
        return []

    # 대화를 시간순 정렬
    conversation = sorted(conversation, key=lambda x: x.get("ts", 0))[-limit:]

    # 마지막 메시지가 상대방(incoming)인지 체크
    last = conversation[-1]
    if last["direction"] != "incoming":
        return ["(마지막 메시지가 상대 메시지가 아니라 답장이 필요하지 않습니다.)"]

    # 전체 대화를 하나의 prompt로 구성
    dialog_text = "\n".join(
        f"{'상대' if m['direction']=='incoming' else '나'}: {m['text']}"
        for m in conversation
    )

    prompt = f"""
너는 Slack DM 대화를 기반으로 상황을 파악하고,
마지막 상대방 메시지에 대한 답장 후보 3개를 생성하는 어시스턴트야.

다음은 Slack DM 대화의 최근 내용입니다:

{dialog_text}

위 맥락을 바탕으로, 마지막 상대 메시지 "{last['text']}"에 대한
답장 후보 3개를 만들어 주세요.

선택된 말투는 : {tone_instruction}

조건:
- 답장은 1~2문장
- 자연스럽고 맥락을 반영
- 번호를 붙여 출력 번호 형식: 1) ~~~

"""

    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)
        raw = response.text.strip()

        candidates = []
        for line in raw.split("\n"):
            if ")" in line:
                try:
                    cands = line.split(")", 1)[1].strip()
                    if cands:
                        candidates.append(cands)
                except:
                    continue

        return candidates[:3]

    except Exception as e:
        print("[LLM ERROR - contextual reply]", e)
        return []
