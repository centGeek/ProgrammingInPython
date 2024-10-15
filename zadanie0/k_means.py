"""K-means clustering using pure Python.

This program is intended to group multidimensional data using the k-means
clustering algorithm. The data should be supplied as a CSV file. The clusters
are determined based on the normalized data. The program reports cluster sizes,
the number of algorithm iterations, and the final within-cluster sum of
squares.
"""

# normalize data once during data loading
# more descriptive names: temp are not accurate
# variable hardly encoded kmeans(3). Make this a global_variable


import csv
import math
import random


def load_data(file, data):
    data_reader = csv.reader(file)
    for row in data_reader:
        data.append(list(map(float, row)))


def distance_two_dimension(point_one, point_two):
    return math.sqrt((point_one[0] - point_two[0]) **
                     2 + (point_one[1] - point_two[1]) ** 2)


def normalize(data):
    # transposition of data to get min and max values
    x_coords, y_coords = zip(*data)
    minx = min(x_coords)
    maxx = max(x_coords)
    miny = min(y_coords)
    maxy = max(y_coords)
    normalized_data = [((x - minx) / (maxx - minx), (y - miny) / (maxy - miny))
                       for x, y in data]
    return normalized_data


def initialize_centers(n_centers, data):
    return random.sample(data, n_centers)


def assign_clusters(centers, data):
    labels = []
    wcss = 0.0
    for point in data:
        dists = [distance_two_dimension(point, center) for center in centers]
        min_dist = min(dists)
        labels.append(dists.index(min_dist))
        wcss += min_dist ** 2
    return labels, wcss


def calc_new_centers(n_clusters, labels, data):
    new_centers = []

    clusters = [[] for _ in range(n_clusters)]

    for loc, point in zip(labels, data):
        clusters[loc].append(point)
    for cluster in clusters:
        sumx, sumy = 0, 0
        for point in cluster:
            sumx += point[0]
            sumy += point[1]
        sumx /= len(cluster)
        sumy /= len(cluster)
        new_centers.append([sumx, sumy])
    return new_centers


def kmeans(n_clusters, data):
    data = normalize(data)
    centers = initialize_centers(n_clusters, data)
    old_labels = None
    n_iters = 0
    wcss = 0
    while True:
        n_iters += 1
        labels, wcss = assign_clusters(centers, data)
        if labels == old_labels:
            break
        centers = calc_new_centers(n_clusters, labels, data)
        old_labels = labels
    return labels, wcss, n_iters


def kmeans_print(n_clusters, data):
    labels, wcss, n_iters = kmeans(n_clusters, data)
    print("Cluster sizes:")
    for c in range(3):
        print(f"{c + 1} -", labels.count(c))
    print("Iterations:", n_iters)
    print("WCSS:", wcss)


# main body

file_csv = open("data.csv", newline="")
data_csv = []
load_data(file_csv, data_csv)
kmeans_print(3, data_csv)
file_csv.close()
