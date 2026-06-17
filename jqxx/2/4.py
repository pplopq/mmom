import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

x = np.linspace(-2 * np.pi, 2 * np.pi, 200)

y1 = np.exp(x)
y2 = x ** 2
y3 = np.sin(3 * x)
y4 = np.cos(2 * x)

plt.figure(num=None, figsize=(10,6), dpi=100, facecolor='#f5f5f5',constrained_layout=True)

plt.plot(x, y1, color='red', linestyle='-', marker='o', markersize=3, label='e^x',alpha=0.5)
plt.plot(x, y2, color='blue', linestyle='--', marker='s', markersize=3, label='x^2',alpha=0.5)
plt.plot(x, y3, color='yellow', linestyle=':', marker='^', markersize=3, label='sin(3x)',alpha=0.5)
plt.plot(x, y4, color='green', linestyle='-.', marker='*', markersize=4, label='cos(2x)',alpha=0.5)
#调用legend()展示图例
plt.legend(loc='upper left', fontsize=12)
#设置横坐标名称、纵坐标名称、图表总标题
plt.title('作业', fontsize=18, fontweight='bold', pad=20)
plt.xlabel('x', fontsize=14)
plt.ylabel('y', fontsize=14)
#开启网格线，设置网格为浅色虚线
plt.grid(True,linestyle='--',color='grey',alpha=0.3)
#统一设置坐标轴字体、标题字体大小
plt.rcParams.update({
    'font.size': 12,             # 全局默认字体大小
    'axes.titlesize': 16,        # 标题大小
    'axes.labelsize': 14,        # 坐标轴名称大小
    'xtick.labelsize': 12,       # x轴刻度字体大小
    'ytick.labelsize': 12,       # y轴刻度字体大小
    'legend.fontsize': 12,       # 图例字体大小
    'figure.figsize': (10, 6),   # 默认图片大小
    'lines.linewidth': 2,        # 线条宽度
    'lines.markersize': 6        # 标记点大小
})
#限定x轴、y轴显示范围，让图像布局更整洁
plt.xlim(-2 * np.pi, 2 * np.pi)
plt.ylim(-2,200)
plt.show()


