import numpy
import tensorflow as tf
import torch
from IPython.core import history
from tensorflow.keras import layers,models

(x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()
model = tf.keras.models.Sequential([
    tf.keras.layers.Flatten(input_shape=(28, 28)),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.Dense(10, activation='softmax')
])
model.summary()
model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

history=model.fit(x_train, y_train, epochs=5)

test_loss, test_acc = model.evaluate(x_test, y_test, verbose=2)
print('\nTest accuracy:', test_acc)
predictions = model.predict(x_test[:5])
for i in range(5):
    p_label = tf.argmax(predictions[i])
