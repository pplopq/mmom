
import pymysql
import time

class BookManager:
    #连接数据库
    def __init__(self):
        try:
            self.conn = pymysql.connect(
                host="localhost",
                user="root",
                password="123456",
                database="library_db",
                charset="utf8mb4"
            )
            self.cursor = self.conn.cursor()
            print("数据库连接成功")
        except Exception as e:
            print("数据库连接失败：", e)

    # 日志写入文件
    def write_log(self, msg):
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        with open("library_log.txt", "a", encoding="utf-8") as f:
            f.write(f"[{now}] {msg}\n")

    # 管理员登录
    def login(self):
        print("\n========== 管理员登录 ==========")
        username = input("请输入账号: ")
        password = input("请输入密码: ")

        sql = "SELECT * FROM admin WHERE username=%s AND password=%s"
        self.cursor.execute(sql, (username, password))
        result = self.cursor.fetchone()

        if result:
            print(f"欢迎回来, {username} !")
            self.write_log(f"管理员 {username} 登录成功")
            return True
        else:
            print("账号或密码错误！")
            return False

    # 1. 添加图书
    def add_book(self, book_id, title, author, publisher):
        try:
            sql = "INSERT INTO book(book_id, title, author, publisher) VALUES(%s, %s, %s, %s)"
            self.cursor.execute(sql, (book_id, title, author, publisher))
            self.conn.commit()
            print("图书添加成功")
            self.write_log(f"添加图书：{book_id}《{title}》")
        except Exception as e:
            self.conn.rollback()
            print("添加失败，图书编号可能已存在")

    # 2. 查看所有图书
    def show_all_books(self):
        sql = "SELECT * FROM book"
        self.cursor.execute(sql)
        books = self.cursor.fetchall()
        if not books:
            print("暂无图书数据")
            return
        print(f"{'编号':<10} {'书名':<10} {'作者':<10} {'分类':<10} {'状态':<10}")
        for b in books:
            print(f"{b[0]:<10} {b[1]:<10} {b[2]:<10} {b[3]:<10} {b[4]:<10}")

    # 3. 按编号查询
    def search_book(self, keyword):
        sql = "SELECT * FROM book WHERE  book_id = %s"
        self.cursor.execute(sql, keyword)
        res = self.cursor.fetchall()
        if res:
            for r in res:
                print(f"编号：{r[0]} "
                      f"书名：{r[1]} "
                      f"作者：{r[2]} "
                      f"分类：{r[3]} "
                      f"状态：{r[4]} ")
        else:
            print("未找到相关图书")

    # 4. 修改图书信息
    def update_book(self, book_id, new_author, new_publisher):
        try:
            sql = "UPDATE book SET author=%s, publisher=%s WHERE book_id=%s"
            self.cursor.execute(sql, (new_author, new_publisher, book_id))
            self.conn.commit()
            if self.cursor.rowcount > 0:
                print("修改成功")
                self.write_log(f"修改图书信息：{book_id}")
            else:
                print("未找到该图书")
        except:
            self.conn.rollback()
            print("修改失败")

    # 5. 删除图书
    def delete_book(self, book_id):
        try:
            a=input(f"是否真的要删除{book_id}:")
            if a=='1':
                sql = "DELETE FROM book WHERE book_id=%s"
                self.cursor.execute(sql, book_id)
                self.conn.commit()
                if self.cursor.rowcount > 0:
                    print("删除成功")
                    self.write_log(f"删除图书：{book_id}")
                else:
                    print("未找到该图书")
            elif a=='0':
                print("不删除")
            else:
                print("只能输入0/1")
        except:
            self.conn.rollback()
            print("删除失败")

    #6. 借阅图书
    def borrow_book(self, book_id):
        try:
            # 先检查书是否存在且在馆
            sql_check = "SELECT * FROM book WHERE book_id=%s AND status='在馆'"
            self.cursor.execute(sql_check, book_id)
            book = self.cursor.fetchone()

            if not book:
                print("借阅失败！可能是图书不存在或已被借出。")
                return

            # 更新状态为借出
            sql_update = "UPDATE book SET status='借出' WHERE book_id=%s"
            self.cursor.execute(sql_update, book_id)
            self.conn.commit()
            print(f"{book[1]}借阅成功！")
            self.write_log(f"借阅图书：{book_id}")
        except:
            self.conn.rollback()
            print("借阅失败")

    # 7. 归还图书
    def return_book(self, book_id):
        try:
            # 先检查书是否存在且是借出状态
            sql_check = "SELECT * FROM book WHERE book_id=%s AND status='借出'"
            self.cursor.execute(sql_check, book_id)
            book = self.cursor.fetchone()

            if not book:
                print("归还失败！可能是图书不存在或状态异常。")
                return

            # 更新状态为在馆
            sql_update = "UPDATE book SET status='在馆' WHERE book_id=%s"
            self.cursor.execute(sql_update, book_id)
            self.conn.commit()
            print(f"{book[1]}归还成功！")
            self.write_log(f"归还图书：{book_id}")
        except:
            self.conn.rollback()
            print("归还失败")
    # 关闭数据库
    def close(self):
        self.cursor.close()
        self.conn.close()

def main():
    # 1. 实例化对象
    lm = BookManager()

    # 2. 登录验证 (循环直到登录成功)
    while not lm.login():
        choice = input("输入 'q' 退出系统，回车重试: ")
        if choice.lower() == 'q':
            print("系统已退出")
            return

    # 3. 主菜单循环
    while True:
        print("\n======= 图书借阅管理系统 =======")
        print("1. 添加图书")
        print("2. 查看所有图书")
        print("3. 查询图书 (编号)")
        print("4. 修改图书信息")
        print("5. 删除图书")
        print("6. 借阅图书")
        print("7. 归还图书")
        print("0. 退出系统")
        print("===============================")

        choice = input("请输入功能编号：")

        if choice == "1":
            bid = input("请输入图书编号：")
            title = input("请输入书名：")
            author = input("请输入作者：")
            publisher = input("请输入分类：")
            lm.add_book(bid, title, author, publisher)

        elif choice == "2":
            lm.show_all_books()

        elif choice == "3":
            keyword = input("请输入编号：")
            lm.search_book(keyword)

        elif choice == "4":
            bid = input("请输入要修改的图书编号：")
            author = input("请输入新作者：")
            publisher = input("请输入新分类：")
            lm.update_book(bid, author, publisher)

        elif choice == "5":
            bid = input("请输入要删除的图书编号：")
            lm.delete_book(bid)

        elif choice == "6":
            bid = input("请输入要借阅的图书编号：")
            lm.borrow_book(bid)

        elif choice == "7":
            bid = input("请输入要归还的图书编号：")
            lm.return_book(bid)

        elif choice == "0":
            lm.close()
            print("系统已退出，再见！")
            break

        else:
            print("输入无效，请输入 0-7 之间的数字")


# 程序入口
if __name__ == "__main__":
    main()