import json
import requests
from datetime import datetime
from openai import OpenAI
import os

# 请将此处的字符串替换为您自己的高德地图API密钥
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

    except Exception as e:
        return f"查询天气预报时发生错误：{e}"

# 查询当前时间的工具保持不变
def get_current_time():
    current_datetime = datetime.now()
    formatted_time = current_datetime.strftime('%Y-%m-%d %H:%M:%S')
    return f"当前时间：{formatted_time}。"


import re


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


# 工具定义：增加了 get_forecast_weather
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "当你想知道现在的时间时非常有用。",
            "parameters": {}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "当你想查询指定城市的实时天气时非常有用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "城市或县区，比如北京市、杭州市、余杭区等。",
                    }
                },
                "required": ["location"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_forecast_weather",
            "description": "当你想查询指定城市未来几天的天气预报时非常有用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "城市或县区，比如北京市、杭州市、余杭区等。",
                    }
                },
                "required": ["location"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "translate_text",
            "description": "将文本翻译成指定语言。支持模糊输入（如'英语'、'en'、'English'）。",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "需要翻译的原始文本"},
                    "target_language": {"type": "string", "description": "目标语言，如：英语、日语、法语、en、ja"},
                    "source_language": {"type": "string", "description": "源语言（可选），默认为自动检测(auto)"}
                },
                "required": ["text", "target_language"]
            }
        }
    }
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
    completion = client.chat.completions.create(
        model='qwen-plus',
        extra_body={'enable_thinking': False},
        messages=messages,
        tools=tools,
        parallel_tool_calls=True,
    )
    return completion.choices[0].message

function_mapper = {
    "get_current_weather": get_current_weather,
    "get_forecast_weather": get_forecast_weather,
    "get_current_time": get_current_time,
    "translate_text": translate_text
}

def run_conversation(messages, tools):
    while True:
        # 1. 调用大模型
        message = function_calling()
        tool_calls = message.tool_calls

        # 2. 判断是否需要调用工具
        if not tool_calls:
            print(f"最终回答: {message.content}")
            break

        # 3. 将模型的意图添加到历史
        messages.append(message)

        # --- 核心修改：处理多个工具调用 ---
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            print(f"正在调用工具: {function_name}...")

            # 执行对应的本地函数
            if function_name in function_mapper:
                try:
                    function_response = function_mapper[function_name](function_args)
                except Exception as e:
                    function_response = f"Error: {str(e)}"
            else:
                function_response = f"Error: Unknown function {function_name}"

            # 将每个工具的返回结果封装成 tool message
            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": str(function_response)
            })
        # ----------------------------------

        # 4. 带着所有工具的结果再次请求模型，让它生成最终回复
        # 循环回到第1步

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
