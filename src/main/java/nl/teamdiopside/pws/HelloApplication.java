package nl.teamdiopside.pws;

import javafx.application.Application;
import javafx.scene.Scene;
import javafx.scene.layout.Pane;
import javafx.scene.paint.Color;
import javafx.scene.shape.*;
import javafx.stage.Stage;

public class HelloApplication extends Application {
    @Override
    public void start(Stage primaryStage) throws InterruptedException {
        Pane pane = new Pane();

        // Pat
        Path path = new Path();
        path.setStroke(Color.BLUE); // Stroke color

        // Wat doet grafriek
        double startT = 0;
        double endT = 100;
        double increment = 0.1;

        for (double t = startT; t <= endT; t += increment) {

            double x = functionX(t);
            double y = functionY(t);

            // Hier moeten de coordinaten op het scherm passen, dat werkt nog niet
            double screenX = x * 16 + 1000;
            // -9 want y werkt van boven naar beneden en dat willen we niet
            double screenY = y * -9 + 1000;

            // maak lijntje
            if (t == startT) {
                path.getElements().add(new MoveTo(screenX, screenY));
            } else {
                path.getElements().add(new LineTo(screenX, screenY));
            }
        }

        pane.getChildren().add(path);
        Scene scene = new Scene(pane, 1920, 1080);
        primaryStage.setScene(scene);
        primaryStage.setTitle("Tytol");
        primaryStage.show();
    }

    public double functionX(double t) {
        return Math.cos(t);
    }

    public double functionY(double t) {
        return Math.sin(t);
    }

    public static void main(String[] args) {
        launch();
    }
}