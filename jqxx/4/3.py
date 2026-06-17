import jieba
import pandas as pd
from sklearn.model_selection import train_test_split
# 导入 Keras 相关库
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, GlobalMaxPooling1D, Dense, Dropout

# ================= 数据准备 =================
data_list = [
    # 正面样本 (45条)
    ("味道超棒，服务好", 1), ("电影太好看了，强烈推荐", 1), ("商品质量不错，物流很快", 1),
    ("环境优雅，性价比很高", 1), ("非常满意，下次还来", 1), ("味道好，干净卫生", 1),
    ("超出预期，体验极佳", 1), ("客服态度好，问题解决快", 1), ("产品做工精细，细节到位", 1),
    ("价格实惠，物超所值", 1), ("服务周到，让人舒服", 1), ("效果远超预期，非常满意", 1),
    ("物流快，包装好", 1), ("口味正宗，分量十足", 1), ("质量上乘，值得购买", 1),
    ("体验感满分，强烈安利", 1), ("环境干净整洁，体验很好", 1), ("态度热情，全程很愉快", 1),
    ("效果很好，会回购的", 1), ("各方面都很满意，好评", 1),("材质环保，没有异味", 1),
    ("包装非常严实，没有任何破损", 1),("发货速度惊人，第二天就到了", 1),("颜色很正，没有色差，喜欢", 1),
    ("面料舒服，穿着透气", 1),("口感很好，甜度适中", 1),("安装简单，说明书很清楚", 1),
    ("电池耐用，续航能力强", 1),("屏幕清晰，色彩还原度高", 1),("音质很棒，低音深沉", 1),
    ("孩子很喜欢，玩得不亦乐乎", 1),("分量很足，两个人吃不完", 1),("新鲜度很高，水果很甜", 1),
    ("客服回复及时，很有耐心", 1),("性价比无敌，这个价格值了", 1),("做工精良，细节处理得很好", 1),
    ("运行流畅，不卡顿", 1),("隔音效果好，睡眠质量提高了", 1),("味道正宗，是家乡的味道", 1),
    ("服务态度一流，宾至如归", 1),("赠品很实用，惊喜", 1),("回购很多次了，一如既往的好", 1),
    ("设计人性化，使用很方便", 1),("清洁能力强，家里干净多了", 1),("信号稳定，网速快", 1),
    # 负面样本 (45条)
    ("太难吃了，再也不会来这家店", 0), ("电影剧情无聊，浪费时间", 0), ("商品质量差，发货很慢", 0),
    ("价格贵，体验很差", 0), ("非常失望，不推荐购买", 0), ("卡顿严重，体验极差", 0),
    ("做工粗糙，不值这个价", 0), ("客服态度差，解决不了问题", 0), ("物流太慢了，等了半个月", 0),
    ("味道难吃，完全踩雷", 0), ("质量堪忧，用了两天就坏了", 0), ("价格虚高，完全不值", 0),
    ("服务态度恶劣，再也不来", 0), ("效果很差，完全没用", 0), ("体验糟糕，差评", 0),
    ("环境脏乱差，太失望了", 0), ("态度冷漠，全程很糟心", 0), ("发货错误，售后也不管", 0),
    ("质量问题严重，不建议买", 0), ("完全不符合预期，避雷", 0),("全是线头，像地摊货", 0),
    ("快递太慢了，等了一周才到", 0),("实物和图片差距太大，被骗了", 0),("穿了一次就起球，质量太差", 0),
    ("太咸了，根本没法吃", 0),("零件缺失，根本装不起来", 0),("充不进电，废品", 0),
    ("全是坏点，看着眼睛疼", 0),("有杂音，听歌体验极差", 0),("玩具味道刺鼻，不敢给孩子玩", 0),
    ("只有几口，完全吃不饱", 0),("收到时已经烂了，不新鲜", 0),("发消息从来不理人，什么态度", 0),
    ("这就是智商税，谁买谁后悔", 0),("缝隙很大，显得很低档", 0),("用一会就发烫，甚至死机", 0),
    ("根本不隔音，吵得要死", 0),("难以下咽，像是剩菜", 0),("爱答不理的，体验极差", 0),
    ("说好的赠品没有，骗人", 0),("再也不会来了，拉黑", 0),("操作反人类，设计有缺陷", 0),
    ("吸力太小，扫不干净", 0),("经常断网，连接不稳定", 0),("甲醛超标，头晕恶心", 0)
]

texts = [i[0] for i in data_list]
labels = [i[1] for i in data_list]
df = pd.DataFrame({'text': texts, 'label': labels})

# 2. 【优化】停用词表：保留否定词，修复语法错误
stop_words = [
    "的", "了", "着", "过",
    "吗", "呢", "吧", "啊",
    "这", "那", "哪",
    "是", "有",
    "和", "跟", "与", "同",
    "在", "从", "向", "对",
    "把", "被", "让", "叫",  # <--- 这里必须加逗号！
    "，", "。", "！", "？", "、", "；", "："
]

def cut_filter(text):
    words = jieba.lcut(text)
    # 过滤停用词和空字符串
    words = [w for w in words if w not in stop_words and len(w.strip()) > 0]
    return " ".join(words)

df['cut_text'] = df['text'].apply(cut_filter)

# 打印一条看看分词效果，确认“不”字还在
print(f"示例分词: {df['cut_text'].iloc[0]}")

x = df['cut_text'].values
y = df['label'].values

# ================= 模型构建与训练 =================
VOCAB_SIZE = 2000
MAX_LEN = 30

tokenizer = Tokenizer(num_words=VOCAB_SIZE)
tokenizer.fit_on_texts(x)
x_seq = tokenizer.texts_to_sequences(x)
x_pad = pad_sequences(x_seq, maxlen=MAX_LEN)

# 【重要修改】数据太少，test_size 改小一点，给模型更多学习机会
x_train, x_test, y_train, y_test = train_test_split(
    x_pad, y, test_size=0.2, random_state=2026, stratify=y
)

model = Sequential([
    Embedding(input_dim=VOCAB_SIZE, output_dim=32, input_length=MAX_LEN),
    GlobalMaxPooling1D(),
    Dense(16, activation='relu'),
    Dropout(0.5),
    Dense(1, activation='sigmoid')
])

model.compile(
    optimizer='adam',
    loss='binary_crossentropy',
    metrics=['accuracy']
)

print("开始训练...")
# 数据少的时候，epochs 可以适当多一点，batch_size 设小一点
model.fit(
    x_train, y_train,
    epochs=30,
    batch_size=8,
    verbose=1
)

loss, acc = model.evaluate(x_test, y_test, verbose=0)
print(f"\n测试集 Loss: {loss:.4f}, Accuracy: {acc:.4f}")

# ================= 预测功能 =================
def pred_sent(text):
    txt = cut_filter(text)
    seq = tokenizer.texts_to_sequences([txt])
    pad_seq = pad_sequences(seq, maxlen=MAX_LEN)
    score = model.predict(pad_seq, verbose=0)[0][0]
    return f"{text} -> {'正面' if score > 0.5 else '负面'} (置信度: {score:.4f})"

print("\n--- 预测测试 ---")
print(pred_sent("性价比高，体验不错"))
print(pred_sent("不好用，非常失望"))
print(pred_sent("这东西一般般，没什么特别的"))