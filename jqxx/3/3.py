from matplotlib import pyplot as plt
from sklearn.datasets import make_classification
import numpy as np
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 有监督
x, y = make_classification(
    n_samples=500,
    n_features=2,
    n_informative=2,
    n_redundant=0,
    n_clusters_per_class=1,
    flip_y=0.05,
    random_state=42
)

x[:, 0] = np.interp(x[:, 0], (x[:, 0].min(), x[:, 0].max()), (0, 60))
x[:, 1] = np.interp(x[:, 1], (x[:, 1].min(), x[:, 1].max()), (0, 90))

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42)

model = LogisticRegression()
model.fit(x_train, y_train)
y_pred = model.predict(x_test)

print("有监督学习（分类）结果")
print(f"准确率: {accuracy_score(y_test,y_pred):.2f}")

plt.figure(figsize=(10, 6))
plt.scatter(x[y==0,0],x[y==0,1],alpha=0.7,color='blue',label='减肥失败')
plt.scatter(x[y==1,0],x[y==1,1],alpha=0.7,color='red',label='减肥成功')
plt.xlabel('每月运动次数')
plt.ylabel('每次运动时长（分钟）')
plt.title('减肥分布')
plt.legend()
plt.grid(True)
plt.show()

