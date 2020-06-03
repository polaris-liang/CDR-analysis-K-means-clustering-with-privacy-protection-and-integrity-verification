# coding=utf-8

from collections import defaultdict
from random import uniform
from math import sqrt
import random
import time


def read_points():
    dataset = []
    with open('CDR_raw_2d_Z.txt', 'r') as file:
        for line in file:
            if line == '\n':
                continue
            dataset.append(list(map(float, line.split(' '))))
        file.close()
        return dataset


def write_results(listResult, dataset, k):
    with open('result.txt', 'a') as file:
        for kind in range(k):
            file.write("CLASSINFO:%d\n" % (kind + 1))
            for j in listResult[kind]:
                file.write('%d\n' % j)
            file.write('\n')
        file.write('\n\n')
        file.close()


def point_avg(points):
    dimensions = len(points[0])
    new_center = []
    for dimension in range(dimensions):
        sum = 0
        for p in points:
            sum += p[dimension]
        new_center.append(float("%.8f" % (sum / float(len(points)))))
    return new_center


def update_centers(data_set, assignments, k):
    new_means = defaultdict(list)
    centers = []
    for assignment, point in zip(assignments, data_set):
        new_means[assignment].append(point)
    for i in range(k):
        points = new_means[i]
        centers.append(point_avg(points))
    return centers


def assign_points(data_points, centers):
    assignments = []
    sse = 0
    for point in data_points:
        shortest = float('inf')
        shortest_index = 0
        for i in range(len(centers)):
            value = distance(point, centers[i])
            if value < shortest:
                shortest = value
                shortest_index = i
        assignments.append(shortest_index)
        sse = (sse + value**2)

    if len(set(assignments)) < len(centers):
        print("\n--!!!产生随机数错误，请重新运行程序!!!--\n")
        exit()
    return assignments, sse


def distance(a, b):
    dimention = len(a)
    sum = 0
    for i in range(dimention):
        sq = (a[i] - b[i]) ** 2
        sum += sq
    return sqrt(sum)



# def generate_k(data_set, k):
#     centers = []
#     dimentions = len(data_set[0])
#     min_max = defaultdict(int)
#     for point in data_set:
#         for i in range(dimentions):
#             value = point[i]
#             min_key = 'min_%d' % i
#             max_key = 'max_%d' % i
#             if min_key not in min_max or value < min_max[min_key]:
#                 min_max[min_key] = value
#             if max_key not in min_max or value > min_max[max_key]:
#                 min_max[max_key] = value
#     for j in range(k):
#         rand_point = []
#         for i in range(dimentions):
#             min_val = min_max['min_%d' % i]
#             max_val = min_max['max_%d' % i]
#             tmp = float("%.8f" % (uniform(min_val, max_val)))
#             rand_point.append(tmp)
#         centers.append(rand_point)
#     return centers

def generate_k(data_set, k):
    # index = random.sample(range(0, len(data_set)), k)
    # print(index)
    # index = [171862, 157497, 31685, 124181, 23427, 176867, 50030, 128388, 178321, 166611]
    # index = [2178983, 1131104, 1746965, 3077838, 1393468, 2097277, 1245010, 2033247, 2231154, 305355]

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

    centers = [data_set[i] for i in index]
    print(centers)
    return centers


def k_means(dataset, k):
    k_points = generate_k(dataset, k)
    assignments, sse = assign_points(dataset, k_points)
    print(assignments)
    old_assignments = None
    num = [0 for i in range(k)]
    iteration = 0
    while assignments != old_assignments:
        interval_start = time.time()

        new_centers = update_centers(dataset, assignments, k)
        old_assignments = assignments
        assignments, sse = assign_points(dataset, new_centers)
        iteration +=1

        interval_end = time.time()
        print(iteration, ' ', (interval_end - interval_start) / 60, 'min')

    result = list(zip(assignments, dataset))
    print('\n\n---------------------------------分类结果---------------------------------------\n\n')
    print('聚类中心：')
    print(new_centers)

    for j in range(k):
        for i in range(len(dataset)):
            if assignments[i] == j:
                num[j] += 1

    print('聚类点个数：')
    print(num)

    print('Sum Square Error:')
    print(sse)

    print('迭代次数：')
    print(iteration)

    res = open("clusters.txt", 'a+')
    print('聚类中心：', file=res)
    for i in range(k):
        print(new_centers[i], file=res)
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
    write_results(listResult, dataset, k)
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


def main():
    dataset = read_points()
    # start = time.time()
    # k_means(dataset, 4)
    # end = time.time()
    # print((end - start) / 3600, 'hour')
    # t = open("time.txt", 'a+')
    # print((end - start) / 3600, 'hour', file=t)
    # t.close()

    for i in range(2, 10):
        k = i + 1
        start = time.time()
        k_means(dataset, k)
        end = time.time()
        print((end-start)/3600, 'hour')

        t = open("time.txt", 'a+')
        print((end - start) / 3600, 'hour', file=t)
        t.close()


if __name__ == "__main__":
    main()