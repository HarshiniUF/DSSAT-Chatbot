import FileXService.IrrigationService;
import FileXModel.FileX;
import FileXModel.Irrigation;
import FileXModel.IrrigationApplication;

import java.io.File;

public class TestIrrigationService {
    public static void main(String[] args) {
        if (args.length != 1) {
            System.out.println("Usage: java TestIrrigationService <path_to_file>");
            return;
        }

        String filePath = args[0];
        File file = new File(filePath);

        // Initialize FileX static fields (VERY IMPORTANT!)
        FileX.NewFileX();

        // Read irrigations from file
        IrrigationService.Read(file);

        // Print out loaded irrigations
        System.out.println("=== Irrigations Loaded ===");
        for (int i = 0; i < FileX.irrigations.GetSize(); i++) {
            Irrigation irrig = (Irrigation) FileX.irrigations.GetAtIndex(i);
            System.out.println(
                "Level: " + irrig.GetLevel() +
                ", EFIR: " + irrig.EFIR +
                ", IDEP: " + irrig.IDEP +
                ", ITHR: " + irrig.ITHR +
                ", IEPT: " + irrig.IEPT +
                ", IOFF: " + irrig.IOFF +
                ", IAME: " + irrig.IAME +
                ", IAMT: " + irrig.IAMT +
                ", IRNAME: " + irrig.IRNAME
            );
            // Print applications
            for (int j = 0; j < irrig.GetSize(); j++) {
                IrrigationApplication app = irrig.GetApp(j);
                System.out.println("  Application: IDATE: " + app.IDATE +
                                   ", IDAY: " + app.IDAY +
                                   ", IROP: " + app.IROP +
                                   ", IRVAL: " + app.IRVAL);
            }
        }
    }
}
