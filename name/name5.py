import os
import re
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import jieba.analyse
from openai import OpenAI

API_KEY = os.getenv("QWEN_API_KEY")
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
MODEL_NAME = "qwen-plus"

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

def clean_text(raw_text):
    text = re.sub(r'<[^>]+>', '', raw_text)
    text = re.sub(r'\n\s*\n', '\n', text).strip()
    return text

def extract_keywords(text, top_k=10):
    keywords = jieba.analyse.extract_tags(text, topK=top_k, withWeight=False)
    return ", ".join(keywords)


def generate_summary(text, style="standard"):
    prompts = {
        "short": "请用【一句话】高度概括这篇文章的核心观点，字数控制在50字以内。",
        "standard": "请生成一段【标准摘要】（3-5句话），保留文章的关键论据和逻辑，不要遗漏重要信息。",
        "detailed": "请以【Q&A问答形式】提炼文章的3个核心问题并给出简要回答，帮助读者快速抓住重点。"
    }
    prompt = prompts.get(style, prompts["standard"])
    messages = [
        {"role": "system", "content": "你是一个专业的文章摘要助手，擅长提炼长文核心内容。"},
        {"role": "user", "content": f"文章内容如下：\n\n{text}\n\n要求：{prompt}"}
    ]
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[生成失败]: {str(e)}"

def process_article():
    source_type = input("请选择输入方式 (1.直接粘贴文本  2.读取TXT文件): ").strip()
    if source_type == "2":
        file_path = input("请输入文件路径: ").strip()
        with open(file_path, "r", encoding="utf-8") as f:
            raw_content = f.read()
    else:
        print("请粘贴文章内容（输入完成后按回车，再输入 END 结束）：")
        lines = []
        while True:
            line = input()
            if line.strip().upper() == "END":
                break
            lines.append(line)
        raw_content = "\n".join(lines)

    if not raw_content:
        print("内容为空，程序退出。")
        return

    clean_content = clean_text(raw_content)
    keywords = extract_keywords(clean_content)

    summary_short = generate_summary(clean_content, style="short")
    summary_standard = generate_summary(clean_content, style="standard")
    summary_detailed = generate_summary(clean_content, style="detailed")
    c=''
    output_md =(f"关键词：{keywords}"
                f"---{c}---"
                f"简短版：{summary_short}"
                f"---{c}---"
                f"标准版：{summary_standard}"
                f"----{c}----"
                f"详细版：{summary_detailed}"
                )
    with open("summary1.md", "w", encoding="utf-8") as f:
        f.write(output_md)
    print("\n摘要已保存至 summary1.md")

    wc=WordCloud(font_path="simhei.ttf", width=800, height=400, background_color="white")
    wc.generate(output_md)
    plt.figure(figsize=(10, 5))
    plt.imshow(wc, interpolation='bilinear')
    plt.axis("off")
    plt.show()

if __name__ == "__main__":
    process_article()