import json
import os
import time
from openai import OpenAI
from jsonschema import validate,ValidationError
import xml.etree.ElementTree as ET
import re

client = OpenAI(
    api_key=os.getenv('QWEN_API_KEY'),
    base_url='https://dashscope.aliyuncs.com/compatible-mode/v1'
)

def function_calling(messages):
    start = time.time()
    completion = client.chat.completions.create(
        model='qwen-plus',
        messages=messages,
        # response_format={'type': 'json_object'},
    )
    cost = round(time.time() - start, 3)
    print(f"\n[LLM接口耗时] {cost} s")
    return completion.choices[0].message.content


def safe_parse_json(text:str) -> dict | None:
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

def extract_with_schema(text:str,schema:dict,model:str = 'qwen-turbo') -> dict:
    schema_str = json.dumps(schema,ensure_ascii=False,indent=2)
    prompt = f"""请从以下文本中提取信息，严格按照 JSON Schema 输出，只输出 JSON 不加任何说明：

JSON Schema：
{schema_str}

待提取文本：
{text}

注意：
1. 只输出符合 Schema 的 JSON
2. required 字段必须存在
3. enum 字段只能使用给定的值"""
    messages = [{'role':'user', 'content':prompt}]
    b=function_calling(messages)
    return json.loads(b)

def validate_ai_output(data:dict,schema:dict) -> tuple[bool,str]:
    try:
        validate(instance= data,schema=schema)
        return True,'校验通过'
    except ValidationError as e:
        return False,f'校验失败:{e.message}'

def parse_ai_xml(xml_text: str) -> ET.Element | None:
    """安全解析 AI 返回的 XML"""
    # 清理 markdown 代码块
    xml_text = re.sub(r'```(?:xml)?\s*', '', xml_text)
    xml_text = xml_text.replace('```', '').strip()

    try:
        return ET.fromstring(xml_text)
    except ET.ParseError as e:
        print(f"XML 解析失败：{e}")
        return None

def review_to_dict(root: ET.Element) -> dict:
    """将 review XML 转为字典"""
    result = {
        "sentiment": root.findtext("sentiment", ""),
        "score": int(root.findtext("score", "0")),
        "pros": [item.text for item in root.findall("pros/item")],
        "cons": [item.text for item in root.findall("cons/item")],
        "summary": root.findtext("summary", "")
    }
    return result

'''
# order_schema = {
#     "type": "object",
#     "properties": {
#         "order_id": {
#             "type": "string",
#             "description": "订单编号，如 ORD-20240101-001"
#         },
#         "customer": {
#             "type": "string",
#             "description": "客户姓名"
#         },
#         "items": {
#             "type": "array",            # 数组类型
#             "description": "购买的商品列表",
#             "items": {                  # 数组每个元素的格式
#                 "type": "object",
#                 "properties": {
#                     "product": {"type": "string"},
#                     "quantity": {"type": "integer"},
#                     "price":    {"type": "number"}
#                 },
#                 "required": ["product", "quantity", "price"]
#             }
#         },
#         "total":  {"type": "number",  "description": "订单总金额"},
#         "status": {
#             "type": "string",
#             "enum": ["待支付", "已支付", "已发货", "已完成", "已取消"],  # 枚举限制
#             "description": "订单状态"
#         },
#         "priority": {
#             "type": "boolean",
#             "description": "是否加急订单"
#         }
#     },
#     "required": ["order_id", "customer", "items", "total", "status"]
# }

# a=input('输入地址：')
# with open(a, "r", encoding="utf-8") as f:
#     content = f.read()
order_schema={
    "type": "object",
    "properties": {
        "sentiment": {
            "type": "string",
            "enum": ["正面", "负面", "中性"],
            "description": "评论情感倾向"
        },
        "score": {
            "type": "integer",
            "minimum": 1,
            "maximum": 5,
            "description": "用户评分，范围1-5分"
        },
        "keywords": {
            "type": "array",
            "description": "评论提取的关键词列表",
            "items": {
                "type": "string"
            }
        },
        "need_manual_process": {
            "type": "boolean",
            "description": "是否需要人工二次处理"
        }
    },
    "required": ["sentiment", "score", "keywords", "need_manual_process"]
}

text = '这个手机屏幕很清晰，就是电池差'
result = extract_with_schema(text,order_schema)
is_valid,msg = validate_ai_output(result,schema=order_schema)
if is_valid:
    print('提取成功')
    print(f'评分:{result['score']}')
    print(f'关键词:{result['keywords']}')
    print(f'情感倾向:{result["sentiment"]}')
    print(f'是否需要人工处理:{result["need_manual_process"]}')
else:
    print(f"数据不合规：{msg}")

# print(json.dumps(result,ensure_ascii=False,indent=2))
'''
# xml_prompt = """
# 请分析这段产品评论，以 XML 格式输出，只输出 XML 不要有其他文字：
#
# 评论：这款手机屏幕很清晰，拍照效果也不错，就是电池续航差了点，价格偏贵。
#
# 要求输出格式：
# <review>
#   <sentiment>正面/负面/中性/混合</sentiment>
#   <score>1-5</score>
#   <pros>
#     <item>优点1</item>
#     <item>优点2</item>
#   </pros>
#   <cons>
#     <item>缺点1</item>
#     <item>缺点2</item>
#   </cons>
#   <summary>一句话总结</summary>
# </review>
# """
# structured_prompt = """
# <task>
#   <role>你是一位专业的代码审查工程师</role>
#   <input>
#     <code language="python">
#       def add(a, b):
#           return a - b   # 这里有 bug
#     </code>
#   </input>
#   <requirements>
#     <item>找出代码中的 bug</item>
#     <item>给出修复建议</item>
#     <item>评估代码质量（1-10分）</item>
#   </requirements>
#   <output_format>
#     以 JSON 格式返回：{"bug": "...", "fix": "...", "score": 数字}
#   </output_format>
# </task>
# """
new_prompt = """
<task>
  <role>你是一位专业的英语新闻分析专家</role>
  <input>
    </code>
        Here’s a tighter version:
         A student-led recycling drive, organized by Li Hua, 
         launched in local neighborhoods on June 12, 2026.
         The campaign encourages residents to sort waste with easy-to-use bins and quick tips. 
         Li hopes the effort will grow citywide this fall.
    </code>
  </input>
  <requirements>
    <item>给出新闻的标题</item>
    <item>给出新闻的作者</item>
    <item>新闻的时间</item>
    <item>新闻内容的摘要</item>
    <item>新闻关键词列表</item>
  </requirements>
  <output_format>
    以 JSON 格式返回：{"标题": "...", "作者": "...", "时间": "...", "摘要":"...", "关键词": 列表}
  </output_format>
</task>
"""

messages=[{"role": "user", "content": new_prompt}]
a=function_calling(messages)
print(a)

# if b is not None:
#     data = review_to_dict(b)
#     print(f'情感：{data['sentiment']},评分:{data['score']}/5')
#     print(f'优点:{','.join(data["pros"])})')
#     print(f'缺点:{','.join(data["cons"])}')
