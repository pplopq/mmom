import os
# 1. 屏蔽 TensorFlow 的 Info 和 Warning 日志 (只显示 Error)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
# 2. 禁用 oneDNN 优化提示
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
# 3. 屏蔽 Python 的 FutureWarning 和 UserWarning
import warnings
warnings.filterwarnings('ignore')

import tensorflow as tf
from tensorflow.keras import layers,models
import numpy as np

(x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()  #加载并预处理mnist数据集
x_train,x_test = x_train / 255.0,x_test / 255.0
model = tf.keras.models.Sequential([
    layers.Flatten(input_shape=(28,28)),  #输入层“将 28x28 的矩阵直接“拉伸”为长度为 784 (28*28) 的一维向量。”
    layers.Dense(128, activation='relu'),  #全连接层
    layers.Dropout(0.2),    #设置dropout率“随机丢弃20%神经元”
    layers.Dense(256,activation='relu'),
    layers.Dropout(0.2),
    layers.Dense(10, activation='softmax')  #输出层“10个输出维度，softmax激活函数”
                                    ])
model.summary()  #输出模型详细结构信息
#编译模型，定义“如何学习”
model.compile(optimizer='adam',   #优化器
              loss='sparse_categorical_crossentropy',  #损失函数
              metrics=['accuracy']   #评估指标“准确率”
              )
history = model.fit(x_train,y_train,epochs = 5)
model.save('mnist_model.keras')
test_loss, test_acc = model.evaluate(x_test, y_test, verbose=2)
predictions = model.predict(x_test[:5])
for i in range(5):
    predicted_digit = np.argmax(predictions[i])
    true_digit = y_test[i]
    print(f"样本 {i+1}: 预测 = {predicted_digit}, 真实 = {true_digit}")