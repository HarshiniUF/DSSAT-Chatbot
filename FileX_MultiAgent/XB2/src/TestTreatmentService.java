import FileXService.TreatmentService;
import FileXModel.FileX;
import FileXModel.Treatment;

import java.io.File;

public class TestTreatmentService {
    public static void main(String[] args) {
        if (args.length != 1) {
            System.out.println("Usage: java TestTreatmentService <path_to_file>");
            return;
        }

        String filePath = args[0];
        File file = new File(filePath);

        // Initialize FileX static fields (VERY IMPORTANT!)
        FileX.NewFileX();

        // Read treatments from file
        TreatmentService.Read(file);

        // Print out loaded treatments
        System.out.println("=== Treatments Loaded ===");
        for (int i = 0; i < FileX.treatments.GetSize(); i++) {
            Treatment treat = (Treatment) FileX.treatments.GetAtIndex(i);
            System.out.println(
                "Level: " + treat.GetLevel() +
                ", TNAME: " + treat.TNAME +
                ", CU: " + treat.CU +
                ", FL: " + treat.FL +
                ", SA: " + treat.SA +
                ", IC: " + treat.IC +
                ", MP: " + treat.MP +
                ", MI: " + treat.MI +
                ", MF: " + treat.MF +
                ", MR: " + treat.MR +
                ", MC: " + treat.MC +
                ", MT: " + treat.MT +
                ", ME: " + treat.ME +
                ", MH: " + treat.MH +
                ", SM: " + treat.SM
            );
        }
    }
}
