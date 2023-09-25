import math
import random

import numpy


def main():
    # alle hidden layers op volgorde, eerste is input, laatste is output, getallen = aantal nodes in layer
    layers = [2, 3, 4, 1]

    # lijst voor alle weight matrices
    all_weights: list = [0] * (len(layers) - 1)

    # maken van weights matrices
    for x in range(len(all_weights)):
        weights = create_random_matrix(layers[x + 1], layers[x])
        all_weights[x] = weights

    # uitrekenen van layers achter elkaar
    inputs = [0.3, 0.2]
    print(inputs)
    for weight in all_weights:
        inputs = numpy.matmul(weight, inputs)  # voor elke weight matrix de nieuwe inputs berekenen
        for x in range(len(inputs)):
            inputs[x] = sigmoid(inputs[x])  # alles door de sigmoid functie halen
        print(inputs)
    print(inputs[0])


def create_random_matrix(height, width):
    matrix = []  # lege matrix maken
    for x in range(height):
        lijst = []  # voor elke rij van de matrix een nieuwe lijst maken (voor de kolom)
        for y in range(width):
            lijst.append(random.random())  # de lijst vullen met random nummers
        matrix.append(lijst)  # de lijst in de matrix doen

    return matrix


# niemand die weet waarom dit zo is
def sigmoid(x):
    return 1 / (1 + math.exp(-x))


def test():
    pass


if __name__ == '__main__':
    main()
