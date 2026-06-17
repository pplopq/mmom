import os
from dotenv import load_dotenv
'''
load_dotenv(override=True)
api_key = os.getenv('GLM_API_KEY')
model = os.getenv('QWEN_MODEL','qwen-plus')
print(model)
print(api_key)


from cryptography.fernet import Fernet
key = Fernet.generate_key()
print(key.decode())

f = Fernet(key)
token = f.encrypt(b"my-secret-key")
print(token.decode())

original = f.decrypt(token)
print(original.decode())

with open("secret.key", "wb") as fout:
    fout.write(key)


from cryptography.fernet import Fernet
import os
def encrypt_env_file(input_file,output_file,key_file):
    #读取数据
    with open(input_file,"rb") as f:
        data = f.read()
    #生成新密钥
    key = Fernet.generate_key()
    #保存密钥
    with open(key_file,"wb") as f:
        f.write(key)
    print(key_file)
    #加密并保存
    fernet = Fernet(key)
    encrypted = fernet.encrypt(data)
    with open(output_file,"wb") as f:
        f.write(encrypted)
    print(output_file)
    print('请删除原始.env文件')

def decrypt_env_file(enc_file,key_file,output_file='.env.tmp'):
    #读取密钥
     with open(key_file,"rb") as f:
         key = f.read()
    #读取加密密钥
     with open(enc_file,"rb") as f:
         encrypted = f.read()
    #执行解密
     fernet = Fernet(key)
     decrypted = fernet.decrypt(encrypted)
    #解密后的东西
     with open(output_file,"wb") as f:
         f.write(decrypted)
     print(output_file)

a = ".env"
b = ".env.enc"
c = ".env.key"
encrypt_env_file(a,b,c)
decrypt_env_file(b,c)
'''
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import os
class SecretManager:
    def __init__(self,key_file='secret.key'):
        self.key_file = key_file
        self._fernet = None
    def _load_key(self):
        if self._fernet is not None:
            return self._fernet
        if not os.path.exists(self.key_file):
            raise FileNotFoundError(f'密钥文件不存在:{self.key_file}')

        with open(self.key_file,'rb') as f:
            key = f.read()
        self._fernet = Fernet(key)
        return self._fernet

    def decrypt_env(self,enc_file='.env.enc'):
        f = self._load_key()
        with open(enc_file,"rb") as file:
            dec = f.decrypt(file.read())

        with open('.env.tmp','wb') as tmp:
            tmp.write(dec)
        load_dotenv('.env.tmp')
        #删除临时明文
        os.remove('.env.tmp')
        print("解密完成")

    @staticmethod
    def create_key(save_path = 'secret.key'):
        key = Fernet.generate_key()
        with open(save_path,'wb') as f:
            f.write(key)
        return key

    def encrypt_env(source: str = '.env', target='.env.enc', k_path='secret.key'):
        with open(k_path, 'rb') as f:
            k = f.read()
        fer = Fernet(k)
        with open(source, 'rb') as f:
            raw = f.read()
        cipher_data = fer.encrypt(raw)
        with open(target, 'wb') as f:
            f.write(cipher_data)
        print('加密成功')















