from fastapi import  FastAPI
from pydantic import BaseModel
import pymysql
from pymysql.cursors import DictCursor
from typing import List
def get_db_connection():
    return pymysql.connect(host='localhost',
                           user ='root',
                           password='123456',
                           database='school',
                           cursorclass=DictCursor)
class Student(BaseModel):
    name: str
    age: int
    gender: str
    major: str
app = FastAPI(
    title='学生管理系统',
    version='0.128.0',
)

@app.get('/students/count/{学生总数}')
def get_student_count():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) AS total FROM students')
    result = cursor.fetchone()
    conn.close()
    return {"total": result['total']}

@app.get('/students/avg_age/{平均年龄}')
def get_avg_age():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT AVG(age) AS avg_age FROM students')
    result = cursor.fetchone()
    conn.close()
    return {"avg_age": result['avg_age']}

@app.post('/students/batch/{批量插入}')
def batch_add_students(students: List[Student]):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = "INSERT INTO students (name, age, gender, major) VALUES (%s, %s, %s, %s)"
        data_to_insert = [
            (stu.name, stu.age, stu.gender, stu.major) for stu in students
        ]
        cursor.executemany(sql, data_to_insert)
        conn.commit()
        return {
            "message": f"成功插入 {len(data_to_insert)} 条学生数据",
            "count": len(data_to_insert)
        }
    except Exception as e:
        conn.rollback()
        return {"error": f"插入失败: {str(e)}"}
    finally:
        conn.close()

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
@app.get('/students/gender/{性别查询}')   #按
def get_students_by_gender(gender: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = 'select * from students where gender=%s'
    cursor.execute(sql, (gender,))
    # 使用 fetchall 获取所有匹配项
    students = cursor.fetchall()
    conn.close()
    if students:
        return {"data": students}
    return {"error": "该性别下没有学生"}

@app.get('/students/name/{名字模糊查询}')
def get_one_student(name: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    search_pattern = f"%{name.strip()}%"
    a = [search_pattern]
    sql = 'select * from students where name LIKE %s'
    cursor.execute(sql, a)
    student = cursor.fetchone()
    conn.close()
    if student:
        return {"data": student}
    return {"error": "没有该学生"}


