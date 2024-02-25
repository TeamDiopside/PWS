import json
import os
import random
from os import listdir

import numpy


def create_file():
    name = input("Generation name: ")
    layers = input("Network layers: ").split()
    layers = list(map(lambda num: int(num), layers))

    # lijst voor alle weight matrices
    weights: list = []
    biases: list = []

    # maken van weights matrices
    for x in range(len(layers) - 1):
        weights.append(create_random_weights(layers[x + 1], layers[x]))
        biases.append(create_random_biases(layers[x]))

    output_network_to_file(weights, biases, layers, name, 0)
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


# Verander de weights van de vorige generatie een klein beetje en hoop dat de auto beter is dan de vorige
def change_weights(all_weights: list[list[list]], max_change):
    new_weights = []
    for x in all_weights:
        list1 = []
        for y in x:
            list2 = []
            for z in y:
                list2.append(z + numpy.random.normal(0, max_change))
            list1.append(list2)
        new_weights.append(list1)

    return new_weights


# Verander de biases van de vorige generatie een klein beetje en hoop dat de auto beter is dan de vorige
def change_biases(all_biases, max_change):
    new_biases = []
    for x in all_biases:
        list1 = []
        for y in x:
            list1.append(y + numpy.random.normal(0, max_change))
        new_biases.append(list1)
    return new_biases


# weights naar json format veranderen en in een file zetten
def output_network_to_file(weights, biases, layers, name, generation):
    string = json.dumps([weights, biases, layers, "Generation " + name, generation], indent=2)
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

    try:
        layers = network[2]
    except IndexError:
        layers = [9, 5, 5, 2]

    return network[0], network[1], layers


def get_highest_gen(name):
    file_names = [int(f.removesuffix(".json")) for f in listdir(f"data/{name}")]
    highest = 0
    for gen in file_names:
        highest = max(highest, gen)
    return highest


def calculate(all_weights, all_biases, inputs):
    # uitrekenen van layers achter elkaar
    for w, weight in enumerate(all_weights):
        inputs = numpy.matmul(weight, inputs)  # voor elke weight matrix de nieuwe inputs berekenen
        for n, number in enumerate(inputs):
            inputs[n] = sigmoid(number + all_biases[w][n])  # alles door de sigmoid functie halen
    return inputs


def sigmoid(x):
    return 1 / (1 + numpy.exp(-x))


if __name__ == '__main__':
    create_file()
