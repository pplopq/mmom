import jieba
import pandas as pd
import os
import re
from sklearn.model_selection import train_test_split
# 1. 导入 Keras 相关库 (来自 项目3.py 的架构)
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, GlobalMaxPooling1D, Dense
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.layers import Dropout
# ===================== 1. 配置与数据加载 (来自 项目2.py) =====================
# 你的数据集路径
dataset_path = r"C:\Users\zc\.cache\modelscope\hub\datasets\yangjiurong\chinese-news-sentiment-c3-ds\data.csv"

print(f"正在尝试加载数据: {dataset_path}")
if not os.path.exists(dataset_path):
    print("错误：找不到数据文件！正在创建模拟数据集用于演示...")
    data = {
        'text': ['味道超棒，服务好', '电影太好看了', '太难吃了，再也不会来', '质量差，体验糟糕', '性价比很高，推荐购买',
                 '非常失望，完全不值'],
        'label': [1, 1, 0, 0, 1, 0]
    }
    df = pd.DataFrame(data)
else:
    try:
        df = pd.read_csv(dataset_path, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(dataset_path, encoding='gbk')
    print(f"数据加载成功，共 {len(df)} 条数据。")

# --- 智能适配列名 & 标签处理 ---
text_col = df.columns[0]
label_col = df.columns[-1]

# 将标签转换为数字 (0 和 1)
unique_labels = df[label_col].unique()
label_map = {val: idx for idx, val in enumerate(sorted(unique_labels))}
df['label'] = df[label_col].map(label_map)

# 清洗空值
df = df.dropna(subset=[text_col, 'label'])
df[text_col] = df[text_col].astype(str)
print(f"标签映射关系: {label_map}")

# ===================== 2. 预处理配置 (融合 项目2.py 的清洗 + 项目3.py 的分词) =====================
# A. 停用词表 (保留否定词 "不"、"没"，去除无意义虚词)
# 注意：这里去掉了 "不"，因为情感分析中否定词至关重要
stop_words = {
    "的", "了", "在", "是", "我", "有", "和", "就", "人", "都", "一", "一个", "上", "也", "很", "到", "说", "要", "去",
    "你",
    "会", "着", "没有", "看", "好", "自己", "这", "他", "她", "它", "们", "那", "些", "什么", "怎么", "如何", "为什么",
    "吗", "吧", "呢", "啊", "哦", "嗯", "之", "与", "及", "等", "被", "把", "让", "向", "从", "对", "为", "以", "而",
    "但", "并", "或者", "如果", "虽然", "因为", "所以", "关于", "通过", "进行", "这个", "那个", "这些", "那些"
}


# B. 分词函数
def cut_and_filter(text):
    if not isinstance(text, str):
        return ""
    # 1. 去除特殊字符、数字、英文字母（只保留中文）
    text = re.sub(r'[^\u4e00-\u9fa5]', '', text)
    # 2. Jieba 分词
    words = jieba.lcut(text)
    # 3. 过滤停用词 + 过滤单字 (可选，但在短文本情感分析中，保留单字如"差"、"烂"可能更好，这里为了演示保留长度>1)
    # 如果效果不好，可以将 len(w) > 1 改为 len(w) > 0
    filtered_words = [w for w in words if w not in stop_words and len(w) > 1]
    return " ".join(filtered_words)


print("正在进行分词处理...")
df['cut_text'] = df[text_col].apply(cut_and_filter)
# 移除分词后为空的行
df = df[df['cut_text'].str.len() > 0]

X_text = df["cut_text"].values
y = df["label"].values

# ===================== 3. 特征工程 (来自 项目3.py: Tokenizer) =====================
VOCAB_SIZE = 5000  # 词汇表大小
MAX_LEN = 30  # 每条文本保留的最大长度

print("正在序列化文本...")
tokenizer = Tokenizer(num_words=VOCAB_SIZE)
tokenizer.fit_on_texts(X_text)
x_seq = tokenizer.texts_to_sequences(X_text)
x_pad = pad_sequences(x_seq, maxlen=MAX_LEN)

# ===================== 4. 模型构建与训练 (来自 项目3.py) =====================
x_train, x_test, y_train, y_test = train_test_split(
    x_pad, y, test_size=0.2, random_state=2026, stratify=y
)

print("\n正在构建深度学习模型...")


model = Sequential([
    Embedding(input_dim=VOCAB_SIZE, output_dim=32, input_length=MAX_LEN),
    GlobalMaxPooling1D(),
    Dense(16, activation='relu'),
    Dropout(0.5),  # 新增
    Dense(1, activation='sigmoid')
])
optimizer = Adam(learning_rate=0.001)
model.compile(
    optimizer=optimizer,
    loss='binary_crossentropy',
    metrics=['accuracy']
)

# 训练模型
model.fit(
    x_train, y_train,
    epochs=10,  # 根据数据量调整，数据少时 epochs 可以大一点
    batch_size=32,  # 批大小
    verbose=1
)

# 评估
loss, acc = model.evaluate(x_test, y_test, verbose=0)
print(f"\n===== 模型评估 =====")
print(f"测试集 Loss: {loss:.4f}, Accuracy: {acc:.4f}")


# ===================== new_3. 预测新数据 =====================
def pred_sent(text):
    # 1. 预处理
    txt = cut_and_filter(text)
    if not txt:
        print("无法分析（无有效中文内容）")
        return

    # 2. 序列化与填充
    seq = tokenizer.texts_to_sequences([txt])
    pad_seq = pad_sequences(seq, maxlen=MAX_LEN)

    # 3. 预测
    score = model.predict(pad_seq, verbose=0)[0][0]
    label = "正面" if score > 0.5 else "负面"

    print(f"\n输入：{text}")
    print(f"处理后：{txt}")
    print(f"模型判断：{label} (置信度: {score:.4f})")
    return label


print("\n===== 开始测试预测 =====")
pred_sent("这项政策非常有利于经济发展，市场前景广阔")
pred_sent("由于管理混乱，导致项目严重延期，损失惨重")
pred_sent("今天天气不错，心情很好")
pred_sent("这东西一般般，没什么特别的")