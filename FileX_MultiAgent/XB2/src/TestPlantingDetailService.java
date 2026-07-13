import FileXService.PlantingDetailService;
import FileXModel.Planting;
import FileXModel.FileX; // Assuming plantings is static in FileX

import java.io.File;

public class TestPlantingDetailService {
    public static void main(String[] args) {
        if (args.length != 1) {
            System.out.println("Usage: java TestPlantingDetailService <path_to_file>");
            return;
        }

        String filePath = args[0];
        File file = new File(filePath);

        if (!file.exists()) {
            System.out.println("File not found: " + filePath);
            return;
        }

         // Initialize FileX static fields
        FileX.NewFileX();

        // Read the planting details from the file
        PlantingDetailService.Read(file);

        // Print out the loaded plantings
        System.out.println("=== Planting Details ===");
        for (int i = 0; i < FileX.plantings.GetSize(); i++) {
            Planting planting = (Planting) FileX.plantings.GetAtIndex(i);
            System.out.println("Planting #" + (i + 1));
            System.out.println("  Level: " + planting.GetLevel());
            System.out.println("  PDATE: " + planting.PDATE);
            System.out.println("  EDATE: " + planting.EDATE);
            System.out.println("  PPOP: " + planting.PPOP);
            System.out.println("  PPOE: " + planting.PPOE);
            System.out.println("  PLME: " + planting.PLME);
            System.out.println("  PLDS: " + planting.PLDS);
            System.out.println("  PLRS: " + planting.PLRS);
            System.out.println("  PLRD: " + planting.PLRD);
            System.out.println("  PLDP: " + planting.PLDP);
            System.out.println("  PLWT: " + planting.PLWT);
            System.out.println("  PAGE: " + planting.PAGE);
            System.out.println("  PENV: " + planting.PENV);
            System.out.println("  PLPH: " + planting.PLPH);
            System.out.println("  SPRL: " + planting.SPRL);
            System.out.println("  PLNAME: " + planting.PLNAME);
            System.out.println("------------------------");
        }
    }
}
