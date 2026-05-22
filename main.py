import pymysql

conn = pymysql.connect(
    host='localhost',
    user='root',
    password='123456',
    db='school',
    charset='utf8mb4',
)
class bookManager:
    def __init__(self):
        try:
            self.conn = pymysql.connect(
                host="localhost",
                user="root",  # 改为自己的MySQL账号
                password="123456",  # 改为自己的MySQL密码
                database="school",
                charset="utf8mb4",
                autocommit=False
            )
            self.cursor = self.conn.cursor(pymysql.cursors.DictCursor)
            print("数据库连接成功")
        except Exception as e:
            print("数据库连接失败：", e)
    def add_book(self,book_id, book_name, author,category,status):
        sql = "INSERT INTO book (book_id, book_name, author,category,status) VALUES (%s,%s,%s, %s, %s)"
        self.cursor.execute(sql, (book_id, book_name, author,category,status))
        self.conn.commit()
        print("添加成功")
    def get_book(self):
        sql = "SELECT * FROM book"
        result = self.cursor.execute(sql)
        return result[0] if result else None
    def get_book_id(self,book_id):
        sql = "SELECT * FROM book where book_id = %s"
        result = self.cursor.execute(sql, (book_id,))
        return result[0] if result else None
    def update_book(self, book_name,author,category,book_id):
        sql = "UPDATE book SET  book_name = %s and author = %s and category = %s WHERE book_id = %s"
        self.cursor.execute(sql, (book_name,author,category,book_id))
        print("已更新")
    def delete_book(self, book_id):
        sql = "DELETE FROM book WHERE book_id = %s"
        self.cursor.execute(sql, book_id)
        print("已删除")
    def close(self):
        self.cursor.close()
        self.conn.close()
        print("✅ 数据库连接已关闭")

def main():
    sm = bookManager()
    cursor = conn.cursor()
    while True:
        print("1. 添加")
        print("2. 查看所有完整信息")
        print("3. 按学号查询学生成绩")
        print("4. 修改学生基础信息")
        print("5. 删除学生（含成绩）")
        print("0. 退出系统")
        choice = input("请输入功能编号：")

        if choice == "1":
            book_id = '01'
            book_name = 'm1'
            author = 'm2'
            category = 'm3'
            status = 'jiey'

            sm.add_book(book_id, book_name, author,category,status)

        elif choice == "2":
            sm.get_book()

        elif choice == "3":
            sid = input("请输入查询id：")
            sm.get_book_id(sid)

        elif choice == "4":
            book_id = '01'
            book_name = input("请输入：")
            author = input("请输入：")
            category = input("请输入：")
            sm.update_book(book_name,author,category,book_id)

        elif choice == "5":

            sid = input("请输入要删除的学号：")
            sm.delete_book(sid)

        elif choice == "0":
            sm.close()
            print("👋 系统退出成功，再见！")
            break

        else:
            print("❌ 输入无效，请输入0-6的数字！")

if __name__ == "__main__":
    main()