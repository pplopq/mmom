import sklearn as sk
from keras.src.losses import mean_absolute_error
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import accuracy_score, r2_score
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression, LinearRegression
import numpy as np

'''
iris = load_iris()
x = iris.data
y=iris.target
plt.figure(figsize=(10,6))
colors = ['red', 'green', 'blue']
for i,c in enumerate(colors):
    plt.scatter(x[y==i,0],x[y==i,2],c=c,label=iris.target_names[i],edgecolors='k',s=50)
    plt.xlabel('Sepal Length')
    plt.ylabel('Petal Length')
    plt.title('Iris Dataset')
    plt.legend()
    plt.show()

x_train,x_test,y_train,y_test = train_test_split(x,y,test_size=0.2,random_state=0)
pipe = make_pipeline(StandardScaler(),LogisticRegression())
pipe.fit(x_train,y_train)

y_pred = pipe.predict(x_test)
accuracy= accuracy_score(y_test,y_pred)
print(accuracy)

iris = load_iris()
x = iris.data
y=iris.target

x_train,x_test,y_train,y_test = train_test_split(x,y,test_size=0.2,random_state=0,stratify=y)

scaler = StandardScaler()
x_train_scaled = scaler.fit_transform(x_train)
x_test_scaled = scaler.transform(x_test)

a = LogisticRegression(max_iter=200,random_state=42)
a.fit(x_train_scaled, y_train)

y_train_pred = a.predict(x_train_scaled)
y_test_pred = a.predict(x_test_scaled)

train_acc = accuracy_score(y_train,y_train_pred)
test_acc = accuracy_score(y_test,y_test_pred)

print(train_acc)
print(test_acc)



np.random.seed(42)
area =np.random.randint(50,150,size=100)
price =1.2*area+np.random.normal(0,10,size=100)
x=area.reshape(-1,1)
y=price
print(x.shape)
print(y.shape)

x_train,x_test,y_train,y_test = train_test_split(x,y,test_size=0.2,random_state=0)
print(f"训练集大小{x_train.shape[0]}")
print(f"测试集大小：{x_test.shape[0]}")

model = LinearRegression()
model.fit(x_train,y_train)
print(f"模型斜率{model.coef_[0]: .4f}")
print(f"模型截距{model.intercept_: .4f}")

plt.figure(figsize=(10,6))
x_line = x_test.flatten()
indices = np.argsort(x_line)
x_line_sorted = x_line[indices]

y_line = model.coef_[0] * x_line_sorted + model.intercept_

plt.plot(x_line_sorted,y_line,'r')

# plt.figure(figsize=(10,6))
# plt.scatter(area,price,alpha=0.7,color='skyblue',label='data price')
plt.xlabel('area')
plt.ylabel('price')
plt.title('bt')
plt.legend()
plt.grid(True)
plt.show()

y_pred = model.predict(x_test)
mae = mean_absolute_error(y_test,y_pred)
r2 = r2_score(y_test,y_pred)
print(f"{mae: .4f}")
print(f"{r2: .4f}")
'''
np.random.seed(42)
area =np.random.randint(50,150,size=100)
price =1.2*area+np.random.normal(0,10,size=100)
x=area.reshape(-1,1)
y=price
print(x.shape)
print(y.shape)

x_train,x_test,y_train,y_test = train_test_split(x,y,test_size=0.2,random_state=0)
print(f"训练集大小{x_train.shape[0]}")
print(f"测试集大小：{x_test.shape[0]}")

rf_model = RandomForestRegressor(n_estimators=100,random_state=42)
rf_model.fit(x_train,y_train)
y_pred = rf_model.predict(x_test)
print(y_pred)






















