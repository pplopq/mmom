import os
from openai import OpenAI


class ConversationManager:
    """多轮对话管理器"""

    def __init__(
        self,
        system_prompt: str,
        model: str = "qwen-plus",
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
    #
    # def inject_context(self, context: str):
    #     """注入背景信息（不占用对话轮次）"""
    #     # 用 system 角色在历史中插入一条上下文
    #     self.history.append({
    #         "role": "user",
    #         "content": f"[背景信息，请记住：{context}]"
    #     })
    #     self.history.append({
    #         "role": "assistant",
    #         "content": "好的，我已记录这些背景信息。"
    #     })
    #
    # def get_summary_prompt(self) -> str:
    #     """生成对话摘要 prompt"""
    #     history_text = "\n".join(
    #         f"{'用户' if m['role']=='user' else 'AI'}: {m['content']}"
    #         for m in self.history
    #     )
    #     return f"请将以下对话总结为3-5句话的摘要：\n\n{history_text}"

client = OpenAI(
        api_key=os.getenv('QWEN_API_KEY'),
        base_url='https://dashscope.aliyuncs.com/compatible-mode/v1'
    )

# 使用演示
conv = ConversationManager(
    system_prompt="简单ai助手，只要直接回答结果，不用分析",
    max_history=4
)

print(conv.chat("你是小明，你喜欢吃苹果", verbose=True))
print(conv.chat("2+2等于几", verbose=True))
print(conv.chat("你是谁，喜欢吃什么", verbose=True))
print(conv.chat('4+4等于几', verbose=True))
print(conv.chat("2+2等于几", verbose=True))
print(conv.chat("3+3等于几", verbose=True))
print(conv.chat('5+5等于几', verbose=True))
print(conv.chat('你是谁，喜欢吃什么', verbose=True))