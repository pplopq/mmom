import tensorflow as tf
from tensorflow.keras import layers,models
from tensorflow.keras.datasets import boston_housing


(x_train, y_train), (x_test, y_test) = boston_housing.load_data()

mean = x_train.mean(axis=0)
std = x_train.std(axis=0)

x_train = (x_train - mean) / std
x_test = (x_test - mean) / std

model = models.Sequential([
    layers.Dense(64, activation='relu', input_shape=(13,)),
    layers.Dropout(0.2),
    layers.Dense(64, activation='relu'),
    layers.Dropout(0.2),
    layers.Dense(64, activation='relu'),
    layers.Dropout(0.2),
    layers.Dense(1)
])
model.summary()
model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
              loss='mse',
              metrics=['mse'])

history = model.fit(x_train,y_train,epochs = 100,batch_size =16,validation_split=0.2)

test_loss, test_mae = model.evaluate(x_test, y_test)
print(round(test_mae,2))
preds = model.predict(x_test).flatten()
for i in range(5):
    print(f"预测 = {preds[i]:.2f}, 真实 = {y_test[i]}")