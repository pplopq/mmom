import tensorflow as tf
import numpy as np

# 1. 加载模型
model = tf.keras.models.load_model('mnist_model.keras')

# 2. 读取图片 (请确保图片名为 my_number.jpg)
img_path = 'number3.png'
img = tf.keras.utils.load_img(img_path, color_mode='grayscale', target_size=(28, 28))

# 3. 转换为数组并预处理
img_array = tf.keras.utils.img_to_array(img)
img_array = img_array / 255.0  # 归一化
img_array = 1 - img_array

# 4. 预测
# 注意：模型需要 [批次, 高, 宽, 通道] 的格式，所以我们要加一个维度
prediction = model.predict(np.expand_dims(img_array, axis=0))
digit = np.argmax(prediction)

print(f"模型认为这个数字是：{digit}")