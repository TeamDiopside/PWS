import math
import random

import numpy as np


def main():
    layers = [2, 3, 4, 1]

    all_weights = [0] * (len(layers) - 1)

    # maken van weights matrices, nu nog compleet random vulling
    for x in range(len(all_weights)):
        weights = create_random_matrix(layers[x + 1], layers[x])
        all_weights[x] = weights

    # uitrekenen van layers achter elkaar
    inputs = [0.3, 0.2]
    print(inputs)
    for weight in all_weights:
        inputs = np.matmul(weight, inputs)
        for x in range(len(inputs)):
            inputs[x] = sigmoid(inputs[x])
        print(inputs)
    print(inputs[0] - 0.5)


def create_random_matrix(height, width):
    matrix = []
    for x in range(height):
        lijst = []
        for y in range(width):
            lijst.append(random.random())
        matrix.append(lijst)

    return matrix


def sigmoid(x):
    return 1 / (1 + math.exp(-x))


def test():
    pass


if __name__ == '__main__':
    main()
