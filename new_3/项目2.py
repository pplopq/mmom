import pandas as pd
from sklearn.preprocessing import StandardScaler
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

a=pd.read_csv(r"C:\py-study\new_3\train.csv")
b=pd.read_csv(r"C:\py-study\new_3\test.csv")
a['label'] = np.where(a['star'] >= 4, 1, 0)
b['label'] = np.where(b['star'] >= 4, 1, 0)
m=['Location#Transportation','Location#Downtown','Location#Easy_to_find',
   'Service#Queue','Service#Hospitality','Service#Parking','Service#Timely',
   'Price#Level','Price#Cost_effective','Price#Discount',
   'Ambience#Decoration','Ambience#Noise','Ambience#Space','Ambience#Sanitary',
   'Food#Portion','Food#Taste','Food#Appearance','Food#Recommend']

x_train=a[m]
y_train=a['label']
x_test=b[m]
y_test=b['label']
scaler = StandardScaler()
x_train_scaled = scaler.fit_transform(x_train)
x_test_scaled = scaler.transform(x_test)

model = LogisticRegression(random_state=42,max_iter=1000)
model.fit(x_train_scaled, y_train)
y_pred = model.predict(x_test_scaled)
print(classification_report(y_test, y_pred))
acc = model.score(x_test_scaled, y_test)
print(f"准确率: {acc:.4f}")

plt.figure(figsize=(8, 6))
cm = confusion_matrix(y_test, y_pred)
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=['差评', '好评'],
            yticklabels=['差评', '好评'])
plt.title('good')
plt.ylabel('2')
plt.xlabel('1')
plt.show()