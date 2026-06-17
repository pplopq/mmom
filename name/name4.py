import os
from openai import OpenAI
from datetime import datetime

class Debater:
    def __init__(self, name: str, model: str, base_url: str, api_key: str):
        self.name = name
        self.model = model
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )

    def reply(self, topic: str, history_context: list):
        print(f"\n>>> {self.name} ({self.model}) 正在思考...")
        messages = [
            {"role": "system", "content": f"你是一个名为「{self.name}」的辩手。请针对辩题发表犀利、有逻辑的观点。保持简短有力。"},
            {"role": "user", "content": f"当前辩题是：{topic}。请根据以下历史记录继续发言：\n\n" + "\n".join([f"{m['role']}: {m['content']}" for m in history_context])}
        ]
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7
        )
        content = response.choices[0].message.content
        return content

#三个角色
a1= Debater(
    name="千问1",
    model="qwen3.7-plus",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    api_key=os.getenv("QWEN_API_KEY")
)
a2= Debater(
    name="千问2",
    model="qwen-plus",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    api_key=os.getenv("QWEN_API_KEY")
)
#裁判
a3= Debater(
    name="清言(裁判)",
    model="glm-4-flash",
    base_url="https://open.bigmodel.cn/api/paas/v4",
    api_key=os.getenv("GLM")
)


def main(topic: str, rounds: int = 3):
    debate_history = []  # 存储所有对话记录
    log_content = f"辩题：{topic}\n时间：{datetime.now()}\n\n"
    debaters = [a1,a2]

    # 循环辩论
    for r in range(rounds):
        print(f"第{r+1}轮")
        log_content += f"第 {r+1} 轮"
        for debater in debaters:
            # 获取回复
            reply_text = debater.reply(topic, debate_history)
            # 打印并记录
            print(f"[{debater.name}]: {reply_text}")
            log_content += f"[{debater.name}]: {reply_text}\n"
            # 更新历史
            debate_history.append(
                {"role": "user" if debater == debaters[0] else "assistant",
                 "content": f"{debater.name}: {reply_text}"}
                )

    # 裁判打分
    print("裁判评分...")
    judge_prompt = f"""
    作为公正的裁判，请阅读以下关于辩题“{topic}”的辩论记录，并对两位辩手进行打分（满分10分）和点评。
    输出格式要求：
    1. 获胜者
    2. 双方得分
    3. 简短点评
    辩论记录：
    {log_content}
    """
    response = a3.client.chat.completions.create(
        model=a3.model,
        messages=[{"role": "user", "content": judge_prompt}]
    )
    verdict = response.choices[0].message.content
    print(f"\n最终裁决:\n{verdict}")

    # 保存日志文件
    with open("debate_log.txt", "w", encoding="utf-8") as f:
        f.write(log_content + "\n\n" + verdict)
    print("辩论记录已保存至 debate_log.txt")


if __name__ == "__main__":
    topic = "人工智能未来是否会取代人类程序员？"
    main(topic)