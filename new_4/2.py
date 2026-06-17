import os
from datetime import datetime
from openai import OpenAI

api_key = os.getenv('QWEN_API_KEY')
client = OpenAI(api_key=api_key, base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")

log_file = open("log.txt", "a", encoding="utf-8")


def log(text):
    t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_file.write(f"[{t}] {text}\n")
    log_file.flush()


def ai_chat(messages):
    response = client.chat.completions.create(
        model="qwen-plus",
        messages=messages
    )
    ai_reply = response.choices[0].message.content
    return ai_reply


if __name__ == "__main__":
    log('对话开始')
    my_prompt = '''
    你是一个有10年某地点旅游经验的导游，从以下几个方向介绍本此旅游
    【时间】【地点】【活动】【交通】（要求内容精简，可以增加美食推荐和避坑指南。）
    ，回答时注意导游身份，使用热情，专业的语气。
    
    '''

    messages = [{"role": "system", "content": my_prompt}]
    while True:
        user1 = input('请输入：')
        if not user1:
            break
        messages.append({"role": "user", "content": user1})
        b = ai_chat(messages)
        messages.append({"role": "system", "content": b})
        log(f'system prompt: {user1}')
        log(f'user prompt: {b}')
        print(b)
    log('对话结束')

