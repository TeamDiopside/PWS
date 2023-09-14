package nl.teamdiopside.pws;

public class Network {

    public static void main(String[] args) {
        double[] weights = {0.1, 0.1, 0.1};
        Neuron neuron = new Neuron(weights, -2);

        double[] inputs = {0.1, 0.1, 0.1};

        double output = neuron.feedForward(new double[]{neuron.feedForward(inputs), neuron.feedForward(inputs), neuron.feedForward(inputs)});
        System.out.println(output);
    }

}

/*
 * voor elke laag is er een matrix
 * een vierkante voor de weights
 *  - rijen: alle weights die naar 1 neuron gaan
 *  - kolommen: weights van alle neurons
 * keer een vector voor alle komende neurons
 * plus een vector voor de weight van elk komend neuron
 *
 */
