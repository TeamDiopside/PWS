import json
import math
import random

import numpy


def main(inputs, cycle):
    # alle hidden layers op volgorde, eerste is input, laatste is output, getallen = aantal nodes in layer
    layers = [2, 2]

    # lijst voor alle weight matrices
    all_weights: list = [0] * (len(layers) - 1)

    # maken van weights matrices
    if cycle == 1:
        for x in range(len(all_weights)):
            weights = create_random_matrix(layers[x + 1], layers[x])
            all_weights[x] = weights
    else:
        all_weights = get_weights_from_file("data/test.json")

    # uitrekenen van layers achter elkaar
    for weight in all_weights:
        inputs = numpy.matmul(weight, inputs)  # voor elke weight matrix de nieuwe inputs berekenen
        for x in range(len(inputs)):
            inputs[x] = sigmoid(inputs[x])  # alles door de sigmoid functie halen

    change_weights(all_weights, cycle)

    output_weights_to_file(all_weights, "data/test.json")
    return inputs


def create_random_matrix(height, width):
    matrix = []  # lege matrix maken
    for x in range(height):
        lijst = []  # voor elke rij van de matrix een nieuwe lijst maken (voor de kolom)
        for y in range(width):
            lijst.append(random.random())  # de lijst vullen met random nummers
        matrix.append(lijst)  # de lijst in de matrix doen

    return matrix


def change_weights(all_weights, cycle):
    max_change = 1 / cycle

    for x in range(len(all_weights)):
        for y in range(len(all_weights[x])):
            for z in range(len(all_weights[x][y])):
                all_weights[x][y][z] += (random.random() * 2 - 1) * max_change
                all_weights[x][y][z] = max(0, all_weights[x][y][z])
                all_weights[x][y][z] = min(1, all_weights[x][y][z])


# weights naar json format veranderen en in een file zetten
def output_weights_to_file(weights, file_name):
    string = json.dumps(weights, indent=2)
    file = open(file_name, "w")
    file.write(string)
    file.close()


# weights van een json file omzetten naar matrix
def get_weights_from_file(file_name):
    file = open(file_name)
    weights = json.loads(file.read())
    file.close()
    return weights


# niemand die weet waarom dit zo is
def sigmoid(x):
    return 1 / (1 + math.exp(-x))


def test():
    pass


if __name__ == '__main__':
    main([0.4, 0.6], 2)
    # test()
