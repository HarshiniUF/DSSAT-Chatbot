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
public class GrowthStageRepository extends DSSATRepositoryBase {
    
    public GrowthStageRepository(String rootPath) {
        super(rootPath);
    }
    
    @Override
    public ArrayList<String> Parse() {
        ArrayList<String> gStage = new ArrayList<String>() {};

        try {
            FileReader file = new FileReader(rootPath + "\\GRSTAGE.cde");

            BufferedReader br = new BufferedReader(file);
            String strRead = null;
            boolean bGStage = false;
            String header = null;
            while ((strRead = br.readLine()) != null) {
                ///////////// Read Growth and Development Codes  ////////////////////////////
                if (strRead.contains("*Growth and Development Codes")) {
                    header = strRead.replace("*Growth and Development Codes - ", "");
                    if (header.contains("(")) {
                        header = header.substring(0, header.indexOf("(")).trim();
                    }
                    bGStage = true;
                } else if (bGStage) {
                    if (strRead.trim().length() > 0) {
                        if (!strRead.startsWith("@") && !strRead.startsWith("!")) {
                            String s = strRead + header;
                            gStage.add(s);
                        }
                    } else {
                        bGStage = false;
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
        
        return gStage;
    }
}
