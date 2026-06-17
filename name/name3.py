import os

import requests
from openai import OpenAI

def get_city_code(name: str, api_key: str):
    url = "https://restapi.amap.com/v3/geocode/geo"
    params = {
        "address": name,
        "key": api_key
    }
    response = requests.get(url, params=params).json()
    if response["status"] == "1" and response["geocodes"]:
        return response["geocodes"][0]["adcode"]
    raise ValueError(f"未找到城市 {name} 的 adcode")

def get_weather(city_code: str, api_key: str):
    url = "https://restapi.amap.com/v3/weather/weatherInfo"
    params = {
        "city": city_code,
        "key": api_key
    }
    response = requests.get(url, params=params).json()
    if response["status"] == "1":
        live = response["lives"][0]
        return {
            "temperature": live["temperature"],
            "humidity": live["humidity"],
            "wind_direction": live["winddirection"],
            "wind_power": live["windpower"],
            "weather": live["weather"]
        }
    raise Exception("天气数据获取失败")

class LLM():
    PLATFORMS = {
        "qwen": {
            "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            "model": "qwen-plus"
        }
    }
    def __init__(self, platform: str, api_key: str):
        config = self.PLATFORMS[platform]
        self.client = OpenAI(api_key=api_key, base_url=config['base_url'])
        self.model = config['model']

    def chat(self, messages: list):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=200,
            temperature=0.8,
        )
        return {
            'content': response.choices[0].message.content,
            'usage': response.usage
        }

def main():
    # 配置参数
    amap_key = "7c5ee1fd7a3fae4109edc23152a0c429"
    dashscope_key = os.getenv("QWEN_API_KEY")
    name = input("请输入城市名：").strip()

    code = get_city_code(name,amap_key)
    print(f"城市 {name} 的 adcode：{code}")
    weather_data = get_weather(code,amap_key)
    print("天气数据：", weather_data)

    prompt = (
        f"今天{name}的天气是{weather_data['weather']}，"
        f"气温{weather_data['temperature']}℃，"
        f"湿度{weather_data['humidity']}%，"
        f"风向{weather_data['wind_direction']}，风力{weather_data['wind_power']}级。"
        f"请根据以上天气情况，给出穿衣建议和出行注意事项。"
    )
    print("Prompt：", prompt)

    assistant = LLM(platform="qwen", api_key=dashscope_key)
    result = assistant.chat([{"role": "user", "content": prompt}])
    print(result['content'])

if __name__ == "__main__":
    main()

