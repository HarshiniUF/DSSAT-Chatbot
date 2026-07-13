import FileXService.CultivarService;
import FileXModel.FileX;
import FileXModel.Cultivar;

import java.io.File;

public class TestCultivarService {
    public static void main(String[] args) {
        if (args.length != 1) {
            System.out.println("Usage: java TestCultivarService <path_to_file>");
            return;
        }

        String filePath = args[0];
        File file = new File(filePath);

        // Initialize static fields in FileX
        FileX.NewFileX();

        // Read cultivars from file
        CultivarService.Read(file);

        // Print out loaded cultivars
        System.out.println("=== Cultivars Loaded ===");
        for (int i = 0; i < FileX.cultivars.GetSize(); i++) {
            Cultivar cul = (Cultivar) FileX.cultivars.GetAtIndex(i);
            System.out.println("Level: " + cul.GetLevel() +
                               ", CR: " + cul.CR +
                               ", INGENO: " + cul.INGENO +
                               ", CNAME: " + cul.CNAME);
        }
    }
}
