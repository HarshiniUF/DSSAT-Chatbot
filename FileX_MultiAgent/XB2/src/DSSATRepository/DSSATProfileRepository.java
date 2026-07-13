package DSSATRepository;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.FilenameFilter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.logging.Level;
import java.util.logging.Logger;
import xbuild.LoadingDataFrame;

/**
 *
 * @author Jazzy
 */
public class DSSATProfileRepository {
    private final String rootPath;
    
    public DSSATProfileRepository(String rootPath){
        this.rootPath = rootPath;
    }
    
    public ArrayList<String> Parse() throws Exception{
        ArrayList<String> dssatList = new ArrayList<String>() {};
        
        // Set File to Read                
        FileReader file = null;
            
        // <editor-fold defaultstate="collapsed" desc="DSSATPRO.vxx">
        try {
            
            File directoryPath = new File(rootPath);
            
            FilenameFilter textFilefilter = (File dir, String name) -> {
                String lowercaseName = name.toLowerCase();
                return lowercaseName.contains("dssatpro.v");
            };
            
            String dssatProfile = "";
            
            File filesList[] = directoryPath.listFiles(textFilefilter);
            for(File f : filesList) {
                dssatProfile = f.getAbsolutePath();
            }            
            
            file = new FileReader(dssatProfile);
        } catch (FileNotFoundException ex) {
            System.out.println(ex);
        }
        
        BufferedReader br = new BufferedReader(file);
        try {
            String strRead;
            while (( strRead = br.readLine()) != null) {
                if (!"".equals(strRead) && !strRead.startsWith("*") && !strRead.startsWith("!")) {
                    dssatList.add(strRead);
                }
            }
        } catch (IOException ex) {
            throw ex;
        }
        try {
            br.close();
        } catch (IOException ex) {
            Logger.getLogger(LoadingDataFrame.class.getName()).log(Level.SEVERE, null, ex);
        }
        try {
            file.close();
        } catch (IOException ex) {
            Logger.getLogger(LoadingDataFrame.class.getName()).log(Level.SEVERE, null, ex);
        }

        // </editor-fold>
        
        return dssatList;
    }
}
