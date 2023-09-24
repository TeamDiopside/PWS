module nl.teamdiopside.pws {
    requires javafx.controls;
    requires javafx.fxml;

    requires org.controlsfx.controls;
    requires net.synedra.validatorfx;
    requires org.kordamp.bootstrapfx.core;
    requires ejml;

    opens nl.teamdiopside.pws to javafx.fxml;
    exports nl.teamdiopside.pws;
}