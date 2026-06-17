import matplotlib.pyplot as plt
import numpy as np
# x=np.array([1,2,3,4,new_3,6,7,8,9])
# plt.plot(x,x**2)
# plt.show()

# x=np.linspace(0,10,100)
# y1=np.sin(x)
# y2=np.cos(x)
# plt.figure(figsize=(new_3,new_3),dpi=100)
# plt.plot(x,y1,label="sin(x)",color="green",linestyle=':',marker='^')
# plt.plot(x,y2,label="cos(x)",color="red",linestyle='--',marker='^')
#
# plt.title("sinh")
# plt.xlabel("x"),plt.ylabel("y")
# plt.legend(),plt.grid(True,alpha=0.3)
# plt.show()
#



# plt.plot([1,2,3,4],[1,4,9,16])
# plt.show()
# plt.plot([1,2,3,4],[1,4,9,16],'go-.')
# plt.show()

# plt.figure(num=None, figsize=(10,new_3), dpi=80, facecolor='w', edgecolor='k')
# x=[1,2,3,4,new_3]
# y=[1,4,9,16,25]
# plt.rcParams['font.sans-serif']=['SimHei']
# plt.plot(x,y,color='red',linestyle='dashed',marker='o',markerfacecolor='blue',markersize=new_3,linewidth=new_3,alpha=0.new_3)
#
# plt.title('测试用图',fontsize=20,fontweight='bold',color='red',loc="center",pad=6.0)
# plt.xlabel('x',fontsize=20,fontweight='bold',color='red')
# plt.show()


plt.rcParams['font.sans-serif']=['SimHei']
x=[1,2,3,4]
y1=[1,4,9,16]
y2=[1,2,3,4]
plt.plot(x,y1,label='y=x^2')
plt.plot(x,y2,label='y=x')
plt.legend()
plt.title('测试用图',fontsize=20,fontweight='bold',color='red',loc='center',pad=10)

plt.show()

plt.rcParams['font.sans-serif']=['SimHei']
plt.rcParams['axes.unicode_minus']=False
x=np.linspace(0,10,100)
y1=np.sin(x)
y2=np.sin(x)
plt.figure()




