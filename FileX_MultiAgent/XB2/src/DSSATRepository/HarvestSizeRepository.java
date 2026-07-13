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
 * @author Jazzy
 */
public class HarvestSizeRepository extends DSSATRepositoryBase {
    
    public HarvestSizeRepository(String rootPath) {
        super(rootPath);
    }
    
    @Override
    public ArrayList<String> Parse() {
        ArrayList<String> harvestSizeList = new ArrayList<String>() {};

        try {
            FileReader file = new FileReader(rootPath + "\\DETAIL.CDE");

            BufferedReader br = new BufferedReader(file);
            String strRead = null;
            boolean bHarvestSize = false;
            while ((strRead = br.readLine()) != null) {
                if (strRead.trim().equals("*Harvest size categories")) {
                    bHarvestSize = true;
                } else if (bHarvestSize) {
                    if (strRead.length() > 0) {
                        if (!strRead.substring(0, 1).equals("@") && !strRead.substring(0, 1).equals("!")) {
                            String s = strRead;
                            harvestSizeList.add(s);
                        }
                    } else {
                        bHarvestSize = false;
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
        
        return harvestSizeList;
    }    
}
