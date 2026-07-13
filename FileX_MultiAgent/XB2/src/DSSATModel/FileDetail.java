/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package DSSATModel;

import java.io.*;
import java.util.*;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 *
 * @author Jazzy
 */
public class FileDetail {
    protected String fileName;
    public FileDetail(String fileName)
    {
        this.fileName = fileName;
    }

    public Crop[] ReadCrop()
    {
        FileReader file = null;
        try {
            file = new FileReader(fileName);
        } catch (FileNotFoundException ex) {
            Logger.getLogger(FileDetail.class.getName()).log(Level.SEVERE, null, ex);
        }
        BufferedReader br = new BufferedReader(file);
        boolean bCrop = false;
        String strCrop;
        ArrayList<Crop> cropList = new ArrayList<Crop>() {};

        try {
            while ((strCrop = br.readLine()) != null) {
                if (strCrop.equals("*Crop and Weed Species")) {
                    bCrop = true;
                } else if (bCrop) {
                    if(strCrop.length() > 0)
                    {
                        if (!strCrop.substring(0, 1).equals("@")) {
                            Crop crop = new Crop();
                            crop.CropCode = strCrop.substring(0, 2);
                            crop.CropName = strCrop.substring(9, 78).trim();
                            cropList.add(crop);
                        }
                    }
                    else {
                        break;
                    }
                }
            }
        } catch (IOException ex) {
            System.out.println(ex.getMessage());
        }

        try {
            br.close();
        } catch (IOException ex) {
            System.out.println(ex.getMessage());
        }
        try {
            file.close();
        } catch (IOException ex) {
            System.out.println(ex.getMessage());
        }

        Crop crops[] = new Crop[cropList.size()];

        for(int i = 0;i < cropList.size();i++)
        {
            crops[i] = cropList.get(i);
        }
        return crops;
    }
}
