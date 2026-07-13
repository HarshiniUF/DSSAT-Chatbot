import FileXService.FertilizerService;
import FileXModel.FileX;
import FileXModel.Fertilizer;
import FileXModel.FertilizerApplication;

import java.io.File;

public class TestFertilizerService {
    public static void main(String[] args) {
        if (args.length != 1) {
            System.out.println("Usage: java TestFertilizerService <path_to_file>");
            return;
        }

        String filePath = args[0];
        File file = new File(filePath);

        // Initialize FileX static fields (VERY IMPORTANT!)
        FileX.NewFileX();

        // Read fertilizers from file
        FertilizerService.Read(file);

        // Print out loaded fertilizers
        System.out.println("=== Fertilizers Loaded ===");
        for (int i = 0; i < FileX.fertilizerList.GetSize(); i++) {
            Fertilizer fertil = (Fertilizer) FileX.fertilizerList.GetAtIndex(i);
            System.out.println(
                "Level: " + fertil.GetLevel() +
                ", FERNAME: " + fertil.FERNAME
            );
            // Print applications
            for (int j = 0; j < fertil.GetSize(); j++) {
                FertilizerApplication app = fertil.GetApp(j);
                System.out.println("  Application: FDATE: " + app.FDATE +
                                   ", FDAY: " + app.FDAY +
                                   ", FMCD: " + app.FMCD +
                                   ", FACD: " + app.FACD +
                                   ", FDEP: " + app.FDEP +
                                   ", FAMN: " + app.FAMN +
                                   ", FAMP: " + app.FAMP +
                                   ", FAMK: " + app.FAMK +
                                   ", FAMC: " + app.FAMC +
                                   ", FAMO: " + app.FAMO +
                                   ", FOCD: " + app.FOCD);
            }
        }
    }
}
