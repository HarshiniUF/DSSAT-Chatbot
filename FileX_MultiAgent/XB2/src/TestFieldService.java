import FileXService.FieldService;
import FileXModel.FileX;
import FileXModel.FieldDetail;

import java.io.File;

public class TestFieldService {
    public static void main(String[] args) {
        if (args.length != 1) {
            System.out.println("Usage: java TestFieldService <path_to_file>");
            return;
        }

        String filePath = args[0];
        File file = new File(filePath);

        // Initialize FileX static fields (VERY IMPORTANT!)
        FileX.NewFileX();

        // Read fields from file
        FieldService.Read(file);

        // Print out loaded fields
        System.out.println("=== Fields Loaded ===");
        for (int i = 0; i < FileX.fieldList.GetSize(); i++) {
            FieldDetail field = (FieldDetail) FileX.fieldList.GetAtIndex(i);
            System.out.println("Level: " + field.GetLevel() +
                               ", ID_FIELD: " + field.ID_FIELD +
                               ", WSTA: " + field.WSTA +
                               ", FLSA: " + field.FLSA +
                               ", FLOB: " + field.FLOB +
                               ", FLDT: " + field.FLDT +
                               ", FLDD: " + field.FLDD +
                               ", FLDS: " + field.FLDS +
                               ", FLST: " + field.FLST +
                               ", SLTX: " + field.SLTX +
                               ", SLDP: " + field.SLDP +
                               ", ID_SOIL: " + field.ID_SOIL +
                               ", FLNAME: " + field.FLNAME);
            // Print more fields as needed
        }
    }
}
