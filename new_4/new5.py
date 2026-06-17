from pydantic import BaseModel,Field,ValidationError
import json
import requests
from datetime import datetime
from openai import OpenAI
import os
import time
from concurrent.futures import ThreadPoolExecutor

AMAP_API_KEY = "7c5ee1fd7a3fae4109edc23152a0c429"

def get_current_weather(arguments):
    """
    调用高德地图API获取指定城市的实时天气信息。
    """
    location = arguments["location"]

    # 第一步：通过地理编码API获取城市的adcode
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

        # 第二步：通过天气API获取实时天气 (extensions=base)
        weather_url = "https://restapi.amap.com/v3/weather/weatherInfo"
        weather_params = {
            "city": city_code,
            "key": AMAP_API_KEY,
            "extensions": "base"  # 获取实况天气
        }

        weather_response = requests.get(weather_url, params=weather_params).json()
        if weather_response["status"] != "1":
            return f"抱歉，获取 {location} 的天气信息失败。"

        live = weather_response["lives"][0]

        # 格式化返回结果
        weather_info = (
            f"{location} 现在是 {live['weather']}，"
            f"气温 {live['temperature']}°C，"
            f"湿度 {live['humidity']}%，"
            f"风向 {live['winddirection']}，风力 {live['windpower']} 级。"
        )
        return weather_info

    except Exception as e:
        return f"查询天气时发生错误：{e}"

def get_forecast_weather(arguments):
    """
    调用高德地图API获取指定城市的未来天气预报。
    """
    location = arguments["location"]
    try:
        params = A2(location=location)
        # 第一步：通过地理编码API获取城市的adcode
        geo_url = "https://restapi.amap.com/v3/geocode/geo"
        geo_params = {
            "address": location,
            "key": AMAP_API_KEY
        }

        geo_response = requests.get(geo_url, params=geo_params).json()
        if geo_response["status"] != "1" or not geo_response["geocodes"]:
            return f"抱歉，未能找到城市 {location} 的相关信息。"

        city_code = geo_response["geocodes"][0]["adcode"]

        # 第二步：通过天气API获取预报天气 (extensions=all)
        weather_url = "https://restapi.amap.com/v3/weather/weatherInfo"
        weather_params = {
            "city": city_code,
            "key": AMAP_API_KEY,
            "extensions": "all"  # 获取预报天气
        }

        weather_response = requests.get(weather_url, params=weather_params).json()
        if weather_response["status"] != "1":
            return f"抱歉，获取 {location} 的天气预报失败。"

        # 获取所有预报数据
        all_forecasts = weather_response["forecasts"][0]["casts"]

        # --- 核心修改点 ---
        # 高德返回的数据包含 [今天, 明天, 后天, 大后天]
        # 使用 [1:] 切片来跳过今天，只获取未来三天的数据
        future_forecasts = all_forecasts[1:]
        # ------------------

        # 格式化返回结果，展示未来三天的预报
        forecast_info = f"{location} 未来3天的天气预报：\n"
        for day in future_forecasts:
            forecast_info += (
                f"- {day['date']} ({day['week']})：{day['dayweather']}，"
                f"气温 {day['daytemp']}°C ~ {day['nighttemp']}°C\n"
            )
        return forecast_info
    except ValidationError as e:
        print(f'参数自动拦截{e}')
    except Exception as e:
        return f"查询天气预报时发生错误：{e}"

# 查询当前时间
def get_current_time(arguments=None):
    current_datetime = datetime.now()
    formatted_time = current_datetime.strftime('%Y-%m-%d %H:%M:%S')
    return f"当前时间：{formatted_time}。"


def translate_text(arguments):
    text = arguments.get("text", "").strip()
    target_lang = arguments.get("target_language", "").strip()
    source_lang = arguments.get("source_language", "auto").strip()
    if not text:
        return "翻译失败：未提供需要翻译的文本。"
    if not target_lang:
        return "翻译失败：未指定目标语言。"
    # 1. 构建语言映射表
    lang_map = {
        "英语": "en", "日文": "ja", "韩语": "ko",
        "法语": "fr", "德语": "de", "西班牙语": "es",
        "俄语": "ru", "泰语": "th", "越南语": "vi"
    }
    # 模糊匹配目标语言
    target_code = lang_map.get(target_lang.lower(), target_lang)
    source_code = lang_map.get(source_lang.lower(), source_lang)
    url = "https://api.mymemory.translated.net/get"
    params = {
        "q": text,
        "langpair": f"{source_code}|{target_code}"
    }
    response = requests.get(url, params=params, timeout=10).json()
    if response.get("responseStatus") == 200:
        translated_text = response["responseData"]["translatedText"]
        # 简单的质量校验（防止API返回原文或空值）
        if translated_text.lower() == text.lower() or not translated_text.strip():
            return f"翻译结果可能与原文相同或为空，请检查源语言和目标语言是否正确。\n原文：{text}"
        return f"翻译结果 ({target_lang})：\n{translated_text}"
    else:
        error_msg = response.get("responseDetails", "未知错误")
        return f"翻译服务返回错误：{error_msg}"


class A1(BaseModel):
    """对应 get_current_time，无参数"""
    pass

class A2(BaseModel):
    """对应 get_current_weather / get_forecast_weather"""
    location: str = Field(..., description="城市或县区，比如北京市、杭州市、余杭区等。")

class A3(BaseModel):
    """对应 translate_text"""
    text: str = Field(..., description="需要翻译的原始文本")
    language1: str = Field(..., description="目标语言，如：英语、日语、法语、en、ja")
    language2: str = Field(default="auto", description="源语言（可选），默认为自动检测(auto)")

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

# --- 4. 注册工具 ---
tools = [
    pydantic_to_tool_definition(A1, 'get_current_time', '查询系统时间'),
    pydantic_to_tool_definition(A2, 'get_current_weather', '查询指定城市的实时天气'),
    pydantic_to_tool_definition(A2, 'get_forecast_weather', '查询指定城市未来几天的天气预报。'),
    pydantic_to_tool_definition(A3, 'translate_text', "将文本翻译成指定语言。支持模糊输入（如'英语'、'en'、'English'）。")
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
        - 如果用户要求翻译文本，请调用‘translate_text’函数。
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

function_mapper = {
    "get_current_weather": (get_current_weather, A2),
    "get_forecast_weather": (get_forecast_weather, A2),
    "translate_text": (translate_text, A3),
    "get_current_time": (get_current_time, A1),
}

def dispatch_tool(func_name, func_args):
    """通用工具分发器，自动匹配函数"""
    if func_name not in function_mapper:
        return f"❌ 不存在工具：{func_name}"
    tool_func,param_model = function_mapper[func_name]
    try:
        valid_params = param_model(**func_args)
        clean_args = valid_params.model_dump()
        return tool_func(clean_args)
    except ValidationError as e:
        print(f'参数校验失败：{e}')


# 线程池专用：单个工具执行包装函数
def run_single_tool(tool_call):
    """接收单个tool_call，执行工具并返回id+结果"""
    func_name = tool_call.function.name
    func_args = json.loads(tool_call.function.arguments)
    print(f"[并行线程] 调用工具 [{func_name}]，参数：{func_args}")
    res = dispatch_tool(func_name, func_args)
    return {
        "tool_call_id": tool_call.id,
        "content": res
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

