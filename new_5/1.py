import json
import os
from openai import OpenAI
import re
from msilib import text

from pydantic import BaseModel, Field, ValidationError
import json
import requests
from datetime import datetime, timedelta
from openai import OpenAI
import os
import time
from concurrent.futures import ThreadPoolExecutor

client = OpenAI(
    api_key=os.getenv('QWEN_API_KEY'),
    base_url='https://dashscope.aliyuncs.com/compatible-mode/v1'
)
'''
#1
client = OpenAI(
    api_key=os.getenv('QWEN_API_KEY'),
    base_url='https://dashscope.aliyuncs.com/compatible-mode/v1'
)


class ConversationState(Enum):
    WAITING = "等待用户"
    SUMMARIZING = "生成摘要"

class ConversationSession:
    def __init__(self, session_id, role_name, tags):
        self.session_id = session_id
        self.role_name = role_name
        self.tags = tags
        self.turn_count = 0
        self.state = None

    def start(self):
        # 模拟启动逻辑
        pass

    def end(self):
        # 模拟结束逻辑
        pass

    def __str__(self):
        return (f"Session({self.session_id}, "
                f"{self.role_name}, "
                f"Tags: {self.tags},"
                f" Turns: {self.turn_count}, "
                f"State: {self.state})"
        )
session = ConversationSession(
    session_id = 'sess_001',
    role_name = '机器学习学习助手',
    tags = ['Python','面试备考']
)

print(session)
session.start()
print('启动后',session)

session.turn_count = 3
session.state =ConversationState.WAITING
print('聊完3轮，等待用户',session)

session.state = ConversationState.SUMMARIZING
print('正在生成摘要',session)

session.end()
print('结束后',session)

#2
client = OpenAI(
    api_key=os.getenv('QWEN_API_KEY'),
    base_url='https://dashscope.aliyuncs.com/compatible-mode/v1'
)

class RoleManager:
    """多角色管理器"""

    def __init__(self, model: str = "qwen-turbo"):
        self.model = model
        self.roles: dict[str, dict] = {}        # 角色库
        self.role_histories: dict[str, list] = {}  # 各角色独立历史
        self.current_role: str | None = None    # 当前角色

    def register_role(self, role_id: str, name: str, system_prompt: str, description: str = ""):
        """注册一个角色"""
        self.roles[role_id] = {
            "name":          name,
            "system_prompt": system_prompt,
            "description":   description
        }
        self.role_histories[role_id] = []
        print(f"角色 [{name}] 注册成功 (id: {role_id})")

    def switch_role(self, role_id: str, keep_history: bool = False):
        """切换当前角色"""
        if role_id not in self.roles:
            raise ValueError(f"角色 {role_id} 不存在")

        old_role = self.current_role
        self.current_role = role_id

        if not keep_history:
            # 切换时可选择是否清空该角色的历史
            pass

        role_name = self.roles[role_id]["name"]
        print(f"角色切换：{self.roles[old_role]['name'] if old_role else '无'} → {role_name}")

    def chat(self, user_input: str) -> str:
        """用当前角色对话"""
        if self.current_role is None:
            raise RuntimeError("未设置当前角色，请先调用 switch_role()")

        role = self.roles[self.current_role]
        history = self.role_histories[self.current_role]

        history.append({"role": "user", "content": user_input})

        messages = [{"role": "system", "content": role["system_prompt"]}] + history

        response = client.chat.completions.create(
            model=self.model,
            messages=messages
        )
        reply = response.choices[0].message.content
        history.append({"role": "assistant", "content": reply})
        return reply

    def auto_route(self, user_input: str) -> str:
        """自动路由：让 AI 判断该用哪个角色，然后切换并回答"""
        role_descriptions = "\n".join(
            f"- {rid}: {info['name']} - {info['description']}"
            for rid, info in self.roles.items()
        )

        routing_prompt = f"""根据用户输入，选择最合适的角色ID来回答。
只输出角色ID，不要任何其他内容。

可用角色：
{role_descriptions}

用户输入：{user_input}
"""
        routing_response = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": routing_prompt}]
        )
        role_id = routing_response.choices[0].message.content.strip()

        # 容错：如果返回的不是有效 role_id，用第一个角色
        if role_id not in self.roles:
            role_id = list(self.roles.keys())[0]

        self.switch_role(role_id)
        return self.chat(user_input)

    def list_roles(self):
        """显示所有角色"""
        print("\n=== 已注册角色 ===")
        for rid, info in self.roles.items():
            marker = " ← 当前" if rid == self.current_role else ""
            print(f"  [{rid}] {info['name']}: {info['description']}{marker}")


# 构建一个客服系统
manager = RoleManager()

# manager.register_role(
#     "tech",
#     "技术支持",
#     "你是专业技术支持工程师，解答产品技术问题，答案要具体准确。",
#     "处理技术问题、bug 报告、使用教程"
# )
#
# manager.register_role(
#     "sales",
#     "销售顾问",
#     "你是热情的销售顾问，了解产品优势，引导用户购买，回答要有亲和力。",
#     "产品介绍、价格咨询、购买建议"
# )
#
# manager.register_role(
#     "complaint",
#     "投诉处理",
#     "你是有同理心的投诉处理专员，先安抚情绪，再解决问题，语气要温柔耐心。",
#     "处理投诉、退款申请、纠纷协调"
# )
manager.register_role(
    "knowledge_teacher",
    "解释概念",
    "你是各类知识专家，解释概念，答案要详细准确。",
    "解释概念，学习概念"
)

manager.register_role(
    "quiz_master",
    "教师",
    "你是老师，出选择题判断题考察理解",
    "出测试题"
)

manager.register_role(
    "study_planner",
    "计划专家",
    "你是专业的计划制定专家，制定学习计划和复习安排，语气要温柔耐心。",
    "制定计划"
)
manager.list_roles()

# 自动路由测试
test_inputs = [
    "学【装饰器】概念",
    "出3道装饰器测试题",
    "制定装饰器复习计划"
]
#
# for user_input in test_inputs:
#     print(f"\n用户：{user_input}")
#     reply = manager.auto_route(user_input)
#     print(f"AI [{manager.roles[manager.current_role]['name']}]：{reply[:100]}...")


# manager.switch_role("knowledge_teacher")
# print(manager.chat(test_inputs[0]))
# manager.switch_role("quiz_master")
# print(manager.chat(test_inputs[1]))
# manager.switch_role("study_planner")
# print(manager.chat(test_inputs[2]))

print(manager.roles.items)


#3
client = OpenAI(
    api_key=os.getenv('QWEN_API_KEY'),
    base_url='https://dashscope.aliyuncs.com/compatible-mode/v1'
)
class SummaryConversationManager:
    """带摘要压缩的对话管理器"""

    def __init__(
        self,
        system_prompt: str,
        model: str = "qwen-turbo",
        compress_every: int = 6,   # 每 6 轮压缩一次
        keep_recent: int = 3       # 压缩后保留最近 3 轮原文
    ):
        self.system_prompt = system_prompt
        self.model = model
        self.compress_every = compress_every
        self.keep_recent = keep_recent
        self.history: list[dict] = []
        self.summary: str = ""     # 历史摘要（压缩的结果）
        self.turn_count = 0

    def _compress(self):
        """压缩历史：把早期历史总结成摘要"""
        print("\n[系统] 正在压缩对话历史...")

        # 准备要压缩的部分（保留最近 keep_recent 轮）
        keep_count = self.keep_recent * 2
        to_compress = self.history[:-keep_count] if len(self.history) > keep_count else []
        recent = self.history[-keep_count:] if len(self.history) > keep_count else self.history

        if not to_compress:
            return  # 没有需要压缩的内容

        # 生成新摘要
        history_text = "\n".join(
            f"{'用户' if m['role']=='user' else 'AI'}: {m['content']}"
            for m in to_compress
        )

        existing_summary = f"已有摘要：\n{self.summary}\n\n" if self.summary else ""

        compress_prompt = f"""{existing_summary}请将以下对话补充摘要到已有摘要中，保留关键事实、用户偏好、重要决策：

{history_text}

要求：
1. 摘要控制在200字以内
2. 用第三人称描述（"用户表示..."）
3. 突出关键信息"""

        response = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": compress_prompt}]
        )
        self.summary = response.choices[0].message.content

        # 用摘要替换旧历史
        self.history = recent
        print(f"[系统] 压缩完成，历史从 {len(to_compress)+len(recent)} 条压缩至 {len(recent)} 条")
        print(f"[摘要] {self.summary[:80]}...")

    def chat(self, user_input: str) -> str:
        """对话，自动触发摘要压缩"""
        self.turn_count += 1
        self.history.append({"role": "user", "content": user_input})

        # 构建消息：system + 摘要（如有）+ 近期历史
        messages = [{"role": "system", "content": self.system_prompt}]

        if self.summary:
            messages.append({
                "role": "system",
                "content": f"[对话摘要 - 之前聊过的内容]\n{self.summary}"
            })

        messages.extend(self.history)

        response = client.chat.completions.create(
            model=self.model,
            messages=messages
        )
        reply = response.choices[0].message.content
        self.history.append({"role": "assistant", "content": reply})

        # 达到压缩阈值时触发压缩
        if self.turn_count % self.compress_every == 0:
            self._compress()

        return reply


# 测试长对话
mgr = SummaryConversationManager(
    system_prompt="你是一个旅游规划师，帮用户规划旅行。记住用户提到的偏好和需求。",
    compress_every=4,
    keep_recent=2
)

conversations = [
    "我想去日本旅游，喜欢安静的地方，不喜欢人多的景点",
    "我的预算大概是1万元，行程10天",
    "我对历史文化很感兴趣，喜欢寺庙和神社",
    "我不能吃海鲜，对花粉过敏",
    "出发时间大概是明年三月",
    "请给我推荐一个详细的10天行程"  # 这时已经压缩过了，看看 AI 还记得多少
]

for msg in conversations:
    print(f"\n用户：{msg}")
    reply = mgr.chat(msg)
    print(f"AI：{reply[:120]}...")

#4

class SummaryConversationManager:
    """带摘要压缩的对话管理器"""

    def __init__(
        self,
        system_prompt: str,
        model: str = "qwen-turbo",
        compress_every: int = 6,   # 每 6 轮压缩一次
        keep_recent: int = 3       # 压缩后保留最近 3 轮原文
    ):
        self.system_prompt = system_prompt
        self.model = model
        self.compress_every = compress_every
        self.keep_recent = keep_recent
        self.history: list[dict] = []
        self.summary: str = ""     # 历史摘要（压缩的结果）
        self.turn_count = 0

    def _compress(self):
        """压缩历史：把早期历史总结成摘要"""
        print("\n[系统] 正在压缩对话历史...")

        # 准备要压缩的部分（保留最近 keep_recent 轮）
        keep_count = self.keep_recent * 2
        to_compress = self.history[:-keep_count] if len(self.history) > keep_count else []
        recent = self.history[-keep_count:] if len(self.history) > keep_count else self.history

        if not to_compress:
            return  # 没有需要压缩的内容

        # 生成新摘要
        history_text = "\n".join(
            f"{'用户' if m['role']=='user' else 'AI'}: {m['content']}"
            for m in to_compress
        )

        existing_summary = f"已有摘要：\n{self.summary}\n\n" if self.summary else ""

        compress_prompt = f"""{existing_summary}请将以下对话补充摘要到已有摘要中，保留关键事实、用户偏好、重要决策：

{history_text}

要求：
1. 摘要控制在200字以内
2. 用第三人称描述（"用户表示..."）
3. 突出关键信息"""

        response = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": compress_prompt}]
        )
        self.summary = response.choices[0].message.content

        # 用摘要替换旧历史
        self.history = recent
        print(f"[系统] 压缩完成，历史从 {len(to_compress)+len(recent)} 条压缩至 {len(recent)} 条")
        print(f"[摘要] {self.summary[:80]}...")

    def chat(self, user_input: str) -> str:
        """对话，自动触发摘要压缩"""
        self.turn_count += 1
        self.history.append({"role": "user", "content": user_input})

        # 构建消息：system + 摘要（如有）+ 近期历史
        messages = [{"role": "system", "content": self.system_prompt}]

        if self.summary:
            messages.append({
                "role": "system",
                "content": f"[对话摘要 - 之前聊过的内容]\n{self.summary}"
            })

        messages.extend(self.history)

        response = client.chat.completions.create(
            model=self.model,
            messages=messages
        )
        reply = response.choices[0].message.content
        self.history.append({"role": "assistant", "content": reply})

        # 达到压缩阈值时触发压缩
        if self.turn_count % self.compress_every == 0:
            self._compress()

        return reply
def extract_key_facts(conversation_history: list[dict], client) -> dict:
    """从对话中提取关键事实，用于后续会话"""
    history_text = "\n".join(
        f"{'用户' if m['role']=='user' else 'AI'}: {m['content']}"
        for m in conversation_history
    )

    prompt = f"""从以下对话中提取关键信息，输出 JSON 格式：

{history_text}

输出格式：
{{
    "user_name": "用户姓名（如果提到）",
    "preferences": ["偏好列表"],
    "constraints": ["限制条件列表"],
    "goals": ["目标列表"],
    "important_facts": ["其他重要事实"]
}}"""

    response = client.chat.completions.create(
        model="qwen-turbo",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)

# 测试长对话
mgr = SummaryConversationManager(
    system_prompt="你是一个旅游规划师，帮用户规划旅行。记住用户提到的偏好和需求。",
    compress_every=4,
    keep_recent=2
)

conversations = [
    "我想去日本旅游，喜欢安静的地方，不喜欢人多的景点",
    "我的预算大概是1万元，行程10天",
    "我对历史文化很感兴趣，喜欢寺庙和神社",
    "我不能吃海鲜，对花粉过敏",
    "出发时间大概是明年三月",
    "请给我推荐一个详细的10天行程"  # 这时已经压缩过了，看看 AI 还记得多少
]

for msg in conversations:
    print(f"\n用户：{msg}")
    reply = mgr.chat(msg)
    print(f"AI：{reply[:120]}...")

facts = extract_key_facts(mgr.history,client)
print(json.dumps(facts,ensure_ascii=False,indent=2))
'''
'''
#5
import json
from typing import List, Dict, Optional

# 定义消息结构
class Message:
    def __init__(self, role: str, content: str):
        self.role = role      # 'user' or 'assistant'
        self.content = content

    def to_dict(self):
        return {"role": self.role, "content": self.content}

    def __str__(self):
        return f"[{self.role.upper()}]: {self.content}"


class ConversationManager:
    """
    基础对话管理器：使用滑动窗口机制
    只保留最近的 N 轮对话，超出部分直接丢弃。
    """

    def __init__(self, max_history: int = 4):
        self.history: List[Message] = []
        self.max_history = max_history * 2  # 1轮对话包含 user + assistant 两条消息

    def add_message(self, role: str, content: str):
        """添加一条消息到历史记录"""
        self.history.append(Message(role, content))

    def get_context_messages(self) -> List[Dict]:
        """
        获取用于发送给 LLM 的上下文消息列表。
        如果超过 max_history，截取最后的部分。
        """
        # 简单的切片操作，只保留最近的记录
        if len(self.history) > self.max_history:
            return [msg.to_dict() for msg in self.history[-self.max_history:]]
        return [msg.to_dict() for msg in self.history]

    def clear(self):
        self.history.clear()


class SummaryConversationManager(ConversationManager):
    """
    摘要对话管理器：使用压缩机制
    当历史记录过长时，将早期对话压缩为一段“摘要文本”，
    并将其作为 System Prompt 或第一条消息保留，从而节省 Token 且保留关键信息。
    """

    def __init__(self, max_history: int = 4, summary_threshold: int = 6):
        super().__init__(max_history)
        self.summary_threshold = summary_threshold  # 触发摘要的消息数量阈值
        self.summary_text: str = ""                 # 存储生成的摘要内容

    def _generate_summary_mock(self, old_messages: List[Message]) -> str:
        """
        【模拟】调用 LLM 生成摘要的过程。
        在实际工程中，这里会调用 llm.invoke(...) 让模型总结 old_messages。
        """
        contents = " | ".join([f"{m.role}: {m.content}" for m in old_messages])
        return f"[系统摘要]: 用户之前提到了关于 {contents[:30]}... 等信息。"

    def add_message(self, role: str, content: str):
        """重写添加消息逻辑，加入摘要判断"""
        self.history.append(Message(role, content))

        # 检查是否需要触发摘要压缩
        # 只有当历史长度超过阈值，且当前还有未压缩的旧消息时才执行
        if len(self.history) > self.summary_threshold:
            # 计算需要被压缩的消息范围
            # 保留最近的 max_history 条消息不被压缩，压缩更早的消息
            compress_count = len(self.history) - self.max_history

            if compress_count > 0:
                messages_to_summarize = self.history[:compress_count]

                # 1. 生成新摘要 (实际开发中需拼接旧摘要和新消息一起总结)
                new_summary_part = self._generate_summary_mock(messages_to_summarize)

                # 2. 更新摘要文本 (简单拼接，实际应让 LLM 融合)
                if self.summary_text:
                    self.summary_text += "\n" + new_summary_part
                else:
                    self.summary_text = new_summary_part

                # 3. 裁剪历史，只保留最近的消息
                self.history = self.history[compress_count:]

    def get_context_messages(self) -> List[Dict]:
        """
        构建最终发给 LLM 的消息列表：
        [System/Summary] + [Recent History]
        """
        context = []

        # 如果有摘要，将其作为第一条系统级消息注入
        if self.summary_text:
            context.append({
                "role": "system",
                "content": f"以下是之前的对话摘要，请基于此继续对话：\n{self.summary_text}"
            })

        # 追加最近的详细对话历史
        context.extend([msg.to_dict() for msg in self.history])
        return context


# ================= 测试运行代码 =================

def test_managers():
    print("=" * 50)
    print("开始对比实验")
    print("=" * 50)

    # 初始化两个管理器
    normal_mgr = ConversationManager(max_history=2)  # 设为2以便快速看到效果
    summary_mgr = SummaryConversationManager(max_history=2, summary_threshold=3)

    # 模拟 5 轮对话
    scenarios = [
        ("user", "我的猫叫奥利奥，它是黑白色的。"),
        ("assistant", "好的，我记住了，奥利奥是一只黑白猫。"),
        ("user", "今天天气真不错。"),
        ("assistant", "是啊，适合带奥利奥出去散步。"),
        ("user", "我想买猫粮，有什么推荐？"),  # 第3轮，测试是否记得猫的名字
    ]

    for role, content in scenarios:
        print(f"\n--- 输入: {content} ---")

        # 1. 普通管理器处理
        normal_mgr.add_message(role, content)
        normal_ctx = normal_mgr.get_context_messages()
        print(f"[Normal] 发送Token数(模拟): {len(normal_ctx)} 条消息")
        # 打印第一条消息看是否丢失了“奥利奥”的信息
        first_msg_content = normal_ctx[0]['content'] if normal_ctx else "Empty"
        if "奥利奥" not in first_msg_content and role == "user":
             print(f"       ⚠️ 警告: 上下文中可能已丢失'奥利奥'信息 (当前首条: {first_msg_content[:20]}...)")

        # 2. 摘要管理器处理
        summary_mgr.add_message(role, content)
        summary_ctx = summary_mgr.get_context_messages()
        print(f"[Summary] 发送Token数(模拟): {len(summary_ctx)} 条消息")
        # 检查摘要中是否包含关键信息
        has_summary = any("奥利奥" in str(m) for m in summary_ctx)
        if has_summary:
            print(f"       ✅ 成功: 摘要机制保留了'奥利奥'的关键信息")

if __name__ == "__main__":
    test_managers()

#6
class ConversationManager:
    """多轮对话管理器"""

    def __init__(
        self,
        system_prompt: str,
        model: str = "qwen-turbo",
        max_history: int = 10,       # 最多保留几轮历史
        max_tokens: int = 4000       # 历史区预留 token 上限（粗略估算）
    ):
        self.system_prompt = system_prompt
        self.model = model
        self.max_history = max_history
        self.max_tokens = max_tokens
        self.history: list[dict] = []
        self.turn_count = 0

    def _estimate_tokens(self, text: str) -> int:
        """粗略估算 token 数（中文约1.5字/token，英文约4字/token）"""
        chinese_count = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        other_count = len(text) - chinese_count
        return int(chinese_count / 1.5 + other_count / 4)

    def _trim_history(self):
        """修剪历史记录：超过限制则删除最早的对话轮"""
        # 先按轮数限制
        while len(self.history) > self.max_history * 2:
            self.history.pop(0)  # 删除最早的 user
            self.history.pop(0)  # 删除对应的 assistant

        # 再按 token 估算限制
        total_tokens = sum(self._estimate_tokens(m["content"]) for m in self.history)
        while total_tokens > self.max_tokens and len(self.history) >= 2:
            removed_user = self.history.pop(0)
            removed_ai   = self.history.pop(0)
            total_tokens -= (
                self._estimate_tokens(removed_user["content"]) +
                self._estimate_tokens(removed_ai["content"])
            )

    def chat(self, user_input: str, verbose: bool = False) -> str:
        """发送消息，自动管理上下文"""
        self.turn_count += 1
        self.history.append({"role": "user", "content": user_input})

        messages = [{"role": "system", "content": self.system_prompt}] + self.history

        if verbose:
            total_msg_tokens = sum(self._estimate_tokens(m["content"]) for m in messages)
            print(f"[轮次 {self.turn_count}] 历史轮数: {len(self.history)//2}, 预计 token: ~{total_msg_tokens}")

        response = client.chat.completions.create(
            model=self.model,
            messages=messages
        )
        reply = response.choices[0].message.content
        self.history.append({"role": "assistant", "content": reply})

        # 添加后再修剪（保证本轮完整）
        self._trim_history()
        return reply

    def inject_context(self, context: str):
        """注入背景信息（不占用对话轮次）"""
        # 用 system 角色在历史中插入一条上下文
        self.history.append({
            "role": "user",
            "content": f"[背景信息，请记住：{context}]"
        })
        self.history.append({
            "role": "assistant",
            "content": "好的，我已记录这些背景信息。"
        })

    def get_summary_prompt(self) -> str:
        """生成对话摘要 prompt"""
        history_text = "\n".join(
            f"{'用户' if m['role']=='user' else 'AI'}: {m['content']}"
            for m in self.history
        )
        return f"请将以下对话总结为3-5句话的摘要：\n\n{history_text}"

class SummaryConversationManager:
    """带摘要压缩的对话管理器"""

    def __init__(
        self,
        system_prompt: str,
        model: str = "qwen-turbo",
        compress_every: int = 6,   # 每 6 轮压缩一次
        keep_recent: int = 3       # 压缩后保留最近 3 轮原文
    ):
        self.system_prompt = system_prompt
        self.model = model
        self.compress_every = compress_every
        self.keep_recent = keep_recent
        self.history: list[dict] = []
        self.summary: str = ""     # 历史摘要（压缩的结果）
        self.turn_count = 0

    def _compress(self):
        """压缩历史：把早期历史总结成摘要"""
        print("\n[系统] 正在压缩对话历史...")

        # 准备要压缩的部分（保留最近 keep_recent 轮）
        keep_count = self.keep_recent * 2
        to_compress = self.history[:-keep_count] if len(self.history) > keep_count else []
        recent = self.history[-keep_count:] if len(self.history) > keep_count else self.history

        if not to_compress:
            return  # 没有需要压缩的内容

        # 生成新摘要
        history_text = "\n".join(
            f"{'用户' if m['role']=='user' else 'AI'}: {m['content']}"
            for m in to_compress
        )

        existing_summary = f"已有摘要：\n{self.summary}\n\n" if self.summary else ""

        compress_prompt = f"""{existing_summary}请将以下对话补充摘要到已有摘要中，保留关键事实、用户偏好、重要决策：

{history_text}

要求：
1. 摘要控制在200字以内
2. 用第三人称描述（"用户表示..."）
3. 突出关键信息"""

        response = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": compress_prompt}]
        )
        self.summary = response.choices[0].message.content

        # 用摘要替换旧历史
        self.history = recent
        print(f"[系统] 压缩完成，历史从 {len(to_compress)+len(recent)} 条压缩至 {len(recent)} 条")
        print(f"[摘要] {self.summary[:80]}...")

    def chat(self, user_input: str) -> str:
        """对话，自动触发摘要压缩"""
        self.turn_count += 1
        self.history.append({"role": "user", "content": user_input})

        # 构建消息：system + 摘要（如有）+ 近期历史
        messages = [{"role": "system", "content": self.system_prompt}]

        if self.summary:
            messages.append({
                "role": "system",
                "content": f"[对话摘要 - 之前聊过的内容]\n{self.summary}"
            })

        messages.extend(self.history)

        response = client.chat.completions.create(
            model=self.model,
            messages=messages
        )
        reply = response.choices[0].message.content
        self.history.append({"role": "assistant", "content": reply})

        # 达到压缩阈值时触发压缩
        if self.turn_count % self.compress_every == 0:
            self._compress()

        return reply

mgr = SummaryConversationManager(
    system_prompt='你是一个ai工具，用1段话帮助用户解决问题，记住用户提到的偏好和需求。',
    compress_every=4,
    keep_recent=2
)

conversations = [
    '',
    '',
    '',
    '',
    ''
]
'''

# personal_ai.py - 完整项目核心

import json
import os
from openai import OpenAI
from datetime import datetime

# ── 角色定义 ────────────────────────────────────────────────
ROLES = {
    "qa": {
        "name": "知识助手",
        "prompt": """你是一个知识渊博的问答助手。
回答问题时，输出 JSON 格式：
{"answer": "回答内容", "confidence": "高/中/低", "related_topics": ["相关话题1", "相关话题2"]}""",
        "output": "json"
    },
    "task": {
        "name": "任务管家",
        "prompt": """你是一个任务管理助手。
当用户描述任务时，提取任务信息输出 JSON：
{"task_name": "任务名", "deadline": "截止日期或null", "priority": "高/中/低", "tags": ["标签"]}
当用户查询任务列表时，以文字形式回复。""",
        "output": "json"
    },
    "writing": {
        "name": "写作助手",
        "prompt": """你是一个专业写作助手，擅长各种文体。
用户可以指定写作风格（正式/轻松/文艺/幽默）。
默认风格：轻松自然。""",
        "output": "text"
    },
    "tutor": {
        "name": "学习导师",
        "prompt": """你是一位耐心细致的学习导师，擅长 Python 和 AI 领域。
根据学员水平调整讲解深度，多用类比和例子。
遇到学员不理解时，换一种方式解释。""",
        "output": "text"
    }
}

ROUTER_PROMPT = """
你是一个角色路由分类器，请根据用户输入，判断应该分配哪个角色。
只输出JSON格式：{"role_id": "角色id"}，只能从以下四个id中选一个：

- qa：用户在提问知识、事实、科普、概念类问题
- task：用户在描述待办事项、任务、计划，或要求记录/管理任务
- writing：用户要求写句子、文案、作文、段落、润色文字，或明确提到“写/创作/生成一段文字”
- tutor：用户在问编程、Python、AI相关的问题，或要求讲解知识点、代码、概念

用户输入是什么，就按上述规则判断，不要额外解释。
"""

class PersonalAI:
    def __init__(self):
        self.current_role = "qa"
        self.histories: dict[str, list] = {role_id: [] for role_id in ROLES}
        self.summaries: dict[str, str] = {role_id: "" for role_id in ROLES}
        self.tasks: list[dict] = []    # 任务列表
        self.turn_counts: dict[str, int] = {role_id: 0 for role_id in ROLES}
        self.auto_route = False
        self.compress_every = 4  # 每4轮对话触发一次压缩
        self.keep_recent = 2  # 压缩后保留最近2轮完整对话
        self.model = "qwen-turbo"

    def switch(self, role_id: str):
        if role_id not in ROLES:
            print(f"无效角色ID，可选：{', '.join(ROLES.keys())}")
            return
        self.current_role = role_id
        print(f"✓ 已切换到【{ROLES[role_id]['name']}】")

    def auto_route_role(self, user_input: str) -> str:
        """调用模型自动判定角色"""
        messages = [
            {"role": "system", "content": ROUTER_PROMPT},
            {"role": "user", "content": user_input}
        ]
        resp = client.chat.completions.create(
            model="qwen-turbo",
            messages=messages,
            response_format={"type": "json_object"}
        )
        try:
            res = json.loads(resp.choices[0].message.content)
            role_id = res.get("role_id", "qa")
            if role_id in ROLES:
                return role_id
        except Exception:
            pass
        # 解析失败默认使用知识助手
        return "qa"

    def _compress(self, role_id: str):
        """
        对话历史压缩（完全迁移自 SummaryConversationManager）
        增量合并摘要，保留指定最近轮数，精简历史上下文
        """
        print("\n[系统] 正在压缩对话历史...")
        history = self.histories[role_id]
        # 一轮对话包含 user + assistant 两条消息
        keep_count = self.keep_recent * 2
        # 分割：待压缩历史 + 保留的近期历史
        to_compress = history[:-keep_count] if len(history) > keep_count else []
        recent_history = history[-keep_count:] if len(history) > keep_count else history

        if not to_compress:
            print("[系统] 无需要压缩的内容")
            return

        # 拼接待压缩对话文本
        history_text = "\n".join(
            f"{'用户' if m['role'] == 'user' else 'AI'}: {m['content']}"
            for m in to_compress
        )

        # 拼接已有摘要
        existing_summary = f"已有摘要：\n{self.summaries[role_id]}\n\n" if self.summaries[role_id] else ""

        # 压缩提示词（沿用原有规则）
        compress_prompt = f"""{existing_summary}请将以下对话补充摘要到已有摘要中，保留关键事实、用户偏好、重要决策：

    {history_text}

    要求：
    1. 摘要控制在200字以内
    2. 用第三人称描述（"用户表示..."）
    3. 突出关键信息"""

        # 调用模型生成新摘要
        resp = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": compress_prompt}]
        )
        self.summaries[role_id] = resp.choices[0].message.content.strip()

        # 替换历史：只保留近期对话
        self.histories[role_id] = recent_history
        total_before = len(to_compress) + len(recent_history)
        print(f"[系统] 压缩完成，历史条数 {total_before} → {len(recent_history)}")
        print(f"[摘要预览] {self.summaries[role_id][:80]}...")


    def chat(self, user_input: str) -> str:
        if self.auto_route:
            auto_role = self.auto_route_role(user_input)
            self.current_role = auto_role
        role_id = self.current_role
        role = ROLES[self.current_role]
        history = self.histories[self.current_role]
        summary = self.summaries[self.current_role]

        self.turn_counts[role_id] += 1
        history.append({"role": "user", "content": user_input})

        messages = [{"role": "system", "content": role["prompt"]}]
        if summary:
            messages.append({"role": "system", "content": f"[历史摘要]\n{summary}"})
        messages.extend(history[-12:])  # 最近6轮

        kwargs = {"model": "qwen-turbo", "messages": messages}
        if role["output"] == "json":
            kwargs["response_format"] = {"type": "json_object"}

        response = client.chat.completions.create(**kwargs)
        reply = response.choices[0].message.content
        history.append({"role": "assistant", "content": reply})

        # 任务管理：解析并保存任务
        if self.current_role == "task":
            try:
                task_data = json.loads(reply)
                if "task_name" in task_data:
                    task_data["created_at"] = datetime.now().strftime("%m-%d %H:%M")
                    task_data["id"] = len(self.tasks) + 1
                    self.tasks.append(task_data)
            except (json.JSONDecodeError, KeyError):
                pass

        if self.turn_counts[role_id] % self.compress_every == 0:
            self._compress(role_id)
        return reply

    def show_tasks(self):
        if not self.tasks:
            print("暂无任务")
            return
        print("\n=== 任务列表 ===")
        for t in self.tasks:
            deadline = t.get('deadline') or '无截止日期'
            print(f"  [{t['id']}] {t['task_name']} | {t.get('priority','中')}优先 | {deadline}")

    def status(self):
        print(f"\n当前角色：【{ROLES[self.current_role]['name']}】")
        print(f"自动路由状态：{'已开启' if self.auto_route else '已关闭'}")
        print(f"任务数量：{len(self.tasks)}")
        print(f"压缩配置：每 {self.compress_every} 轮压缩，保留最近 {self.keep_recent} 轮对话")
        for rid, count in self.turn_counts.items():
            if count > 0:
                print(f"  {ROLES[rid]['name']}: {count} 轮对话")
            if self.summaries[rid]:
                print(f"  {ROLES[rid]['name']} 摘要：{self.summaries[rid][:60]}...")


def main():
    ai = PersonalAI()
    print("PersonalAI 启动！输入 /help 查看命令\n")

    COMMANDS = {
        "/qa":      ("切换知识助手",    lambda: ai.switch("qa")),
        "/task":    ("切换任务管家",    lambda: ai.switch("task")),
        "/write":   ("切换写作助手",    lambda: ai.switch("writing")),
        "/tutor":   ("切换学习导师",    lambda: ai.switch("tutor")),
        "/tasks":   ("查看任务列表",    lambda: ai.show_tasks()),
        "/status":  ("查看系统状态",    lambda: ai.status()),
        "/auto": ("切换自动路由(开/关)", lambda: setattr(ai, "auto_route", not ai.auto_route)),
        "/quit":    ("退出",           lambda: exit(0)),
    }

    while True:
        route_tag = "[自动路由]" if ai.auto_route else ""
        user_input = input(f"\n{route_tag}[{ROLES[ai.current_role]['name']}] > ").strip()
        if not user_input:
            continue

        if user_input in COMMANDS:
            desc, action = COMMANDS[user_input]
            action()
            if user_input == "/auto":
                print(f"✓ 自动路由已 {'开启' if ai.auto_route else '关闭'}")
            continue

        if user_input == "/help":
            for cmd, (desc, _) in COMMANDS.items():
                print(f"  {cmd:12} {desc}")
            continue

        reply = ai.chat(user_input)

        # 格式化输出
        if ROLES[ai.current_role]["output"] == "json":
            try:
                data = json.loads(reply)
                print(json.dumps(data, ensure_ascii=False, indent=2))
            except json.JSONDecodeError:
                print(reply)
        else:
            print(f"\n{reply}")


if __name__ == "__main__":
    main()




















