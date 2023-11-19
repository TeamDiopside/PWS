import json
import os
import random

import numpy


def create_file(name):
    # alle hidden layers op volgorde, eerste is input, laatste is output, getallen = aantal nodes in layer
    layers = [9, 5, 5, 2]

    # lijst voor alle weight matrices
    weights: list = []
    biases: list = []

    # maken van weights matrices
    for x in range(len(layers) - 1):
        weights.append(create_random_weights(layers[x + 1], layers[x]))
        biases.append(create_random_biases(layers[x]))

    output_network_to_file(weights, biases, name, 0)
    print("Done!")


def create_random_weights(height, width):
    matrix = []  # lege matrix maken
    for x in range(height):
        lijst = []  # voor elke rij van de matrix een nieuwe lijst maken (voor de kolom)
        for y in range(width):
            lijst.append(random.random() * 2 - 1)  # de lijst vullen met random nummers
        matrix.append(lijst)  # de lijst in de matrix doen

    return matrix


def create_random_biases(length):
    matrix = []
    for x in range(length):
        matrix.append(random.random() * 2 - 1)  # de lijst vullen met random nummers

    return matrix


def calculate(all_weights, all_biases, inputs):
    # uitrekenen van layers achter elkaar
    for w, weight in enumerate(all_weights):
        inputs = numpy.matmul(weight, inputs)  # voor elke weight matrix de nieuwe inputs berekenen
        for n, number in enumerate(inputs):
            inputs[n] = sigmoid(number + all_biases[w][n])  # alles door de sigmoid functie halen
    return inputs


def change_weights(all_weights: list[list[list]], max_change):
    new_weights = []
    for x in all_weights:
        list1 = []
        for y in x:
            list2 = []
            for z in y:
                list2.append(z + (random.random() * 2 - 1) * max_change)
            list1.append(list2)
        new_weights.append(list1)

    return new_weights


def change_biases(all_biases, max_change):
    new_biases = []
    for x in all_biases:
        list1 = []
        for y in x:
            list1.append(y + (random.random() * 2 - 1) * max_change)
        new_biases.append(list1)
    return new_biases


# weights naar json format veranderen en in een file zetten
def output_network_to_file(weights, biases, name, generation):
    string = json.dumps([weights, biases], indent=2)
    if not os.path.exists(f"data/{name}"):
        os.makedirs(f"data/{name}")
    file = open(f"data/{name}/{generation}.json", "w")
    file.write(string)
    file.close()


# weights van een json file omzetten naar matrix
def get_network_from_file(name, generation):
    file = open(f"data/{name}/{generation}.json")
    network = json.loads(file.read())
    file.close()
    return network[0], network[1]


def sigmoid(x):
    return 1 / (1 + numpy.exp(-x))


def test():
    pass


if __name__ == '__main__':
    create_file(input("Generation name: "))
