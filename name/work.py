import os
from datetime import datetime
from openai import OpenAI
from cryptography.fernet import Fernet
from dotenv import load_dotenv

class SecretManager:
    def __init__(self, key_file='secret.key'):
        self.key_file = key_file
        self._fernet = None

    def _load_key(self):
        if self._fernet is not None:
            return self._fernet
        if not os.path.exists(self.key_file):
            raise FileNotFoundError(f'密钥文件不存在:{self.key_file}')

        with open(self.key_file, 'rb') as f:
            key = f.read()
        self._fernet = Fernet(key)
        return self._fernet

    def decrypt_env(self, enc_file='.env.enc'):
        f = self._load_key()
        with open(enc_file, "rb") as file:
            dec = f.decrypt(file.read())

        with open('.env.tmp', 'wb') as tmp:
            tmp.write(dec)
        load_dotenv('.env.tmp')
        os.remove('.env.tmp')
        print("解密完成")

    @staticmethod
    def create_key(save_path='secret.key'):
        key = Fernet.generate_key()
        with open(save_path, 'wb') as f:
            f.write(key)
        return key

    def encrypt_env(self, source='.env', target='.env.enc', k_path='secret.key'):
        with open(k_path, 'rb') as f:
            k = f.read()
        fer = Fernet(k)
        with open(source, 'rb') as f:
            raw = f.read()
        cipher_data = fer.encrypt(raw)
        with open(target, 'wb') as f:
            f.write(cipher_data)
        print('加密成功')

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
            messages = [{'role': 'system', 'content': system_prompt}]
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
    sm = SecretManager()

    # 检查是否需要生成密钥或加密文件 (首次运行引导)
    if not os.path.exists('secret.key'):
        print("检测到未初始化，正在生成密钥...")
        sm.create_key()

    if not os.path.exists('.env.enc') and os.path.exists('.env'):
        print("检测到明文 .env 文件，正在加密...")
        sm.encrypt_env()
        os.remove('.env')  # 加密后删除明文以保安全
        print("已删除明文 .env 文件")

    sm.decrypt_env()

    log('对话开始:')
    while True:
        a = int(input("1.千问。2.智谱。请输入选项："))
        if a == 1:
            api = os.getenv('QWEN_API_KEY')
            ai = LLM("qwen", api_key=api)
            n1(ai)
        elif a == 2:
            api = os.getenv('GLM')
            ai = LLM("glm", api_key=api)
            n1(ai)
        else:
            print('对话结束，再见')
            log("对话结束")
            log_file.close()
            break
            