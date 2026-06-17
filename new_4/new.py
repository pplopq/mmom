import json
import random
from datetime import datetime
'''
# 模拟天气查询工具。返回结果示例：“北京今天是雨天。”
def get_current_weather(arguments):
    # 定义备选的天气条件列表
    weather_conditions = ["晴天", "多云", "雨天"]
    # 随机选择一个天气条件
    random_weather = random.choice(weather_conditions)
    # 从 JSON 中提取位置信息
    location = arguments["location"]
    # 返回格式化的天气信息
    return f"{location}今天是{random_weather}。"


# 查询当前时间的工具。返回结果示例：“当前时间：2024-04-15 17:15:18。“
def get_current_time():
    # 获取当前日期和时间
    current_datetime = datetime.now()
    # 格式化当前日期和时间
    formatted_time = current_datetime.strftime('%Y-%m-%d %H:%M:%S')
    # 返回格式化后的当前时间
    return f"当前时间：{formatted_time}。"

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
            "description": "当你想查询指定城市的天气时非常有用。",
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
    }
]
tool_name = [tool["function"]["name"] for tool in tools]
print(f"创建了{len(tools)}个工具，为：{tool_name}\n")


messages = [
    {
        "role": "system",
        "content": """你是一个很有帮助的助手。如果用户提问关于天气的问题，请调用 ‘get_current_weather’ 函数;
     如果用户提问关于时间的问题，请调用‘get_current_time’函数。
     请以友好的语气回答问题。""",
    }
]

from openai import OpenAI
import os

client = OpenAI(
    api_key=os.getenv('QWEN_API_KEY'),
    base_url = 'https://dashscope.aliyuncs.com/compatible-mode/v1'
)

def function_calling():
    completion =client.chat.completions.create(
        model = 'qwen-plus',
        extra_body={'enable_thinking': False},
        messages = messages,
        tools=tools
    )
    print(completion.choices[0].message.model_dump_json())
    return completion

while True:
    a = input('输入：')
    if a =='q':
        break
    messages.append({'role': 'user', 'content': a})
    completion = function_calling()
    # 从返回的结果中获取函数名称和入参
    function_name = completion.choices[0].message.tool_calls[0].function.name
    arguments_string = completion.choices[0].message.tool_calls[0].function.arguments

    # 创建一个函数映射表
    function_mapper = {
        "get_current_weather": get_current_weather,
        "get_current_time": get_current_time
    }

    # 使用json模块解析参数字符串
    arguments = json.loads(arguments_string)

    # 获取函数实体
    function = function_mapper[function_name]
    # 如果入参为空，则直接调用函数。否则，传入参数后调用函数
    if arguments == {}:
        function_output = function()
    else:
        function_output = function(arguments)
    #输出
    print(function_output)

    messages.append(completion.choices[0].message)
    print("已添加assistant message")
    messages.append(
        {"role": "tool", "content": function_output, "tool_call_id": completion.choices[0].message.tool_calls[0].id})
    print("已添加tool message\n")

    completion = function_calling()



from openai import OpenAI
import os

client = OpenAI(
    api_key=os.getenv('QWEN_API_KEY'),
    base_url='https://dashscope.aliyuncs.com/compatible-mode/v1'
)
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "当你想查询指定城市的天气时非常有用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "城市或县区，比如北京市、杭州市、余杭区等。",
                    }
                },
                "required": ["location"],
            },
        },
    },
]

stream = client.chat.completions.create(
    model="qwen3.6-plus",
    extra_body={"enable_thinking": False},
    messages=[{"role": "user", "content": "杭州天气?"}],
    tools=tools,
    stream=True
)

for chunk in stream:
    delta = chunk.choices[0].delta
    print(delta.tool_calls)


tool_calls = {}
for response_chunk in stream:
    delta_tool_calls = response_chunk.choices[0].delta.tool_calls
    if delta_tool_calls:
        for tool_call_chunk in delta_tool_calls:
            call_index = tool_call_chunk.index
            tool_call_chunk.function.arguments = tool_call_chunk.function.arguments or ""
            if call_index not in tool_calls:
                tool_calls[call_index] = tool_call_chunk
            else:
                tool_calls[call_index].function.arguments += tool_call_chunk.function.arguments
print(tool_calls[0].model_dump_json())

'''







