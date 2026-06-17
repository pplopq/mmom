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

AMAP_API_KEY = "7c5ee1fd7a3fae4109edc23152a0c429"

# 工具1：数学计算
def math_calc(num1: float | int, num2: float | int, op: str):
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

#工具2：文件读取（安全目录限制）
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

#工具3：日期计算
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


#工具4：当前天气
def get_current_weather(arguments):
    location = arguments["location"]
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
#工具5：未来天气
def get_forecast_weather(arguments):
    location = arguments["location"]
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
#工具6：系统时间
def get_current_time(arguments=None):
    current_datetime = datetime.now()
    formatted_time = current_datetime.strftime('%Y-%m-%d %H:%M:%S')
    return f"当前时间：{formatted_time}。"

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
    pydantic_to_tool_definition(A1, 'get_current_time', '查询系统时间'),
    pydantic_to_tool_definition(A2, 'get_current_weather', '查询指定城市的实时天气'),
    pydantic_to_tool_definition(A2, 'get_forecast_weather', '查询指定城市未来几天的天气预报。'),
    pydantic_to_tool_definition(A4, 'math_calc', '数学计算器，支持加减乘除和开平方运算。'),
    pydantic_to_tool_definition(A5, 'file_read', '读取当前目录及子目录下的文本文件内容。'),
    pydantic_to_tool_definition(A6, 'date_calc', '日期计算工具，输入起始日期和结束日期，计算相差时间。')
]
tool_name = [tool["function"]["name"] for tool in tools]
print(f"创建了{len(tools)}个工具，为：{tool_name}\n")

messages = [
    {
        "role": "system",
        "content": """你是一个很有帮助的助手。
        - 如果用户提问关于天气的问题，请调用 ‘get_current_weather’ 函数。
        - 如果用户提问关于未来天气预报的问题，请调用 ‘get_forecast_weather’ 函数。
        - 如果用户提问关于时间的问题，请调用‘get_current_time’函数。
        - 如果用户需要数学计算（加减乘除/开平方），请调用‘math_calc’函数。
        - 如果用户需要读取文件内容，请调用‘file_read’函数。
        - 如果用户需要日期计算，请调用‘date_calc’函数。
        请以友好的语气回答问题。""",
    }
]

client = OpenAI(
    api_key=os.getenv('QWEN_API_KEY'),
    base_url='https://dashscope.aliyuncs.com/compatible-mode/v1'
)

def function_calling():
    start = time.time()
    completion = client.chat.completions.create(
        model='qwen-plus',
        extra_body={'enable_thinking': False},
        messages=messages,
        tools=tools,
        parallel_tool_calls=True,
    )
    cost = round(time.time() - start, 3)
    print(f"\n[LLM接口耗时] {cost} s")
    return completion

# ==============================
# 更新工具映射，加入新增的3个工具
# ==============================
function_mapper = {
    "get_current_weather": (get_current_weather, A2),
    "get_forecast_weather": (get_forecast_weather, A2),
    "get_current_time": (get_current_time, A1),
    "math_calc": (math_calc, A4),
    "file_read": (file_read, A5),
    "date_calc": (date_calc, A6),
}

def dispatch_tool(func_name, func_args):
    """通用工具分发器，自动匹配函数"""
    if func_name not in function_mapper:
        return f"❌ 不存在工具：{func_name}"
    tool_func,param_model = function_mapper[func_name]
    try:
        valid_params = param_model(**func_args)
        clean_args = valid_params.model_dump()
        # 适配sqrt运算：num2为None时不传入
        if func_name == "math_calc" and clean_args["op"] == "sqrt":
            clean_args.pop("num2", None)
        return tool_func(**clean_args)
    except ValidationError as e:
        print(f'参数校验失败：{e}')
        return f"参数校验失败：{str(e)}"

def safe_parse_json(text:str) -> dict|None:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    pattern_code = r'''(?:json)?\s*([\s\S]+?)'''
    match = re.search(pattern_code, text)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    patten_obj = r'\{[\s\S]+?\}'
    match = re.search(patten_obj, text)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return None

# 线程池专用：单个工具执行包装函数
def run_single_tool(tool_call):
    """接收单个tool_call，执行工具并返回id+结果"""
    func_name = tool_call.function.name
    func_args = json.loads(tool_call.function.arguments)
    print(f"[并行线程] 调用工具 [{func_name}]，参数：{func_args}")
    res = dispatch_tool(func_name, func_args)
    return {
        "tool_call_id": tool_call.id,
        "content": str(res)  # 统一转为字符串，避免返回dict导致后续报错
    }

def run_conversation(messages, tools):
    while True:
        # 1. 调用大模型
        message = function_calling()

        if message.choices[0].message.content is None:
            message.choices[0].message.content = ""
        messages.append(message.choices[0].message)

        if not message.choices[0].message.tool_calls:
            print(f"无需调用工具，直接回复: {message.choices[0].message.content}")
            break
        else:
            print(f"\n模型一次性下发 {len(message.choices[0].message.tool_calls)} 个工具任务，开启多线程并行执行...")
            tool_start = time.time()
            # 创建线程池，最大并发10个线程
            with ThreadPoolExecutor(max_workers=10) as pool:
                # map自动把每个tool_call分给不同线程同时执行
                all_tool_results = list(pool.map(run_single_tool, message.choices[0].message.tool_calls))
            tool_cost = round(time.time() - tool_start, 3)
            print(f"\n[全部工具并行执行总耗时] {tool_cost} s")
            for item in all_tool_results:
                print(f"\n[工具返回结果]\n{item['content']}")
                messages.append({
                    "role": "tool",
                    "tool_call_id": item["tool_call_id"],
                    "content": item["content"]
                })
        # 所有工具并行执行完成，统一请求大模型整合全部信息
        final_response = function_calling()
        final_ans = final_response.choices[0].message.content
        print("\n===== 助手最终整合回复 =====")
        print(final_ans)
        break

# 初始化对话
messages = []
while True:
    a = input('输入：')
    if a == 'q':
        break
    messages.append({
        'role': 'user',
        'content': a
    })
    run_conversation(messages, tools)