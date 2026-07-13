package DSSATRepository;

import java.io.BufferedReader;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 *
 * @author Jazz
 */
public class IrrigationMethodRepository extends DSSATRepositoryBase {
    
    public IrrigationMethodRepository(String rootPath) {
        super(rootPath);
    }
    
    @Override
    public ArrayList<String> Parse() {
        ArrayList<String> irrigationMethod = new ArrayList<>();

        try {
            FileReader file = new FileReader(rootPath + "\\DETAIL.CDE");

            BufferedReader br = new BufferedReader(file);
            String strRead = null;
            boolean bIrrigation = false;
            while ((strRead = br.readLine()) != null) {
                if (strRead.trim().equals("*Methods - Irrigation and Water Management (Units for associated data)")) {
                    bIrrigation = true;
                } else if (bIrrigation) {
                    if (strRead.length() > 0) {
                        if (!strRead.substring(0, 1).equals("@") && !strRead.substring(0, 1).equals("!")) {
                            String s = strRead;
                            irrigationMethod.add(s);
                        }
                    } else {
                        bIrrigation = false;
                        break;
                    }
                }
            }
            
            br.close();
            file.close();

        } catch (FileNotFoundException ex) {
            System.out.println(ex);
        } catch (IOException ex) {
            Logger.getLogger(CropRepository.class.getName()).log(Level.SEVERE, null, ex);
        }
        
        return irrigationMethod;
    }
}
