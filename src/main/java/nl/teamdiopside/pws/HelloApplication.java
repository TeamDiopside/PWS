package nl.teamdiopside.pws;

import javafx.application.Application;
import javafx.scene.Scene;
import javafx.scene.layout.Pane;
import javafx.scene.paint.Color;
import javafx.scene.shape.*;
import javafx.stage.Stage;

public class HelloApplication extends Application {
    @Override
    public void start(Stage primaryStage) {
        Pane pane = new Pane();

        // Pat
        Path path = new Path();
        path.setStroke(Color.BLUE); // Stroke color

        // Wat doet grafriek
        double startX = 1;
        double endX = 100;
        double increment = 0.1;

        for (double x = startX; x <= endX; x += increment) {

            double y = function(x);

            // Hier moeten de coordinaten op het scherm passen, dat werkt nog niet
            double screenX = x * 16 + 100;
            // -9 want y werkt van boven naar beneden en dat willen we niet
            double screenY = y * -9 + 100;

            // maak lijntje
            if (x == startX) {
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

    public double function(double x) {
        return x*x;
    }

    public static void main(String[] args) {
        launch();
    }
}