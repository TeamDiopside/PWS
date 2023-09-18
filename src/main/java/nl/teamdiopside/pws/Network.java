package nl.teamdiopside.pws;

import org.ejml.simple.SimpleMatrix;

public class Network {

    public static void main(String[] args) {
        doStuff();
    }

    // simpel netwerk
    // 2 inputs
    // 3 outputs
    public static void doStuff() {
        double[][] weightsArray = { {0.1, 0.2, 0.3}, {0.4, 0.5, 0.6} };
        double[] inputsArray = {0.4, 0.6};

        SimpleMatrix weights = new SimpleMatrix(weightsArray);
        SimpleMatrix inputs = new SimpleMatrix(inputsArray);
        SimpleMatrix output = weights.mult(inputs);

        System.out.println(output.get(0, 0));
        System.out.println(output.get(1, 0));
    }

    public static double sigmoid(double f) {
        return 1 / (1 + Math.exp((-f)));
    }
}

