package DSSATRepository;

import Extensions.Variables;
import java.io.BufferedReader;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Date;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 *
 * @author Jazzy
 */
public class ChemicalRepository extends DSSATRepositoryBase {

    public ChemicalRepository(String rootPath) {
        super(rootPath);
    }   
    
    @Override
    public ArrayList<String> Parse() {
        ArrayList<String> chemList = new ArrayList<String>() {};

        try {
            FileReader file = new FileReader(rootPath + "\\DETAIL.CDE");

            BufferedReader br = new BufferedReader(file);
            String strRead = null;
            boolean bChem = false;
            while ((strRead = br.readLine()) != null) {
                if (strRead.trim().equals("*Chemicals (Herbicides, Insecticides, Fungicides, etc.)")) {
                    bChem = true;
                } else if (bChem) {
                    if (strRead.length() > 0) {
                        if (!strRead.substring(0, 1).equals("@") && !strRead.substring(0, 1).equals("!")) {
                            String s = strRead;
                            chemList.add(s);
                        }
                    } else {
                        bChem = false;
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
        
        return chemList;
    }
}
