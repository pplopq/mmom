import os
from datetime import datetime
from openai import OpenAI

api_key = os.getenv('QWEN_API_KEY')
client = OpenAI(api_key=api_key, base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")

log_file = open("chat1.log", "a", encoding="utf-8")
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
    你是一个耐心，热情，乐于助人的电商客服专家，回答内容精简，符合客服身份
    
    '''



    # '''
    # 【角色】设定是你在对话中的身份
    # 【精确任务】明确核心行动与细节要求
    # 【语气】定义文字的情感与风格
    # 【背景】补充关键背景信息
    # 【输出格式】规范内容的呈现形式
    # 【示例】提供简短的参考片段
    # '''
    messages =[{"role": "system", "content": my_prompt}]
    while True:
        user1 = input('请输入：')
        if not user1:
            break
        messages.append({"role": "user", "content": user1})
        b=ai_chat(messages)
        messages.append({"role": "system", "content": b})
        log(f'system prompt: {user1}')
        log(f'user prompt: {b}')
        print(b)
    log('对话结束')
