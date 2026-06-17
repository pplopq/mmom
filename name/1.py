import json
import os
import random
import pymysql
from openai import OpenAI

API_KEY = os.getenv("QWEN_API_KEY")
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
MODEL_NAME = "qwen-plus"

# 数据库配置
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "123456",
    "database": "study",
    "charset": "utf8mb4"
}

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)


def load_words(filename="word.json"):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_ai(word_en):
    prompt = f"请帮我生成一个包含单词{word_en}的简短英文例句（附带中文翻译）和该单词的联想记忆技巧。请直接返回结果，不要多余的废话。"
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def save_record(word_en,word_cn, is_correct):
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    sql = "SELECT COUNT(*) FROM words WHERE en = %s"
    cursor.execute(sql, word_en)
    count = cursor.fetchone()[0]
    if count > 0:
        update_sql = "UPDATE words SET is_correct = %s WHERE en = %s"
        cursor.execute(update_sql, (is_correct, word_en))
    else:
        insert_sql = "INSERT INTO words (en,cn,is_correct) VALUES (%s, %s ,%s)"
        cursor.execute(insert_sql, (word_en, word_cn, is_correct))
    conn.commit()

def ok():
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    wrong_list = []
    sql = "SELECT COUNT(*) FROM words WHERE is_correct = %s"
    cursor.execute(sql, 0)
    results = cursor.fetchall()
    if results:
        for row in results:
            wrong_list.append({"en": row[0], "cn": row[1]})
    else:
        print('没有错题')
    return wrong_list


def main():
    while True:
        a=int(input())
        if a == 1:
            all_words = load_words()
            words = all_words.copy()
            while words:
                current_word = random.choice(words)
                cn = current_word['cn']
                en = current_word['en']

                print(f"请写出对应的英文单词：【{cn}】")
                user_input = input("你的回答:").strip().lower()

                if user_input == 'q':
                    break
                if user_input == en.lower():
                    print("回答正确！+10分")
                    words.remove(current_word)
                    save_record(en, cn, True)

                else:
                    print(f"回答错误！正确答案是：{en}")
                    save_record(en, cn, False)
                    print(get_ai(en))
            if not words:
                print("学习结束")
            continue
        elif a == 2:
            list = ok()
            while list:
                current_word = random.choice(list)
                cn = current_word['cn']
                en = current_word['en']
                print(f"请写出对应的英文单词：【{cn}】")
                user_input = input("你的回答:").strip().lower()

                if user_input == 'q':
                    break
                if user_input == en.lower():
                    print("回答正确！+10分")
                    list.remove(current_word)
                    save_record(en, cn, True)

                else:
                    print(f"回答错误！正确答案是：{en}")
                    save_record(en, cn, False)
                    print(get_ai(en))
            continue
        elif a == 3:
            break
        else:
            print('没用该选项')
            continue



if __name__ == "__main__":
    main()











