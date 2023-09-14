package nl.teamdiopside.pws;

public class Neuron {

    public double[] weights;
    public double bias;

    public Neuron(double[] weights, double bias) {
        this.weights = weights;
        this.bias = bias;
    }

    public double feedForward(double[] x) {
        return sigmoid(dotProduct(x, weights) + bias);
    }
    
    public static double sigmoid(double f) {
        return 1 / (1 + Math.exp((-f)));
    }

    public static double dotProduct(double[] x, double[] y) {
        if (x.length != y.length)
            throw new RuntimeException("Arrays must be same size");
        double sum = 0;
        for (int i = 0; i < x.length; i++)
            sum += x[i] * y[i];
        return sum;
    }

    public static void main(String[] args) {
        double[] inputs = {0.3, 0.7, 0.01};
        double[] weights = {0.1, 0.3, 0.9};
        double a = new Neuron(weights, 0).feedForward(inputs);
        System.out.println(a);
    }
}
