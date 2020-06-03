from collections import defaultdict
from random import uniform
from math import sqrt
import random
import time

import numpy as np
np.set_printoptions(suppress=True)
np.set_printoptions(precision=30)
import mvhe

#读取待聚类数据集
def read_points(filename):
    # dataset = []
    # with open('data.txt', 'r') as file:
    #     for line in file:
    #         if line == '\n':
    #             continue
    #         dataset.append(list(map(float, line.split(' '))))
    #     file.close()
    #     return dataset
    dataset = np.loadtxt(filename)
    return  dataset

#保存结果
def write_vhe_results(listResult, dataset, k):
    with open('vhe_result.txt', 'a') as file:
        for kind in range(k):
            file.write("CLASSINFO:%d\n" % (kind + 1))
            for j in listResult[kind]:
                file.write('%d\n' % j)
            file.write('\n')
        file.write('\n\n')
        file.close()

#加密待聚类数据集
def data_enc(dataset):
    enc_dataset = np.zeros((row, col + K), dtype=object)
    for i in range(row):
        enc_dataset[i] = mvhe.encrypt(T, Mt, dataset[i])

    return enc_dataset

#随机选取初始的k个聚类中心
def enc_generate_k(enc_dataset, k):
    # index = random.sample(range(0, len(enc_dataset)), k)
    # index = [220, 306, 205, 78, 140]
    # index = [171862, 157497, 31685, 124181, 23427, 176867, 50030, 128388, 178321, 166611]
    # index = [1018129, 4542716, 2692724, 1822511, 1557532, 3727009, 2730432]
    if k == 3:
        index = [2260993, 4303383, 3096846]
    elif k == 4:
        index = [893516, 1322327, 2966729, 3752031]
    elif k == 5:
        index = [2132770, 2700825, 1347190, 250085, 746037]
    elif k == 6:
        index = [4111447, 277213, 496653, 4304035, 4597082, 3829727]
    elif k == 7:
        index = [1018129, 4542716, 2692724, 1822511, 1557532, 3727009, 2730432]
    elif k == 8:
        index = [1143467, 2476951, 4211734, 4793215, 4136995, 3042230, 2971447, 2914474]
    elif k == 9:
        index = [3136863, 3675507, 1686115, 1079662, 1796439, 1768544, 996955, 1396508, 3320551]
    elif k == 10:
        index = [1446369, 338845, 4422376, 276898, 1123113, 351070, 2906918, 954396, 4872747, 1634534]
    centers = [enc_dataset[i] for i in index]
    return centers

#计算距离
def enc_disatance(a, b):
    # dimension = len(a)
    # sum = 0
    # for i in range(dimension):
    #     sq = (a[i] - b[i]) ** 2
    #     sum += sq
    # return sqrt(sum)
    # print((a-b).T)
    # print(H)
    # print(a-b)
    # print(((a-b).T.dot(H).dot(a-b))/(mvhe.w**2))
    return ((a-b).T.dot(H).dot(a-b))/(mvhe.w**2)

#为每个点分配标签
def enc_assign_points(enc_dataset, centers):
    assignments = []
    for point in enc_dataset:
        shortest = float('inf')
        shortest_index = 0
        for i in range(len(centers)):
            value = enc_disatance(point, centers[i])
            if value < shortest:
                shortest = value
                shortest_index = i
        assignments.append(shortest_index)

    if len(set(assignments)) < len(centers):
        print("\n--!!!产生随机数错误，请重新运行程序!!!--\n")
        exit()
    return assignments

#计算k个聚类中点个数的最小公倍数，LCM=(n1,n2,...,nk), nj为每个聚类的点的个数
# def LCM(num):
#     size = len(num)
#     idx = 1
#     i = num[0]
#     while idx < size:
#         j = num[idx]
#         # 用辗转相除法求i,j的最大公约数m
#         b = i if i < j else j  # i，j中较小那个值
#         a = i if i > j else j  # i,j中较大那个值
#         r = b  # a除以b的余数
#         while(r != 0):
#             r = a % b
#             if r != 0:
#                 a = b
#                 b = r
#         lcm = i*j/b  # 两个数的最小公倍数
#         i = lcm
#         idx += 1
#     return lcm

#产生新的聚类中心
def enc_update_centers(enc_dataset, assignments, k):
    new_means = defaultdict(list)
    centers = []
    for assignment, point in zip(assignments, enc_dataset):
        new_means[assignment].append(point)

    # num = [0 for i in range(k)]
    # for j in range(k):
    #     for i in range(len(enc_dataset)):
    #         if assignments[i] == j:
    #             num[j] += 1
    # lcm = LCM(num)

    for i in range(k):
        points = new_means[i]
        centers.append(point_avg(points))

    return centers

#聚类中的点求均值
def point_avg(points):
    # enc_avg = np.zeros((1, col + K), dtype=object)
    # for p in points:
    #     enc_avg = mvhe.addVector(enc_avg, p)
    # enc_avg = env_avg/len(points)
    # return enc_avg
    dimensions = len(points[0])
    new_center = []
    for dimension in range(dimensions):
        sum = 0
        for p in points:
            sum += p[dimension]
        new_center.append(float("%.8f" % (sum / float(len(points)))))
    return new_center

def vhe_kmeans(dataset,k):
    enc_dataset = data_enc(dataset)
    k_point = enc_generate_k(enc_dataset, k)
    assignments = enc_assign_points(enc_dataset, k_point)
    print(assignments)
    print(k_point)
    old_assignments = None
    num = [0 for i in range(k)]
    iteration = 0
    while assignments != old_assignments:
        interval_start = time.time()

        new_centers = enc_update_centers(enc_dataset, assignments, k)
        old_assignments = assignments
        assignments = enc_assign_points(enc_dataset, new_centers)
        iteration += 1

        interval_end = time.time()
        print(iteration, ' ', (interval_end - interval_start)/60, 'min')

    dec_dataset = np.zeros((row, col), dtype=object)
    for i in range(row):
        dec_dataset[i] = mvhe.decrypt(S, enc_dataset[i])
        # print(dec_dataset[i])

    result = list(zip(assignments, dec_dataset))

    print('\n\n---------------------------------分类结果---------------------------------------\n\n')
    print('聚类中心：')
    new_centers = np.array(new_centers)
    dec_new_centers = np.zeros((k, col), dtype=object)
    for i in range(k):
        dec_new_centers[i] = mvhe.decrypt(S, new_centers[i])
    print(dec_new_centers)

    for j in range(k):
        for i in range(len(dataset)):
            if assignments[i] == j:
                num[j] += 1

    print('聚类点个数：')
    print(num)

    print('迭代次数：')
    print(iteration)

    res = open("vhe_clusters.txt", 'a+')
    print('聚类中心：', file=res)
    for i in range(k):
        print(dec_new_centers[i], file=res)
    print('\n\n')
    print('聚类点个数：', file=res)
    print(num, file=res)
    print('\n\n')
    print('迭代次数：', file=res)
    print(iteration, file=res)
    res.close()


    print('\n\n---------------------------------标号简记---------------------------------------\n\n')
    # for out in result:
    #     print(out, end='\n')
    print('\n\n---------------------------------聚类结果---------------------------------------\n\n')
    listResult = [[] for i in range(k)]
    count = 0
    for i in assignments:
        listResult[i].append(count)
        count = count + 1
    write_vhe_results(listResult, dec_dataset, k)
    for kind in range(k):
        print("第%d类数据有:" % (kind + 1))
        count = 0
        for j in listResult[kind]:
            # print(j, end=' ')
            count = count + 1
            # if count % 25 == 0:
            #     print('\n')
        print(count)
        print('\n')
    print('\n\n--------------------------------------------------------------------------------\n\n')


# 读取数据集
print("Load dataset...")
# dataset = read_points('CDR_Z.txt')
dataset = read_points('CDR_raw_2d_Z.txt')
dataset = np.array(dataset)
print("Dataset has %d items and %d dims" % (dataset.shape[0], dataset.shape[1]))
print(dataset[0])

# 参数设置
row = dataset.shape[0]
col = dataset.shape[1]
print(row, col)

K = 1
N = col
St, Mt = mvhe.getinvertiblematrix(N + K)
T = mvhe.getRandomMatrix(N, K, mvhe.tBound)
S = mvhe.getSecretKey(T, St)
H = np.dot(S.T, S)

def main():
    for i in range(2, 10):
        k = i + 1
        start = time.time()
        vhe_kmeans(dataset, k)
        end = time.time()
        print((end-start)/3600, 'hour')

        t = open("vhe_time.txt", 'a+')
        print((end - start) / 3600, 'hour', file=t)
        t.close()

    # start = time.time()
    # vhe_kmeans(dataset, 3)
    # end = time.time()
    # print((end - start) / 3600, 'hour')
    #
    # t = open("vhe_time_test.txt", 'a+')
    # print((end - start) / 3600, 'hour', file=t)
    # t.close()

    # k=5
    # print(dataset)
    # enc_dataset = data_enc(dataset)
    # print(enc_dataset)
    # k_point = enc_generate_k(enc_dataset, k)
    # print(k_point)
    # assignments = enc_assign_points(enc_dataset, k_point)
    # new_centers = enc_update_centers(enc_dataset, assignments, k)
    # print(len(new_centers[0]))





if __name__ == '__main__':
    main()

