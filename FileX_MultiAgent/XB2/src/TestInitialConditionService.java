import FileXService.InitialConditionService;
import FileXModel.FileX;
import FileXModel.InitialCondition;
import FileXModel.InitialConditionApplication;

import java.io.File;

public class TestInitialConditionService {
    public static void main(String[] args) {
        if (args.length != 1) {
            System.out.println("Usage: java TestInitialConditionService <path_to_file>");
            return;
        }

        String filePath = args[0];
        File file = new File(filePath);

        // Initialize FileX static fields (VERY IMPORTANT!)
        FileX.NewFileX();

        // Read initial conditions from file
        InitialConditionService.Read(file);

        // Print out loaded initial conditions
        System.out.println("=== Initial Conditions Loaded ===");
        for (int i = 0; i < FileX.initialList.GetSize(); i++) {
            InitialCondition init = (InitialCondition) FileX.initialList.GetAtIndex(i);
            System.out.println("Level: " + init.GetLevel() +
                               ", PCR: " + init.PCR +
                               ", ICDAT: " + init.ICDAT +
                               ", ICRT: " + init.ICRT +
                               ", ICND: " + init.ICND +
                               ", ICNAME: " + init.ICNAME);

            // Print applications
            for (int j = 0; j < init.GetSize(); j++) {
                InitialConditionApplication app = init.GetApp(j);
                System.out.println("  ICBL: " + app.ICBL +
                                   ", SH2O: " + app.SH2O +
                                   ", SNH4: " + app.SNH4 +
                                   ", SNO3: " + app.SNO3);
            }
        }
    }
}
