import random

import numpy as np


def main():
    layers = [2, 3]

    all_weights = [None] * (len(layers) - 1)

    # maken van weights matrices, nu nog compleet random vulling
    for x in range(len(all_weights)):
        weights = [[None] * layers[x]] * layers[x + 1]
        weights = make_weights(weights)
        all_weights[x] = weights

    # uitrekenen van layers achter elkaar
    inputs = [0.3, 0.7]
    for w in all_weights:
        inputs = np.matmul(w, inputs)
    # print(inputs)


# matrix vullen met random
def make_weights(matrix):

    x_length = len(matrix)
    y_length = len(matrix[0])

    print(x_length, y_length)

    for x in range(x_length):
        for y in range(y_length):
            matrix[x][y] = random.random()
            print(f"{x}, {y}: {matrix[x][y]}")
            # print(array)
    print(matrix)
    return matrix


def test():
    a = [[1, 2, 3], [4, 5, 6]]

    for x in range(2):
        for y in range(3):
            a[x][y] = random.random()

    print(a)


if __name__ == '__main__':
    main()
