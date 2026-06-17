import jieba
from gensim.models import Word2Vec

# 1. 扩充语料，让语义更清晰
sentences = [
    "今天天气很好，我很开心",
    "心情愉悦，十分开心",
    "今天晴空万里，出去玩特别快乐",
    "我很高兴能和朋友一起玩",
    "收到礼物，我非常高兴",
    "今天下雨，心情低落，很难过",
    "阴雨连绵，让人感到郁闷",
    "考试没考好，我很难过",
    "今天很糟糕，心情郁闷",
    "天气不好，让人心情低落"
]

# 2. 分词
cut_texts = [jieba.lcut(s) for s in sentences]

# 3. 调整参数训练模型
model = Word2Vec(
    sentences=cut_texts,
    vector_size=10,    # 维度调大，模型泛化性更好
    window=3,          # 上下文窗口调大，看到更多词
    min_count=1,
    sg=0,
    epochs=100         # 训练轮次增加，让模型学透
)

# 4. 测试
print("开心 的词向量（前5维）：")
print(model.wv["开心"][:5])

print("\n和开心最相近的词：")
print(model.wv.most_similar("开心", topn=3))

sim1 = model.wv.similarity("开心", "快乐")
sim2 = model.wv.similarity("开心", "难过")
print(f"\n开心和快乐相似度：{sim1:.2f}")
print(f"开心和难过相似度：{sim2:.2f}")