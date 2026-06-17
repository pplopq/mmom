import jieba
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
import re


a=pd.read_csv(r"C:\py-study\new_3\train.csv")
b=pd.read_csv(r"C:\py-study\new_3\test.csv")
y_train = a['star']
y_test = b['star']
stop_words_list = set([
    '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到',
    '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这', '他', '她', '它', '们', '那', '些',
    '什么', '怎么', '如何', '吗', '吧', '呢', '啊', '哦', '嗯', '哎', '呀', '哈', '嘿', '呵', '嘻', '噗',
    '与', '及', '等', '之', '而', '但', '但是', '虽然', '因为', '所以', '如果', '即使', '尽管', '不管',
    '把', '被', '让', '给', '对', '对于', '关于', '以', '用', '从', '向', '往', '朝', '比', '跟', '同',
    '和', '或', '以及', '并且', '而且', '或者', '还是', '要么', '与其', '不如', '宁可', '宁愿'
])
def clean_and_tokenize(text):
    if not isinstance(text, str):
        return ""
    text = re.sub(r'[^\w\u4e00-\u9fa5]', '', text)
    words = jieba.cut(text)
    filtered_words = [word for word in words if word not in stop_words_list and len(word) > 1]
    return " ".join(filtered_words)

a['cut_review'] = a['review'].apply(clean_and_tokenize)
b['cut_review'] = b['review'].apply(clean_and_tokenize)

tfidf = TfidfVectorizer(
    max_features=3000,
    min_df=3,
    ngram_range=(1, 1),
    sublinear_tf=True
)

x_train = tfidf.fit_transform(a['cut_review'])

x_test = tfidf.transform(b['cut_review'])

model = LogisticRegression(
    solver='lbfgs',
    multi_class='multinomial',
    max_iter=1000
)

model.fit(x_train, y_train)

y_pred = model.predict(x_test)

accuracy = model.score(x_test, y_test)
print(f"模型准确率: {accuracy:.4f}")

print(classification_report(y_test, y_pred))