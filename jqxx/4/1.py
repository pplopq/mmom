import jieba
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# ===================== 【核心修改：加载外部数据集】 =====================

# 1. 设置文件路径
# 注意：请根据你截图中的实际路径修改这里。
# 通常在 C:\Users\用户名\.cache\modelscope\hub\datasets\...\data.csv
file_path = r"C:\Users\zc\.cache\modelscope\hub\datasets\yangjiurong\chinese-news-sentiment-c3-ds\data.csv"

try:
    # 尝试读取CSV (如果报错，可能需要尝试 encoding='gbk')
    df = pd.read_csv(file_path)

    # 打印列名，方便确认哪一列是文本，哪一列是标签
    print(f"数据集列名: {df.columns.tolist()}")
    print(f"数据集形状: {df.shape}")

    # 2. 数据清洗与重命名
    # 假设第一列是文本(text)，第二列是标签(label)。
    # 如果列名不同，请根据上面打印的列名修改下面的 'text' 和 'label'
    # 例如：df.rename(columns={'content': 'text', 'sentiment': 'label'}, inplace=True)

    # 删除空行（非常重要，防止报错）
    df.dropna(subset=['text', 'label'], inplace=True)

    # 3. 标签数字化 (Label Encoding)
    # 该数据集通常有 3 类：negative(负面), neutral(中性), positive(正面)
    # 朴素贝叶斯二分类通常需要把 "neutral" 去掉，或者归并。
    # 这里我们演示：只保留 正面(1) 和 负面(0)，过滤掉中性。

    unique_labels = df['label'].unique()
    print(f"原始标签类型: {unique_labels}")

    # 定义映射规则 (根据你的数据集实际情况调整字符串)
    label_map = {
        'positive': 1,
        'Positive': 1,
        '1': 1,       # 有些数据集直接用数字
        'negative': 0,
        'Negative': 0,
        '0': 0
    }

    # 过滤掉不在映射表里的标签（比如 'neutral' 或 '2'）
    df = df[df['label'].isin(label_map.keys())]

    # 应用映射
    df['label'] = df['label'].map(label_map)

    # 为了防止数据量太大跑得太慢，我们可以只取前 5000 条进行测试
    # 如果你想用全量数据，注释掉下面这一行即可
    df = df.sample(n=5000, random_state=42)

    print(f"清洗后数据量: {len(df)}")

except FileNotFoundError:
    print("错误：找不到文件，请检查 file_path 路径是否正确！")
    exit()
except Exception as e:
    print(f"读取数据出错: {e}")
    exit()

# ======================================================================


# ===================== 【保持不变：预处理逻辑】 =====================

# 自定义停用词 (可以针对新闻语料适当扩充)
stop_words = {"的", "了", "也", "很", "都", "就", "是", "会", "来", "这", "还会", "再", "，", "。", "！", "？", " ", "\n"}


def cut_and_filter(text):
    if not isinstance(text, str):
        return ""
    words = jieba.lcut(text)
    words = [w for w in words if w not in stop_words and len(w) > 0]
    return " ".join(words)


# 执行分词
print("正在分词...")
df["cut_text"] = df["text"].apply(cut_and_filter)

X = df["cut_text"]
y = df["label"]

# TF-IDF 向量化
tfidf = TfidfVectorizer(ngram_range=(1, 2), max_features=5000) # 限制最大特征数，防止内存溢出
X_tfidf = tfidf.fit_transform(X)

# 划分数据集
X_train, X_test, y_train, y_test = train_test_split(
    X_tfidf, y, test_size=0.2, random_state=66, stratify=y
)

# 训练模型
clf = MultinomialNB(alpha=0.8)
clf.fit(X_train, y_train)

# 评估
y_pred = clf.predict(X_test)
print(f"\n测试集准确率：{accuracy_score(y_test, y_pred):.4f}")


# ===================== 【保持不变：预测函数】 =====================

def pred_sent(text):
    txt = cut_and_filter(text)
    vec = tfidf.transform([txt])

    # 获取概率
    proba = clf.predict_proba(vec)[0]
    # 注意：predict_proba 返回的顺序取决于 clf.classes_
    # 通常是 [0的概率, 1的概率] 即 [负面, 正面]

    res = clf.predict(vec)[0]
    result = "正面" if res == 1 else "负面"

    print(f"\n输入：{text}")
    print(f"模型判断：{result}")
    # 简单展示概率
    print(f"各类别概率分布: {dict(zip(clf.classes_, proba))}")
    return result


# 测试
print("\n===== 开始测试 =====")
pred_sent("服务非常好，我很满意")
pred_sent("质量太差了，完全是骗人")
pred_sent("今天天气不错") # 这种中性句子在二分类模型中可能会被迫归类