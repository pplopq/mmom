def register_user(self):
    """
    用户注册功能（针对普通用户/学生）
    """
    print("\n=== 用户注册 ===")
    username = input("请输入新账号名: ").strip()
    password = input("请输入新密码: ").strip()

    # 简单验证
    if not username or not password:
        print("❌ 账号或密码不能为空！")
        return

    # SQL 插入语句 (假设表名为 user，字段为 username, password)
    # 注意：如果你的表名是 student 或其他，请修改这里
    sql = "INSERT INTO user (username, password) VALUES (%s, %s)"

    try:
        # 执行插入
        self.cursor.execute(sql, (username, password))
        self.conn.commit()
        print(f"✅ 用户 [{username}] 注册成功！现在可以登录了。")

        # 可选：记录日志
        self.write_log(f"新用户注册成功: {username}")

    except Exception as e:
        # 回滚事务，防止数据错误
        self.conn.rollback()
        # 这里的错误通常是因为主键冲突（账号已存在）
        print(f"❌ 注册失败：账号可能已存在，或数据库错误。")
        # print(f"详细错误: {e}") # 调试时可以打开这行看具体错误

        # 假设这是你的登录/主界面菜单逻辑
    print("1. 管理员登录")
    print("2. 用户注册")  # 新增这一行
    print("3. 退出")

    choice = input("请选择: ")
    if choice == '2':
        self.register_user()  # 调用刚才写的函数