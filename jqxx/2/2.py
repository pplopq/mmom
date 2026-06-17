import numpy as np

np.random.seed(10)
n=50
ids = np.arange(1,n+1)
math = np.clip(np.round(np.random.normal(75,15,n)),0,100).astype(int)
eng = np.clip(np.round(np.random.normal(75,12,n)),0,100).astype(int)
chine = np.clip(np.round(np.random.normal(75,15,n)),0,100).astype(int)
student = np.column_stack((ids,math,eng,chine))
student1 = np.column_stack((chine,math,eng))  #成绩

# #各科统计
# print("数学平均分：",np.mean(math),"数学最高分：",np.max(math),"数学最低分：",np.min(math))
# print("英语平均分：",np.mean(eng),"英语最高分：",np.max(eng),"英语最低分：",np.min(eng))
# print("语文平均分：",np.mean(chine),"语文最高分：",np.max(chine),"语文最低分：",np.min(chine))
#
# #每人的总分，平均分
student2=np.column_stack((ids,np.sum(student1,axis=1),np.mean(student1,axis=1)))
# for i in range(len(student2)):
#     print(f"id:{student2[i][0]:.0f}",f"总分：{student2[i][1]:.0f}",f"平均分：{student2[i][2]:.2f}")
#
# #总分最高的学生
# adj=np.argmax(np.sum(student1,axis=1))
# print(f"总分最高的学生{student[adj]}")
#
# #挂科学生
# mask = student1<60
# b=np.any(mask,axis=1)
#
# print("挂科学生")
# print(student[b])
#
# #按总分排名
# c=np.argsort(student2[:,1])[::-1]
# print("按总分排名")
# print(student[c])
#

#
# mask = (math >85) & (eng > 90)
# print(student[mask])
# print(math)
# new_math=np.clip(math,math+new_3,100)
# student3=np.column_stack((ids,new_math,eng,chine))
# print(student3)
