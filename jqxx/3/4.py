from matplotlib import pyplot as plt
from sklearn.datasets import make_blobs
import numpy as np
from sklearn.cluster import KMeans

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 无监督
x2,_ = make_blobs(n_samples=500, centers=3, cluster_std=[0.5,1.0,1.5], random_state=42)

x2[:,0] = np.interp(x2[:,0],(x2[:,0].min(),x2[:,0].max()),(0,60))
x2[:,1] = np.interp(x2[:,1],(x2[:,1].min(),x2[:,1].max()),(0,90))

km = KMeans(n_clusters=3, random_state=42)
labels = km.fit_predict(x2)

print("无监督学习（聚类）结果")
print(f"聚类中心坐标：\n{km.cluster_centers_}")

centers = km.cluster_centers_
score = centers[:,0] + centers[:,1]
idx = np.argsort(score)
label_map = {idx[0]:"不运动",idx[1]:"运动小白",idx[2]:"运动达人"}

plt.figure(figsize=(9,6))
colors = ['red','green','orange']
for i in range(3):
    mask = labels==i
    plt.scatter(x2[mask,0],x2[mask,1],c=colors[i],alpha=0.7,label=label_map[i])

plt.scatter(km.cluster_centers_[:,0], km.cluster_centers_[:,1],
            c='red',marker='*',s=100,edgecolors='black',lw=1.2,label='聚类中心')

plt.xlabel("每月运动次数")
plt.ylabel("每次运动时长（分钟）")
plt.title("人群运动聚类（3类）")
plt.legend()
plt.show()