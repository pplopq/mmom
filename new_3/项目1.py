import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score

plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

a=pd.read_csv(r"C:\py-study\new_3\train.csv")
b=pd.read_csv(r"C:\py-study\new_3\test.csv")
#缺失值
a.isnull().sum()
m=['Location#Transportation','Location#Downtown','Location#Easy_to_find',
   'Service#Queue','Service#Hospitality','Service#Parking','Service#Timely',
   'Price#Level','Price#Cost_effective','Price#Discount',
   'Ambience#Decoration','Ambience#Noise','Ambience#Space','Ambience#Sanitary',
   'Food#Portion','Food#Taste','Food#Appearance','Food#Recommend']

x_train=a[m]
y_train=a['star']
x_test=b[m]
y_test=b['star']

scaler = StandardScaler()
x_train_scaled = scaler.fit_transform(x_train)
x_test_scaled = scaler.transform(x_test)

rf_model = RandomForestRegressor(
    n_estimators=1000,
    max_depth=15,
    random_state=42,
    n_jobs=-1
)
rf_model.fit(x_train_scaled, y_train)

y_pred = rf_model.predict(x_test_scaled)

mae = mean_absolute_error(y_test, y_pred)
print(f"平均绝对误差 (MAE): {mae:.4f}")

r2 = r2_score(y_test, y_pred)
print(f"R² 分数: {r2:.4f}")


plt.figure(figsize=(10, 6))
plt.scatter(y_test, y_pred, alpha=0.6, color='royalblue', edgecolors='white', s=60)
min_val = min(y_test.min(), y_pred.min())
max_val = max(y_test.max(), y_pred.max())
plt.plot(
    [min_val, max_val],
    [min_val, max_val],
    'r--',
    lw=2,
    label='Perfect Prediction'
)

plt.title(f'预测值 vs 真实值 (MAE: {mae:.4f}, R²: {r2:.4f})', fontsize=16)
plt.xlabel('真实评分 (True Star)', fontsize=12)
plt.ylabel('预测评分 (Predicted Star)', fontsize=12)
plt.legend()
plt.grid(True, linestyle='--', alpha=0.5)

plt.tight_layout()
plt.show()
