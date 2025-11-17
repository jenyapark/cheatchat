# imports

import os
from dotenv import load_dotenv
from slack_sdk import WebClient
from openai import OpenAI
from IPython.display import Markdown, display, update_display
from llmcl2 import partner_msgs, my_msgs


load_dotenv()
<<<<<<< HEAD
print(">>> SLACK_BOT_TOKEN =", os.getenv("SLACK_BOT_TOKEN"))

client = WebClient(token="SLACK_BOT_TOKEN")
=======
client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))
>>>>>>> 7e1e71e4ca081889b72a46c8e4140349b53d15b6
user_id = "U09QQB0J7S6"  # 내 user id
partner_id = "U09RBS32291"

dm_channel_id = None


#  DM 채널 ID 가져오기 (상대방과의 채팅방)
dm_list = client.conversations_list(types="im")

for dm in dm_list["channels"]:
    if dm.get("user") == partner_id:
        dm_channel_id = dm["id"] # user = 상대방 user_id


print(dm_channel_id)


history = client.conversations_history(channel=dm_channel_id, limit=100)

# user / 상대방 메시지 분리

for msg in history["messages"]:
    if msg["user"] == user_id:
        my_msgs.append(msg["text"])
    else:
        partner_msgs.append(msg["text"])



load_dotenv(override=True)
openai_api_key = os.getenv('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')

if openai_api_key:
    print(f"OpenAI API Key exists and begins {openai_api_key[:8]}")
else:
    print("OpenAI API Key not set")

openai = OpenAI()

relations = ['친한 친구', '연인', '동료', '가족', '직장', '기타']
styles = ['반말로, 편하게', '존댓말, 부드럽게', '밝고 활기차게', '차분하고 간결하게' ]
style = styles[1]

#대화 내용을 history에 받아오고 이걸 넣어주기
#history에서 role을 통해 user, assistant(상대자) 구분해주기





gpt_model = "gpt-4o-mini"

# gpt_system = " 너는 두 사람의 대화를 보고, 사용자의 말투를" + style + "반영해; \
#               상대가 방금 보낸 메시지에 대한 답장 후보 2~3개만 제안하는 코치야; \
#               대화는 $partner_msgs 와 $my_msgs 로 각각 상대가 보낸 메세지, 사용자가 보낸 메세지로 구분돼; \
#               두 사람의 관계: $relation; \
#               각 답변은 1~2문장으로 자연스럽게"

gpt_system = f"""
너는 두 사람의 대화를 보고 사용자의 말투를 {style} 반영해서 답장 후보 2~3개를 제안하는 어시스턴트야.

대화 맥락은 다음과 같이 제공됨:
- partner_msgs = 상대방이 한 말
- my_msgs = 내가 한 말

두 사람의 관계: {relations[0]}

조건:
- 각 답장은 1~2문장
- 자연스럽고 맥락에 맞아야 함
- 너무 장황하게 설명하지 말고 '답장 후보'만 출력해
"""

#메세지를 보낸것을 여기 gpt_messages 리스트에 append하고 상대에게 온 메세지를 claude_messages 리스트에 매번 append 해주기
#gpt_messages = ["안녕하세요"]
#claude_messages = ["지우씨, 오늘까지 제출해야 서류 어디에 제출했어?"]

#여기서 gpt_messages에 내가 보낸 메세지, claude_messages에 상대가 보낸 메세지를 가져오기
#내가 assistant가 되는것임. 
def call_gpt():
    messages = [{"role": "system", "content": gpt_system}]
    for partner, mine in zip(partner_msgs, my_msgs):
        messages.append({"role": "user", "content": partner})
        messages.append({"role": "assistant", "content": mine})

    messages.append({"role": "user", "content" : partner_msgs[-1]})


    completion = openai.chat.completions.create(
        model=gpt_model,
        messages=messages
    )
    print(messages)
    return completion.choices[0].message.content

"""
과거 대화 패턴 분석

내 말투 학습

관계 기반 톤 조절

마지막 user(상대방) 메시지 → 핵심 입력

assistant 역할로 자연스러운 답장 2~3개 생성
"""
call_gpt()