import numpy as np
# list_1d = [1,2,3,4,new_3]
# arr_1d = np.array(list_1d)
# print(arr_1d)
# list_2d = [[1,2,3],[4,new_3,6],[7,8,9]]
# arr_2d = np.array(list_2d)
# print(arr_2d)
# print(arr_2d.shape)  #形状
# print(arr_2d.ndim) #维度
# print(arr_2d.size) #元素总数
# print(arr_2d.dtype) #元素类型
#
# list_3d = [[[1,2,3],[4,new_3,6],[7,8,9]],[[10,11,12],[13,14,15],[16,17,18]],[[19,20,21],[22,23,24],[25,26,27]]]
#
# arr_3d = np.array(list_3d)
# print(arr_3d)

# print(np.ones((2,3)))  #创建指定形状的全是1数组
# print()
# print(np.zeros((2,3)))  #创建指定形状的全是0数组
# print()
# print(np.arange(1,6,2)) #生成指定步长的等差数列
# print()
# print(np.linspace(1,6,6)) #生产线性间隔的均匀数组
# print()
# print(np.full((2,3),4))  #创建填充特定数值的数组
# print()
# print(np.eye(3)) #创建指定大小的单位矩阵
# print()
# print(np.random.rand(2,3)) #生成【0，1）区间的随机浮点数数组


# arr = np.arange(12)
# print(arr)
# print(arr.reshape(3,4)) #变为3行4列
# print(arr.reshape(4,-1))  #自动计算
#
# print()
# arr = np.array([[1,2,3,4],[new_3,6,7,8]])
# print(arr)
# transposed = arr.T  #转置，行变列
# print(transposed)
#
# arr1 = np.array([[1,2],[3,4]])
# arr2 = np.array([[new_3,6],[7,8]])
#
# print(np.concatenate((arr1,arr2),0))  #垂直拼接
# print(np.concatenate((arr1,arr2),1))  #水平拼接


# grades = np.array([[78,83,92],[94,63,83]])
# print(grades.mean()) #平均分
# print(grades.std()) #标准差
# print(grades.min())
# print(grades.max())
# print(grades.sum()) #求和
# print(grades.mean(axis=0)) #按列平均分
# print(grades.mean(axis=1)) #按行平均分


# a=np.random.randint(0,100,(2,new_3,3))
# print(a)
#
# print("每个班级平均分：",np.mean(a,axis=(1,2)))
# print("每个班级每门课平均分：",np.mean(a,axis=(1)))
# print("没门课中位数：",np.median(a,axis=1))
# print("每个学生最低分：",np.min(a,axis=2))
# print("每个学生最高的分：",np.max(a,axis=2))


# arr=np.array([[1,2,3,4],[new_3,6,7,8],[9,10,11,12]])
# print(arr[1,2])
# print(arr[0])
# print(arr[:,1])
# print(arr[:2,2:])

# a=np.random.randint(0,100,(2,new_3,3))
# print(a)
# print("班级1的全部数据：",a[0])
# print()
# print("所有班级第3个学生：",a[:,2])
# print()
# print("最后一个班级后2个学生前2门课：",a[-1,-2:,:2])
# print()
# print("所有班级的最后一门课",a[:,-1])


# grades = np.array([[29,31,12,31],[23,34,87,65]])
# mask =grades>=30
# print(mask)
# high =grades[mask]
# print(high)
#
# adj=np.where(grades<30,30,grades)
# print(adj)
# indices = np.where(adj>=35)
# print(indices)


# a=np.random.randint(0,100,(2,new_3,3))
# print(a)
# adj=np.where(a[0]>85)
# print(a[0][adj])
#
# adj1=np.where(a>=90,'优秀',np.where(a<60,'不及格','及格'))
# print(adj1)
# mask = adj1=='不及格'
# b=np.any(mask,axis=2)
# print(b)
# print(a[b])


arr1=np.array([1,2,3,4,5,6,7,8,9,10,11,12,13,14,15])
arr2=np.array([1,2,3,4,5,6,7,8,9,10,11,12,13,14,15])
arr3=np.array([[1,2,3],[4,5,6],[7,8,9]])
arr4=np.array([[1,2,3],[4,5,6],[7,8,9]])
print(arr1+arr2)
print(arr3+arr4)








