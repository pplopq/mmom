import os

import pandas as pd
from click import prompt
from fontTools.misc.eexec import encrypt

'''
#1
student_data = {
    '姓名':['小明','小红','小李','小兰'],
    '科目':['数学','语文','英语','物理'],
    '成绩':[95,88,92,98]
}

student_df = pd.DataFrame(student_data)
print(student_df)

#2
a=pd.read_csv(r"C:\py-study\new_3\student_scores.csv")
print(a)
print(a.head())  #前5行数据
print(a.shape)   #数据形状
print(a.info())  #每列非空数量和数据类型
print(a.describe())  #统计列信息

#3
a=pd.read_csv(r"C:\py-study\new_3\student_scores.csv")
print(a.loc[[0,1,2]]) #按标签选行
print(a.iloc[1])  #按位置选行
print(a.loc[2:4,['姓名','成绩']]) #同时选行和列（指定列）

#4
a=pd.read_csv(r"C:\py-study\new_3\student_scores.csv")
high_score = a[a['成绩']>=90]
print(high_score)  #选成绩大于等于90的信息

#new_3
a=pd.read_csv(r"C:\py-study\new_3\student_scores.csv")
print(a.isnull().sum()) #每列缺失值的数量
print(a.dropna())  #删除含缺失值后的数据
a.fillna({'成绩':a['成绩'].mean()}, inplace=True)   #用成绩列的均值填充空值
print(a)
print(a[a.duplicated(subset=['姓名','科目'],keep=False)])  #查看重复行
a1=a.drop_duplicates(subset=['姓名','科目'],keep='first')  #删除重复行，保留每一组的第一个（keep=‘first’）
print(a1)
print(a1.isnull().sum())  #最终检查

#6
a=pd.read_csv(r"C:\py-study\new_3\student_scores.csv")
subject_avg = a.groupby('科目')['成绩'].mean()  #各科平均分
print(subject_avg)
class_gender_avg = a.groupby(['班级','性别'])['成绩'].max()  #各班不同性别的最高成绩
print(class_gender_avg)
a['总分'] = a['成绩']+a['平时分']  #加一个总分列
print(a)
a['调整后成绩'] = a['成绩'].apply(lambda x:min(x+new_3,100))  成绩加5，最高到100
print(a)
a_score = a.sort_values(by='成绩',ascending=False)  #按成绩排序
print(a_score)

#7
import  fastapi
print(fastapi.__version__)

#8
from fastapi import  FastAPI
from pydantic import BaseModel
import pymysql
from pymysql.cursors import DictCursor
def get_db_connection():
    return pymysql.connect(host='localhost',
                           user ='root',
                           password='123456',
                           database='student_db',
                           cursorclass=DictCursor)
class Student(BaseModel):
    name: str
    age: int

app = FastAPI(
    title='学生管理系统',
    version='0.128.0',
)
#9
@app.get('/students')
def get_all_students():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('select * from students')
    students = cursor.fetchall()
    conn.close()
    return {"data":students}

#10
@app.get('/students/{stu_id}')
def get_one_student(stu_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('select * from students where id=%s', (stu_id,))
    student = cursor.fetchone()
    conn.close()
    if student:
        return student
    return {"error":"学生不存在"}

#11
@app.post('/students')
def add_student(stu: Student):
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = 'insert into students (name,age) values (%s,%s)'
    cursor.execute(sql, (stu.name, stu.age))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return {'msg':'添加成功','id':new_id}

#12
@app.put('/students/{stu_id}')
def update_student(stu_id: int, stu: Student):
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = 'update students set name=%s, age=%s where id=%s'
    cursor.execute(sql, (stu.name, stu.age, stu_id))
    conn.commit()
    return {'msg':'修改成功'}

#13
@app.delete('/students/{stu_id}')
def delete_student(stu_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('delete from students where id=%s', (stu_id,))
    conn.commit()
    conn.close()
    return {'msg':'删除成功'}
'''
#14
from openai import OpenAI
from datetime import datetime
import requests
import webbrowser
'''
client = OpenAI(
    api_key='123abcd',
    base_url='https://text.pollinations.ai/openai',
)

res = client.chat.completions.create(
    model='openai',
    messages=[{"role":"system","content":"你是一名计算机科学专业的大四学生"},
              {"role":"user","content":"你认为ai是什么"}]
)
print(res.choices[0].message.content)

stream = client.chat.completions.create(
    model='openai',
    messages=[{'role':'user','content':'写一段简短小故事'}],
    stream=True
)
for i in stream:
    if i.choices[0].delta.content:
        print(i.choices[0].delta.content,end='')

#15
client = OpenAI(
    api_key='sk-7f2b941e37d748eb9ea7146f47616713',
    base_url='https://dashscope.aliyuncs.com/compatible-mode/v1',
)
messages=[]
while True:
    user_input = input('请输入你的问题:')
    messages.append({'role': 'user', 'content': user_input})

    stream = client.chat.completions.create(
        model='qwen-plus',
        messages=messages,
        stream=True,
        max_tokens=200, #上限字数
        temperature=0.8,  #风格
    )
    ans = ''
    print('AI:',end='')
    for i in stream:
        if i.choices and i.choices[0].delta and i.choices[0].delta.content:
            txt = i.choices[0].delta.content
            ans = ans + txt
            print(txt,end='')
    print()
    messages.append({'role': 'assistant', 'content': ans})
    
client = OpenAI(
   api_key='111',
   base_url='http://127.0.0.1:1234/v1',
)
    
'''
'''
#16
client = OpenAI(
   api_key='sk-7f2b941e37d748eb9ea7146f47616713',
   base_url='https://dashscope.aliyuncs.com/compatible-mode/v1',
)

log_file = open("chat.log", "a", encoding="utf-8")
def log(text):
    t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_file.write(f"[{t}] {text}\n")
    log_file.flush()
log("对话开始")

system_prompt = input("你是一个:").strip() or 'ai助手'

messages = [{'role': 'system', 'content':f"你现在的人设是【{system_prompt}】。无论用户说什么，你都必须保持在这个角色里，绝对不能跳出角色。"}]

log(f"ai人设为{system_prompt}")

while True:
   user_input = input('请输入你的问题:').strip() or 'EXIT'
   if user_input == 'q' :
       log("用户:输入q")
       log("对话结束")
       log_file.close()
       print("再见")
       break

   elif user_input == 'EXIT':
       print("不能输入为空，请重新输入")
       log("用户:")
       log("输入为空，重新输入")
       continue

   elif user_input.lower() == 'c':
       messages = [{'role': 'system', 'content': system_prompt}]
       log("用户:输入c")
       log("清空上下文")
       print("清空上下文")
       continue

   elif '天气' in user_input:
       a = input("是否需要查询当前时间？(y/n): ").strip().lower()
       if a == 'y':
           city = input("城市：")
           try:
               url = f"https://wttr.in/{city}?format=3&lang=zh"
               r = requests.get(url, timeout=5)
               weather_info = r.text.strip()
               print(f"{weather_info}")
               log("用户：当前天气")
               log(f"系统：{weather_info}")
           except Exception as e:
               print(f"查询失败: {e}")
       else:
           print("已取消查询。")
           log("用户：取消了天气查询")
       continue


   elif '时间' in user_input:
       a = input("是否需要查询当前时间？(y/n): ").strip().lower()
       if a == 'y':
           now = datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")
           print(f"现在是：{now}")
           log("用户：确认查询当前时间")
           log(f"系统：{now}")
       else:
           print("已取消查询。")
           log("用户：取消了时间查询")
       continue

   elif '打开' in user_input:
       a = input("是否需要查询当前时间？(y/n): ").strip().lower()
       if a == 'y':
           if '百度' in user_input:
               url = "https://www.baidu.com"
           elif 'B站' in user_input or 'bilibili' in user_input:
               url = "https://www.bilibili.com"
           elif '谷歌' in user_input:
               url = "https://www.google.com"
           else:
               search_term = user_input.replace("打开", "").strip()
               url = f"https://www.baidu.com/s?wd={search_term}"
           print(f"正在为你打开: {url} ...")
           webbrowser.open(url)
           log(f"系统: 打开了 {url}")
       else:
           print("已取消打开。")
           log("用户：取消了打开网站")
       continue

   log(f"用户: {user_input}")
   messages.append({'role': 'user', 'content': user_input})

   stream = client.chat.completions.create(
       model='qwen-plus',
       messages=messages,
       stream=True,
       max_tokens=200, #上限字数
       temperature=0.8,  #风格
   )
   ans = ''
   print('AI:',end='')
   for i in stream:
       if i.choices and i.choices[0].delta and i.choices[0].delta.content:
           txt = i.choices[0].delta.content
           ans = ans + txt
           print(txt,end='')
   print()
   log(f"AI: {ans}")
   messages.append({'role': 'assistant', 'content': ans})


'''
#17
class LLM():
    PLATFORMS = {
        "qwen": {
            "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            "model": "qwen-plus"
        },
        "glm": {
            "base_url": "https://open.bigmodel.cn/api/paas/v4",
            "model": "glm-4-flash"
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
log_file = open("chat1.log", "a", encoding="utf-8")
def log(text):
    t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_file.write(f"[{t}] {text}\n")
    log_file.flush()

def n1(ai_instance):
    system_prompt = "你是一个智能助手，请简洁明了地回答问题。"
    messages = [{'role': 'system', 'content': system_prompt}]
    while True:
        user_input = input('请输入你的问题:').strip() or 'EXIT'
        if user_input == 'q':
            log("用户:输入q")
            log('再见')
            print("再见")
            break
        elif user_input == 'EXIT':
            print("不能输入为空，请重新输入")
            log("用户:")
            log("输入为空，重新输入")
            continue
        elif user_input.lower() == 'c':
            messages = [{'role': 'system', 'content':system_prompt}]
            log("用户:输入c")
            log("清空上下文")
            print("清空上下文")
            continue

        messages.append({'role': 'user', 'content': user_input})

        result = ai_instance.chat(messages)
        content = result['content']
        usage = result['usage']

        print(content)

        total = usage.prompt_tokens + usage.completion_tokens
        stats = f"Token用量: 输入={usage.prompt_tokens}, 输出={usage.completion_tokens}, 总计={total}"
        print(stats)
        log(stats)

        messages.append({'role': 'assistant', 'content': content})

        log(f"User: {user_input}")
        log(f"AI: {content}")

if __name__ == '__main__':
    log('对话开始:')
    while True:
        a=int(input("1.千问。2.智谱。请输入选项："))
        if a == 1:
            api=os.getenv('QWEN_API_KEY')
            ai = LLM("qwen", api_key=api)
            n1(ai)
        elif a == 2:
            api=os.getenv('GLM')
            ai = LLM("glm", api_key=api)
            n1(ai)
        else:
            print('对话结束，再见')
            log("对话结束")
            log_file.close()
            break
























