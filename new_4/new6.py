import json
import os
import time
from openai import OpenAI
from jsonschema import validate,ValidationError
import xml.etree.ElementTree as ET
import re


class AIRole:
    """可持久化的 AI 角色"""

    def __init__(self, name: str, system_prompt: str, model: str = "qwen-plus"):
        self.name = name
        self.system_prompt = system_prompt
        self.model = model
        self.history: list[dict] = []  # 对话历史

    def chat(self, user_input: str) -> str:
        """发送消息，保留上下文"""
        self.history.append({"role": "user", "content": user_input})

        messages = [{"role": "system", "content": self.system_prompt}] + self.history

        response = client.chat.completions.create(
            model=self.model,
            messages=messages
        )
        reply = response.choices[0].message.content
        self.history.append({"role": "assistant", "content": reply})
        return reply

    def reset(self):
        """重置对话历史，保留角色设定"""
        self.history = []
        print(f"[{self.name}] 对话历史已清空")

    def get_history_count(self) -> int:
        return len(self.history) // 2  # 轮数

client = OpenAI(
        api_key=os.getenv('QWEN_API_KEY'),
        base_url='https://dashscope.aliyuncs.com/compatible-mode/v1'
    )
a='''
---python
def add(a,b):
   return a-b
'''
system_prompt1=f'''
##角色
你是一个严格代码审查官，这是学员的代码{a}
##行为准则
1.发现bug态度严格，要求学员修改通过后才结束
2.回答要简洁，每条解释不超过3句话
##输出格式
解释部分：2-3句话
- 代码示例：用 ```python 代码块包裹
##边界问题
-只回答python相关问题
- 不涉及政治、宗教等无关话题
- 遇到超出范围的问题，严格的引导回 Python 学习
'''
system_prompt2=f'''
##角色
你是一个温柔学习伙伴，这是学员的代码{a}
##行为准则
1.鼓励式教学，即使代码错了也先肯定亮点
2.回答要简洁，每条解释不超过3句话
##输出格式
解释部分：2-3句话
- 代码示例：用 ```python 代码块包裹
##边界问题
-只回答python相关问题
- 不涉及政治、宗教等无关话题
- 遇到超出范围的问题，礼貌地引导回 Python 学习
'''

# 创建两个不同角色
python_tutor = AIRole(
    name="学小智",
    system_prompt=system_prompt1
)

career_advisor = AIRole(
    name="职场导师",
    system_prompt=system_prompt2
)

# 测试
print(python_tutor.chat(a))
print(career_advisor.chat(a))