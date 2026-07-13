/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package DSSATModel;

import java.io.BufferedReader;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 *
 * @author Jazzy
 */
public class CultivarList {
    public static ArrayList<Cultivar> cultivars = new ArrayList<>();

    public static void AddNew(Crop crop, String culFile) {
        if(culFile.length() > 0){
            try {
                FileReader file = null;
                try {
                    file = new FileReader(culFile);
                } catch (FileNotFoundException ex) {
                    System.out.println(ex);
                }
                BufferedReader br = new BufferedReader(file);
                String strRead = "";
                while ((strRead = br.readLine()) != null) {
                    if (!strRead.startsWith("!") && !strRead.startsWith("*") && !strRead.startsWith("@") && !strRead.startsWith("$") && strRead.trim().length() >= 8) {
                        try {
                            int end = (strRead.length() > 23) ? 23 : strRead.length();
                            Cultivar cul = new Cultivar(crop);
                            cul.CulCode = strRead.substring(0, 6).trim();
                            cul.CulName = strRead.substring(7, end).trim();
                            cultivars.add(cul);
                        } catch (Exception e) {
                            System.out.println(strRead + "\n" + e.getMessage());
                        }
                    }
                }
            } catch (IOException ex) {
                Logger.getLogger(CultivarList.class.getName()).log(Level.SEVERE, null, ex);
            }
        }
        else{
            Cultivar cul = new Cultivar(crop);
            if(crop.CropCode.equals("FA")){
               cul.CulCode = "IB0001";
               cul.CulName = crop.CropName;
            }
            cultivars.add(cul);
        }
    }

    public static int size()
    {
        return cultivars.size();
    }

    public static Cultivar GetAt(String CulCode, Crop crop)
    {
        Cultivar cul = null;
        for(int i = 0;i < cultivars.size();i++)
        {
            if(((Cultivar)cultivars.get(i)).CulCode.equals(CulCode) && ((Cultivar)cultivars.get(i)).CropCode.equals(crop.CropCode))
                cul = (Cultivar)cultivars.get(i);
        }

        return cul;
    }
    
    public static List<Cultivar> GetAll()
    {
        List<Cultivar> culs = new ArrayList<>();
        for(int i = 0;i < cultivars.size();i++)
        {
            culs.add((Cultivar)cultivars.get(i));
        }
        
        Collections.sort(culs, (Cultivar c1, Cultivar c2) -> {
            int c = c1.CropName.compareTo(c2.CropName);
            if(c == 0)
                c = c1.CulName.compareTo(c2.CulName);
            
            return c;
        });

        return culs;
    }

    public static List<Cultivar> GetAt(Crop crop)
    {
        List<Cultivar> culs = new ArrayList<>();
        for(int i = 0;i < cultivars.size();i++)
        {
            if(((Cultivar)cultivars.get(i)).CropCode.equals(crop.CropCode))
                culs.add((Cultivar)cultivars.get(i));
        }
        
        Collections.sort(culs, (Cultivar c1, Cultivar c2) -> c1.CulName.compareTo(c2.CulName));

        return culs;
    }

    public static Cultivar GetAt(int i)
    {
        Cultivar cul = null;
        try{
            cul = (Cultivar) cultivars.get(i);
        }
        catch(Exception ex) {}

        return cul;
    }

    public static void Clear()
    {
        cultivars.clear();
    }
}
