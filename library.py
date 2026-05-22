import pymysql
import time
import datetime

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


    def add_user(self):
        print("=== 用户注册 ===")
        username = input("请输入新账号名: ").strip()
        password = input("请输入新密码: ").strip()

        if not username or not password:
            print("❌ 账号或密码不能为空！")
            return
        sql = "insert into admin (username, password) VALUES (%s, %s)"
        try:
            self.cursor.execute(sql, (username, password))
            self.conn.commit()
            print(f"用户{username}注册成功")

            self.write_log(f"新用户注册成功: {username}")

        except Exception as e:
            self.conn.rollback()
            print("注册失败：账号可能已存在。",e)

    # 管理员登录
    def login(self):
        print("\n========== 管理员登录/学生登入 ==========")
        username = input("请输入账号: ")
        password = input("请输入密码: ")

        sql = "SELECT username, role FROM admin WHERE username=%s AND password=%s"
        self.cursor.execute(sql, (username, password))
        result = self.cursor.fetchone()
        if result:
            self.current_user = result[0]
            self.current_role = result[1]
            print(f"欢迎回来，{self.current_user} ! (身份: {self.current_role})")
            self.write_log(f"用户 {self.current_user} 登录成功")
            return True
        else:
            print("账号或密码错误！")
            return False


    def add_admin(self):
        print("1.新增账号")
        print("2.删除账号")
        choice = input("选择操作1/2:")
        if choice == '1':
            new_user = input("输入新账号名: ")
            new_pwd = input("输入新密码: ")
            print("选择角色: 1.普通管理员 2.学生")
            r = input("请输入角色编号: ")
            if r == '1':
                role = 'admin'
            else:
                role = 'student'
            sql = "insert into admin (username, password, role) VALUES(%s, %s, %s)"
            try:
                self.cursor.execute(sql, (new_user, new_pwd, role))
                self.conn.commit()
                print("账号添加成功")
            except Exception as e:
                print("添加失败 (可能是账号已存在):", e)
        elif choice == '2':
            del_user = input("输入要删除的账号名: ")
            if del_user == self.current_user:
                print("不能删除自己")
                return
            sql = "delete from admin where username=%s"
            confirm = input(f"确定要删除 {del_user}吗 y/n: ")
            if confirm.lower() == 'y':
                self.cursor.execute(sql, del_user)
                if self.cursor.rowcount > 0:
                    self.conn.commit()
                    print("删除成功")
                else:
                    print("账号不存在")

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

    # 2. 查询图书
    def search_book(self):
        while True:
            print("请选择查询方式 ")
            print("1. 按书名模糊查询")
            print("2. 按分类筛选")
            print("3. 按作者筛选图书")
            print("4. 显示所有图书")
            print("0. 返回")
            sql = "select * from book where 1=1"
            a=[]
            choice = input("输入选项0/1/2/3/4：")
            if choice == '1':
                b1=input("请输入关键词：").strip()
                if b1:
                    sql +=" and title like %s"
                    a.append(f"%{b1}%")
                else:
                    print("关键词不能为空")
                    continue
            elif choice == '2':
                b2=input("请输入分类:").strip()
                if b2:
                    sql +=" and publisher like %s"
                    a.append(b2)
                else:
                    print("分类不能为空")
                    continue
            elif choice =='3':
                b3=input("请输入作者名:").strip()
                if b3:
                    sql +=" and author like %s"
                    a.append(b3)
                else:
                    print("作者不能为空")
                    continue
            elif choice =='4':
                pass
            elif choice == '0':
                return
            else:
                print("输入错误，请重新输入")
                continue
            try:
                self.cursor.execute(sql,a)
                results = self.cursor.fetchall()
                if results:
                    print(f" 查询结果:共 {len(results)}本书")
                    print(f"{'编号':<10} {'书名':<10} {'作者':<10} {'分类':<10} {'状态':<10}")
                    for row in results:
                        print(f"{row[0]:<10} {row[1]:<10} {row[2]:<10} {row[3]:<10} {row[4]:<10}")
                else:
                    print("未找到相关图书")

            except Exception as e:
                print(f"查询出错:{e}")

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
            a=input(f"是否真的要删除{book_id} 0.不删除/1.删除:")
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
            # 1. 检查是否已借满 3 本
            sql_count = "select count(*) from borrower where username=%s and status='借阅中'"
            self.cursor.execute(sql_count, self.current_user)
            count = self.cursor.fetchone()[0]
            if count >= 3:
                print("失败：每人最多只能借 3 本书！")
                return

            # 2. 检查书是否在馆
            sql_check = "select * from book where book_id=%s and status='在馆'"
            self.cursor.execute(sql_check,book_id)
            book = self.cursor.fetchone()
            if not book:
                print("失败：书不在馆或不存在！")
                return

            # 3. 开始借书操作
            now = datetime.datetime.now()  # 当前时间
            due = now + datetime.timedelta(days=7)

            sql_insert = "insert into borrower (book_id, username, borrow_time, return_time, status) values (%s, %s, %s, %s, %s)"
            self.cursor.execute(sql_insert, (book_id, self.current_user, now, due, '借阅中'))

            sql_update = "update book set status='借出' where book_id=%s"
            self.cursor.execute(sql_update,book_id)

            self.conn.commit()
            print(f"借阅成功！请在 {due.strftime('%Y-%m-%d')} 前归还。")

        except Exception as e:
            self.conn.rollback()
            print("借阅出错：", e)

    # 7. 归还图书
    def return_book(self, book_id):
        try:
            # 1. 检查这本书是否是你借的，且处于“借阅中”状态
            sql = "select * from borrower where book_id=%s and username=%s and status='借阅中'"
            self.cursor.execute(sql, (book_id, self.current_user))
            record = self.cursor.fetchone()
            if not record:
                print("失败：你没有借阅这本书，或者已经归还了。")
                return

            # 2. 开始还书操作
            sql_update_record = "update borrower set status='已归还' where book_id=%s"
            self.cursor.execute(sql_update_record, book_id)

            sql_update_book = "update book set status= '在馆' where book_id=%s"
            self.cursor.execute(sql_update_book,book_id)

            self.conn.commit()
            print("归还成功！")

        except Exception as e:
            self.conn.rollback()
            print("归还出错：", e)

    # 8. 修改密码
    def change_password(self):
        old_password = input("输入旧密码：")
        sql = "select * from admin where username=%s and password=%s"
        self.cursor.execute(sql, (self.current_user, old_password))
        if not self.cursor.fetchone():
            print("旧密码错误，无法修改！")
            return
        new_password = input("输入新密码: ")
        sql2 = "update admin set password=%s where username=%s"
        try:
            self.cursor.execute(sql2, (new_password, self.current_user))
            self.conn.commit()
            print("密码修改成功！")
        except Exception as e:
            print("修改失败:", e)

    #关闭
    def close(self):
        self.cursor.close()
        self.conn.close()

def main():
    # 1. 实例化对象
    lm = BookManager()

    # 2. 登录验证 (循环直到登录成功)

    # 3. 主菜单循环
    while True:
        print("1. 登录")
        print("2. 用户注册")
        print("3. 退出")
        n = input("请选择: ")
        if n == '1':
            while not lm.login():
                choice = input("输入 'q' 退出系统，回车重试: ")
                if choice.lower() == 'q':
                    print("系统已退出")
                    return
            while True:
                print(f"当前用户: {lm.current_user} ({lm.current_role})")
                if lm.current_role == 'super':
                    print("1. 添加图书")
                    print("2. 查询图书")
                    print("3. 修改图书信息")
                    print("4. 删除图书")
                    print("5. 借阅图书")
                    print("6. 归还图书")
                    print("7. 修改密码")
                    print("8. 增加删除账户")
                    print("0. 退出系统")
                    choice = input("请输入功能编号：")
                    if choice == "1":
                        bid = input("请输入图书编号：")
                        if bid.isdigit():
                            bid = int(bid)
                            title = input("请输入书名: ")
                            author = input("请输入作者: ")
                            publisher = input("请输入分类: ")
                            lm.add_book(bid, title, author, publisher)
                        else:
                            print("添加失败：图书编号必须是数字！")

                    elif choice == "2":
                        lm.search_book()

                    elif choice == "3":
                        bid = input("请输入要修改的图书编号：")
                        author = input("请输入新作者：")
                        publisher = input("请输入新分类：")
                        lm.update_book(bid, author, publisher)

                    elif choice == "4":
                        bid = input("请输入要删除的图书编号：")
                        lm.delete_book(bid)

                    elif choice == "5":
                        bid = input("请输入要借阅的图书编号：")
                        lm.borrow_book(bid)

                    elif choice == "6":
                        bid = input("请输入要归还的图书编号：")
                        lm.return_book(bid)

                    elif choice == "7":
                        lm.change_password()

                    elif choice == "8":
                        lm.add_admin()

                    elif choice == "0":
                        break

                    else:
                        print("输入无效，请输入 0-8 之间的数字")

                elif lm.current_role == 'admin':
                    print("1. 添加图书")
                    print("2. 查询图书 ")
                    print("3. 修改图书信息")
                    print("4. 删除图书")
                    print("5. 借阅图书")
                    print("6. 归还图书")
                    print("7. 修改密码")
                    print("0. 退出系统")
                    choice = input("请输入功能编号：")
                    if choice == "1":
                        bid = input("请输入图书编号：")
                        if bid.isdigit():
                            bid = int(bid)
                            title = input("请输入书名: ")
                            author = input("请输入作者: ")
                            publisher = input("请输入分类: ")
                            lm.add_book(bid, title, author, publisher)
                        else:
                            print("添加失败：图书编号必须是数字！")

                    elif choice == "2":
                        lm.search_book()

                    elif choice == "3":
                        bid = input("请输入要修改的图书编号：")
                        author = input("请输入新作者：")
                        publisher = input("请输入新分类：")
                        lm.update_book(bid, author, publisher)

                    elif choice == "4":
                        bid = input("请输入要删除的图书编号：")
                        lm.delete_book(bid)

                    elif choice == "5":
                        bid = input("请输入要借阅的图书编号：")
                        lm.borrow_book(bid)

                    elif choice == "6":
                        bid = input("请输入要归还的图书编号：")
                        lm.return_book(bid)

                    elif choice == "7":
                        lm.change_password()

                    elif choice == "0":
                        break

                    else:
                        print("输入无效，请输入 0-7 之间的数字")

                else:
                    print("1. 查询图书")
                    print("2. 借阅图书")
                    print("3. 归还图书")
                    print("4. 修改密码")
                    print("0. 退出系统")
                    choice = input("请输入功能编号：")

                    if choice == "1":
                        lm.search_book()

                    elif choice == "2":
                        bid = input("请输入要借阅的图书编号：")
                        lm.borrow_book(bid)

                    elif choice == "3":
                        bid = input("请输入要归还的图书编号：")
                        lm.return_book(bid)

                    elif choice == ("4"):
                        lm.change_password()

                    elif choice == "0":
                        break

                    else:
                        print("输入无效，请输入 0-4 之间的数字")
        elif n=='2':
            lm.add_user()
        else:
            lm.close()
            print("系统已退出，再见！")
            break

# 程序入口
if __name__ == "__main__":
    main()