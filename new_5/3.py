import re
import json
import requests
import os
import time
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, ValidationError
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor

# ===================== 客户端 & 密钥配置 =====================
client = OpenAI(
    api_key=os.getenv('QWEN_API_KEY'),
    base_url='https://dashscope.aliyuncs.com/compatible-mode/v1'
)
AMAP_API_KEY = "7c5ee1fd7a3fae4109edc23152a0c429"

# ===================== 工具函数定义 =====================
# 工具1：数学计算
def math_calc(num1: float | int, num2: float | int | None, op: str):
    try:
        if op == "add":
            res = num1 + num2
        elif op == "sub":
            res = num1 - num2
        elif op == "mul":
            res = num1 * num2
        elif op == "div":
            if num2 == 0:
                return "除数不能为0"
            res = num1 / num2
        elif op == "sqrt":
            if num1 < 0:
                return "负数无法开方"
            res = num1 ** 0.5
        else:
            return "不支持的运算类型"
        return f"计算结果:{res}"
    except Exception as e:
        return f"计算异常: {str(e)}"

# 工具2：文件读取（安全目录限制）
SAFE_ROOT = os.path.abspath(".")
def file_read(file_path: str):
    abs_path = os.path.abspath(file_path)
    if not abs_path.startswith(SAFE_ROOT):
        return "读取失败: 禁止越权访问文件"
    if not os.path.exists(abs_path):
        return "文件不存在"
    try:
            with open(abs_path, "r", encoding="utf-8") as f:
                content = f.read()
            return f"文件读取成功:{content}"
    except Exception as e:
        return f"读取文件异常: {str(e)}"

# 工具3：日期计算
def date_calc(start_date: str, end_date: str):
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
    except ValueError:
        return '起始时间不合法'
    try:
        end = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        return '结束时间不合法'
    delta_days = (end - start).days
    return f"日期计算成功，两个日期相差 {abs(delta_days)} 天"

# 工具4：当前天气
def get_current_weather(location: str):
    geo_url = "https://restapi.amap.com/v3/geocode/geo"
    geo_params = {
        "address": location,
        "key": AMAP_API_KEY
    }
    try:
        geo_response = requests.get(geo_url, params=geo_params).json()
        if geo_response["status"] != "1" or not geo_response["geocodes"]:
            return f"抱歉，未能找到城市 {location} 的相关信息。"
        city_code = geo_response["geocodes"][0]["adcode"]

        weather_url = "https://restapi.amap.com/v3/weather/weatherInfo"
        weather_params = {
            "city": city_code,
            "key": AMAP_API_KEY,
            "extensions": "base"
        }
        weather_response = requests.get(weather_url, params=weather_params).json()
        if weather_response["status"] != "1":
            return f"抱歉，获取 {location} 的天气信息失败。"
        live = weather_response["lives"][0]
        weather_info = (
            f"{location} 现在是 {live['weather']}，"
            f"气温 {live['temperature']}°C，"
            f"湿度 {live['humidity']}%，"
            f"风向 {live['winddirection']}，风力 {live['windpower']} 级。"
        )
        return weather_info
    except Exception as e:
        return f"查询天气时发生错误：{e}"

# 工具5：未来天气
def get_forecast_weather(location: str):
    try:
        geo_url = "https://restapi.amap.com/v3/geocode/geo"
        geo_params = {
            "address": location,
            "key": AMAP_API_KEY
        }
        geo_response = requests.get(geo_url, params=geo_params).json()
        if geo_response["status"] != "1" or not geo_response["geocodes"]:
            return f"抱歉，未能找到城市 {location} 的相关信息。"
        city_code = geo_response["geocodes"][0]["adcode"]

        weather_url = "https://restapi.amap.com/v3/weather/weatherInfo"
        weather_params = {
            "city": city_code,
            "key": AMAP_API_KEY,
            "extensions": "all"
        }
        weather_response = requests.get(weather_url, params=weather_params).json()
        if weather_response["status"] != "1":
            return f"抱歉，获取 {location} 的天气预报失败。"
        all_forecasts = weather_response["forecasts"][0]["casts"]
        future_forecasts = all_forecasts[1:]
        forecast_info = f"{location} 未来3天的天气预报：\n"
        for day in future_forecasts:
            forecast_info += (
                f"- {day['date']} ({day['week']})：{day['dayweather']}，"
                f"气温 {day['daytemp']}°C ~ {day['nighttemp']}°C\n"
            )
        return forecast_info
    except Exception as e:
        return f"查询天气预报时发生错误：{e}"

# 工具6：系统时间
def get_current_time():
    current_datetime = datetime.now()
    formatted_time = current_datetime.strftime('%Y-%m-%d %H:%M:%S')
    return f"当前时间：{formatted_time}。"

# 工具映射：函数名 -> 实际函数
TOOL_MAP = {
    "get_current_time": get_current_time,
    "get_current_weather": get_current_weather,
    "get_forecast_weather": get_forecast_weather,
    "math_calc": math_calc,
    "file_read": file_read,
    "date_calc": date_calc
}

# ===================== Pydantic 参数模型 & 工具描述 =====================
class A1(BaseModel):
    """对应 get_current_time，无参数"""
    pass

class A2(BaseModel):
    """对应 get_current_weather / get_forecast_weather"""
    location: str = Field(..., description="城市或县区，比如北京市、杭州市、余杭区等。")

class A4(BaseModel):
    """对应 math_calc"""
    num1: float | int = Field(..., description="第一个数字（或被开方数）")
    num2: float | int | None = Field(None, description="第二个数字，sqrt运算时可不传")
    op: str = Field(..., description="运算类型，可选 add/sub/mul/div/sqrt")

class A5(BaseModel):
    """对应 file_read"""
    file_path: str = Field(..., description="要读取的文件路径，仅允许读取当前目录及子目录下的文件")

class A6(BaseModel):
    """对应 date_calc"""
    start_date: str = Field(..., description="起始日期，格式 YYYY-MM-DD")
    end_date: str = Field(..., description="结束日期，格式 YYYY-MM-DD")

def pydantic_to_tool_definition(model, name, desc):
    json_schema = model.model_json_schema()
    return {
        'type': 'function',
        'function': {
            'name': name,
            'description': desc,
            'parameters': json_schema
        }
    }

tools = [
    pydantic_to_tool_definition(A1, 'get_current_time', '查询系统当前时间'),
    pydantic_to_tool_definition(A2, 'get_current_weather', '查询指定城市的实时天气'),
    pydantic_to_tool_definition(A2, 'get_forecast_weather', '查询指定城市未来几天的天气预报'),
    pydantic_to_tool_definition(A4, 'math_calc', '数学计算器，支持加减乘除和开平方运算'),
    pydantic_to_tool_definition(A5, 'file_read', '读取当前目录及子目录下的文本文件内容'),
    pydantic_to_tool_definition(A6, 'date_calc', '日期计算工具，输入起止日期计算相隔天数')
]
tool_name = [tool["function"]["name"] for tool in tools]
print(f"创建了{len(tools)}个工具，为：{tool_name}\n")

# ===================== 角色配置 & 提示词 =====================
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

MODEL_PROMPT = """你是一个智能助手，可以调用外部工具完成用户请求。
规则：
- 查询时间 → 调用 get_current_time
- 查询实时天气 → 调用 get_current_weather
- 查询未来天气预报 → 调用 get_forecast_weather
- 数学计算(加减乘除/开方) → 调用 math_calc
- 读取本地文本文件 → 调用 file_read
- 计算两个日期间隔天数 → 调用 date_calc
根据问题自动选择工具，工具返回结果后整理成自然语言回答用户。"""

ROUTER_PROMPT = """
你是一个角色路由分类器，请根据用户输入，判断应该分配哪个角色。
只输出JSON格式：{"role_id": "角色id"}，只能从以下四个id中选一个：
- qa：用户在提问知识、事实、科普、概念类问题
- task：用户在描述待办事项、任务、计划，或要求记录/管理任务
- writing：用户要求写句子、文案、作文、段落、润色文字
- tutor：用户在问编程、Python、AI相关问题或讲解代码、知识点
不要额外解释。
"""

# ===================== 主AI类（含角色、摘要、Function Calling） =====================
class PersonalAI:
    def __init__(self):
        self.current_role = "qa"
        self.histories: dict[str, list] = {role_id: [] for role_id in ROLES}
        self.summaries: dict[str, str] = {role_id: "" for role_id in ROLES}
        self.tasks: list[dict] = []
        self.turn_counts: dict[str, int] = {role_id: 0 for role_id in ROLES}
        self.auto_route = False
        self.compress_every = 4
        self.keep_recent = 2
        self.model = "qwen-turbo"

    def switch(self, role_id: str):
        if role_id not in ROLES:
            print(f"无效角色ID，可选：{', '.join(ROLES.keys())}")
            return
        self.current_role = role_id
        print(f"✓ 已切换到【{ROLES[role_id]['name']}】")

    def auto_route_role(self, user_input: str) -> str:
        messages = [
            {"role": "system", "content": MODEL_PROMPT},
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
        return "qa"

    def _compress(self, role_id: str):
        """对话历史摘要压缩"""
        print("\n[系统] 正在压缩对话历史...")
        history = self.histories[role_id]
        keep_count = self.keep_recent * 2
        to_compress = history[:-keep_count] if len(history) > keep_count else []
        recent_history = history[-keep_count:] if len(history) > keep_count else history

        if not to_compress:
            print("[系统] 无需要压缩的内容")
            return

        history_text = "\n".join(
            f"{'用户' if m['role'] == 'user' else 'AI'}: {m['content']}"
            for m in to_compress
        )
        existing_summary = f"已有摘要：\n{self.summaries[role_id]}\n\n" if self.summaries[role_id] else ""
        compress_prompt = f"""{existing_summary}请将以下对话补充摘要到已有摘要中，保留关键事实、用户偏好、重要决策：
{history_text}
要求：
1. 摘要控制在200字以内
2. 用第三人称描述（"用户表示..."）
3. 突出关键信息"""

        resp = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": compress_prompt}]
        )
        self.summaries[role_id] = resp.choices[0].message.content.strip()
        self.histories[role_id] = recent_history
        total_before = len(to_compress) + len(recent_history)
        print(f"[系统] 压缩完成，历史条数 {total_before} → {len(recent_history)}")
        print(f"[摘要预览] {self.summaries[role_id][:80]}...")

    def _call_tool(self, tool_name: str, args: dict) -> str:
        """执行本地工具函数"""
        if tool_name not in TOOL_MAP:
            return f"错误：未知工具 {tool_name}"
        func = TOOL_MAP[tool_name]
        try:
            return func(**args)
        except Exception as e:
            return f"工具执行异常：{str(e)}"

    def chat(self, user_input: str) -> str:
        # 自动路由角色
        if self.auto_route:
            self.current_role = self.auto_route_role(user_input)
        role_id = self.current_role
        role_cfg = ROLES[role_id]
        history = self.histories[role_id]
        summary = self.summaries[role_id]

        self.turn_counts[role_id] += 1
        history.append({"role": "user", "content": user_input})

        # 组装基础上下文
        messages = [{"role": "system", "content": MODEL_PROMPT}]
        messages.append({"role": "system", "content": role_cfg["prompt"]})
        if summary:
            messages.append({"role": "system", "content": f"[历史摘要]\n{summary}"})
        messages.extend(history[-12:])

        # 第一轮：判断是否调用工具
        response = client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tools
        )
        msg = response.choices[0].message

        # ========== Function Calling 逻辑 ==========
        if msg.tool_calls:
            print("\n[系统] 检测到工具调用，开始执行...")
            for tool_call in msg.tool_calls:
                t_name = tool_call.function.name
                t_args = json.loads(tool_call.function.arguments)
                # 执行工具
                tool_result = self._call_tool(t_name, t_args)
                print(f"[工具 {t_name}] 执行结果：{tool_result[:100]}...")

                # 追加工具调用记录 & 结果
                history.append({
                    "role": "assistant",
                    "tool_calls": [tool_call.dict()]
                })
                history.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": t_name,
                    "content": tool_result
                })

            # 第二轮：传入工具结果，生成最终回答
            final_messages = [{"role": "system", "content": MODEL_PROMPT}]
            final_messages.append({"role": "system", "content": role_cfg["prompt"]})
            if summary:
                final_messages.append({"role": "system", "content": f"[历史摘要]\n{summary}"})
            final_messages.extend(history[-12:])

            if role_cfg["output"] == "json":
                final_resp = client.chat.completions.create(
                    model=self.model,
                    messages=final_messages,
                    response_format={"type": "json_object"}
                )
            else:
                final_resp = client.chat.completions.create(
                    model=self.model,
                    messages=final_messages
                )
            final_reply = final_resp.choices[0].message.content
            history.append({"role": "assistant", "content": final_reply})
            reply = final_reply
        else:
            # 不调用工具，直接返回回答
            reply = msg.content
            history.append({"role": "assistant", "content": reply})

        # 任务管家：保存任务
        if role_id == "task":
            try:
                task_data = json.loads(reply)
                if "task_name" in task_data:
                    task_data["created_at"] = datetime.now().strftime("%m-%d %H:%M")
                    task_data["id"] = len(self.tasks) + 1
                    self.tasks.append(task_data)
            except (json.JSONDecodeError, KeyError):
                pass

        # 触发摘要压缩
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

# ===================== 主入口 =====================
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
        "/auto":    ("切换自动路由(开/关)", lambda: setattr(ai, "auto_route", not ai.auto_route)),
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