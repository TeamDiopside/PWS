package nl.teamdiopside.pws;

import javafx.scene.transform.MatrixType;
import org.apache.commons.math3.linear.MatrixUtils;
import org.apache.commons.math3.linear.RealMatrix;

public class Network {

    public static void main(String[] args) {
        double[][] data = { {1}, {2} };
        double[][] data2 = { {3, 4} };
        RealMatrix matrix = MatrixUtils.createRealMatrix(data);
        RealMatrix matrix2 = matrix.multiply(MatrixUtils.createRealMatrix(data2));
        System.out.println(matrix2);
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
