import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

#取值范围：-2pi ～ 2pi，一共200个采样点
x = np.linspace(-2 * np.pi, 2 * np.pi, 200)

# 计算四条函数曲线
y1 = np.exp(x)
y2 = x**2
y3 = np.sin(3 * x)
y4 = np.cos(2 * x)

# 设置画布大小，让图像布局更整洁
plt.figure(figsize=(12, 7))

# 绘制四条曲线，要求颜色、线型、标记符号全部互不相同
plt.plot(x, y1, color='red', linestyle='-', marker='o', markersize=3, label='e^x')
plt.plot(x, y2, color='blue', linestyle='--', marker='s', markersize=3, label='x^2')
plt.plot(x, y3, color='green', linestyle='-.', marker='^', markersize=3, label='sin(3x)')
plt.plot(x, y4, color='purple', linestyle=':', marker='*', markersize=4, label='cos(2x)')

# 设置横纵坐标名称、图表总标题，并统一设置字体大小
plt.xlabel('x', fontsize=14)
plt.ylabel('y', fontsize=14)
plt.title('作业', fontsize=18, fontweight='bold')

# 统一设置坐标轴刻度字体大小
plt.tick_params(axis='both', which='major', labelsize=12)

# 开启网格线，设置为浅色虚线
plt.grid(True, linestyle='--', color='lightgray', alpha=0.7)

# 自定义图例位置
plt.legend(loc='upper right', fontsize=12)

# 限定x轴、y轴显示范围，让图像布局更整洁
plt.xlim(-2 * np.pi, 2 * np.pi)
plt.ylim(-2, 15)

plt.show()