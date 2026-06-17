import tensorflow as tf
import numpy as np
import cv2

# 1. 加载模型
model = tf.keras.models.load_model('mnist_model.keras')

# 2. 读取图片
img_path = 'number1.png'
# 读取为灰度图
img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)

# 3. 【关键步骤】暴力二值化
# 设定一个阈值（比如 200），大于 200 的全变成 255 (白)，小于的全变成 0 (黑)
# 这样可以彻底去除背景噪点
_, img_binary = cv2.threshold(img, 200, 255, cv2.THRESH_BINARY)

# 4. 【关键步骤】强制反转
# 现在 img_binary 是 白底(255) 黑字(0)
# 我们需要把它变成 黑底(0) 白字(255)
img_final = 255 - img_binary

# new_3. 缩放并居中
# 缩放到 20x20 (留出边缘)
img_resized = cv2.resize(img_final, (20, 20))

# 创建一个 28x28 的全黑画布
canvas = np.zeros((28, 28), dtype=np.uint8)

# 把 20x20 的数字贴到画布中间 (4:24, 4:24)
canvas[4:24, 4:24] = img_resized

# 6. 归一化
final_img = canvas.astype('float32') / 255.0

# 7. 预测
prediction_input = np.expand_dims(final_img, axis=0)
prediction = model.predict(prediction_input)
digit = np.argmax(prediction)
confidence = np.max(prediction)

print(f"模型认为这个数字是：{digit}")
print(f"置信度：{confidence:.4f}")