import pandas as pd
import numpy as np
import jieba
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from collections import Counter
from sklearn.metrics import classification_report

# ==========================================
# 1. 配置与超参数
# ==========================================
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
BATCH_SIZE = 64
EPOCHS = 10
LEARNING_RATE = 0.001
MAX_VOCAB_SIZE = 10000  # 词表大小
MAX_SEQ_LEN = 100       # 句子最大长度（截断或填充）

print(f"Using device: {DEVICE}")

# ==========================================
# 2. 数据预处理与词表构建
# ==========================================
def load_data():
    a = pd.read_csv(r"C:\py-study\new_3\train.csv")
    b = pd.read_csv(r"C:\py-study\new_3\test.csv")

    # 标签处理：>=4星为1，否则为0
    a['label'] = (a['star'] >= 4).astype(int)
    b['label'] = (b['star'] >= 4).astype(int)

    # 简单分词（深度学习对分词要求不严，但jieba对中文依然有效）
    a['text'] = a['review'].apply(lambda x: " ".join(jieba.cut(str(x))))
    b['text'] = b['review'].apply(lambda x: " ".join(jieba.cut(str(x))))

    return a, b

def build_vocab(texts):
    counter = Counter()
    for text in texts:
        counter.update(text.split())

    # 建立词到索引的映射，<PAD>用于填充，<UNK>用于未知词
    word2idx = {"<PAD>": 0, "<UNK>": 1}
    idx = 2
    for word, _ in counter.most_common(MAX_VOCAB_SIZE - 2):
        word2idx[word] = idx
        idx += 1
    return word2idx

def encode_text(text, word2idx):
    indices = [word2idx.get(w, word2idx["<UNK>"]) for w in text.split()]
    # 截断或填充
    if len(indices) > MAX_SEQ_LEN:
        indices = indices[:MAX_SEQ_LEN]
    else:
        indices = indices + [word2idx["<PAD>"]] * (MAX_SEQ_LEN - len(indices))
    return indices

# ==========================================
# 3. 数据集定义
# ==========================================
class ReviewDataset(Dataset):
    def __init__(self, df, word2idx):
        self.texts = [encode_text(t, word2idx) for t in df['text']]
        self.labels = df['label'].values.astype(np.float32)

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        return torch.tensor(self.texts[idx], dtype=torch.long), torch.tensor([self.labels[idx]], dtype=torch.float32)

# ==========================================
# 4. 模型定义 (TextCNN)
# ==========================================
class TextCNN(nn.Module):
    def __init__(self, vocab_size, embed_dim, num_classes, filter_sizes, num_filters):
        super(TextCNN, self).__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.convs = nn.ModuleList([
            nn.Conv2d(1, num_filters, (fs, embed_dim)) for fs in filter_sizes
        ])
        self.dropout = nn.Dropout(0.5)
        self.fc = nn.Linear(num_filters * len(filter_sizes), num_classes)

    def forward(self, x):
        x = self.embedding(x).unsqueeze(1)  # (batch, 1, seq_len, embed_dim)
        conv_outs = [torch.relu(conv(x)).squeeze(3) for conv in self.convs]
        pooled_outs = [torch.max(out, dim=2)[0] for out in conv_outs]
        cat_out = torch.cat(pooled_outs, dim=1)
        out = self.dropout(cat_out)
        return self.fc(out)

# ==========================================
# 5. 训练与评估流程
# ==========================================
def train_model():
    # 加载数据
    train_df, test_df = load_data()
    vocab = build_vocab(train_df['text'])

    train_dataset = ReviewDataset(train_df, vocab)
    test_dataset = ReviewDataset(test_df, vocab)

    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False)

    # 初始化模型
    model = TextCNN(
        vocab_size=len(vocab),
        embed_dim=128,
        num_classes=1,  # 二分类输出一个值
        filter_sizes=[2, 3, 4], # 卷积核大小，对应2-gram, 3-gram, 4-gram
        num_filters=100
    ).to(DEVICE)

    criterion = nn.BCEWithLogitsLoss()
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)

    # 训练循环
    model.train()
    for epoch in range(EPOCHS):
        total_loss = 0
        for texts, labels in train_loader:
            texts, labels = texts.to(DEVICE), labels.to(DEVICE)
            optimizer.zero_grad()
            outputs = model(texts).squeeze(1)
            loss = criterion(outputs, labels.squeeze(1))
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

        print(f"Epoch {epoch+1}/{EPOCHS}, Loss: {total_loss/len(train_loader):.4f}")

    # 评估
    model.eval()
    all_preds = []
    all_labels = []
    with torch.no_grad():
        for texts, labels in test_loader:
            texts = texts.to(DEVICE)
            outputs = model(texts).squeeze(1)
            preds = (torch.sigmoid(outputs) >= 0.5).float().cpu().numpy()
            all_preds.extend(preds)
            all_labels.extend(labels.numpy())

    print("\n--- 测试集评估报告 ---")
    print(classification_report(all_labels, all_preds, target_names=['差评', '好评']))

if __name__ == "__main__":
    train_model()