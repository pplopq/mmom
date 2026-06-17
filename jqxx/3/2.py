from keras.src.losses import mean_absolute_error
from matplotlib import pyplot as plt
from sklearn.cluster import KMeans
from sklearn.datasets import load_iris, make_regression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import numpy as np
import tensorflow as tf
tf.experimental.numpy.experimental_enable_numpy_behavior()
'''
plt.rcParams['font.sans-serif']=['SimHei']
plt.rcParams['axes.unicode_minus']=False

iris = load_iris()
x = iris.data

scaler = StandardScaler()
x_scaled = scaler.fit_transform(x)

kmeans = KMeans(n_clusters=new_3, random_state=42)

y_pred = kmeans.fit_predict(x_scaled)

print("中心点：")
print(kmeans.cluster_centers_)

plt.scatter(x_scaled[:,0],x_scaled[:,1],c=y_pred,cmap='viridis')

centers = kmeans.cluster_centers_
plt.scatter(centers[:,0],centers[:,1],c='red',marker='x',s=100,label='中心')
plt.title('结果')
plt.legend()
plt.show()
'''


x,y=make_regression(
    n_samples=500,
    n_features=3,
    noise=25,
    random_state=42,
)
plt.rcParams['font.sans-serif']=['SimHei']
plt.rcParams['axes.unicode_minus']=False
x[:,0]=np.interp(x[:,0],(x[:,0].min(),x[:,0].max()),(50,150))
x[:,1]=np.interp(x[:,1],(x[:,1].min(),x[:,1].max()),(0,30))
x[:,2]=np.interp(x[:,2],(x[:,2].min(),x[:,2].max()),(1,5))
x[:,2]=np.round(x[:,2]).astype(int)

y=np.interp(y,(y.min(),y.max()),(80,500))
y=np.round(y,2)

print(x.shape)
print(y.shape)
print(x[:5])
print(y[:5])

x_train,x_test,y_train,y_test = train_test_split(
    x,
    y,
    test_size=0.2,
    random_state=42,
)
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(x_train,y_train)
y_pred = model.predict(x_test)

print(round(r2_score(y_test,y_pred),4))
print(round(mean_absolute_error(y_test,y_pred),2))



plt.figure(figsize=(15,4))
titles = ['面积','房龄','房间数']
for i in range(3):
    plt.subplot(2,3,i+1)
    plt.hist(x[:,i],bins=20,color='skyblue',edgecolor='black')
    plt.title(titles[i])
    plt.grid(True,alpha=0.3)
plt.tight_layout()
plt.show()

plt.figure(figsize=(15,4))
for i in range(3):
    plt.subplot(2,3,i+1)
    plt.scatter(x[:i],y,alpha=0.6,c='orange')
    plt.xlabel(titles[i])
    plt.ylabel('房价')
    plt.grid(True,alpha=0.3)
plt.tight_layout()
plt.show()





















