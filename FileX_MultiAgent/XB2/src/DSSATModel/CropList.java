/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package DSSATModel;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

/**
 *
 * @author Jazzy
 */
public class CropList {
    protected static ArrayList<Crop> crops = new ArrayList<>();

    public static void AddNew(Crop crop)
    {
        crops.add(crop);
    }
    
    public static void Clear()
    {
        crops.clear();
    }

    public static Crop GetAt(String Code)
    {
        Crop crop = null;
        try{
            Object[] object = crops.toArray();
            for(int i = 0;i < object.length;i++)
            {
                if(((Crop)object[i]).CropCode.equals(Code))
                {
                    Crop tmp = ((Crop) object[i]);
                    crop = new Crop();
                    crop.CropCode = tmp.CropCode;
                    crop.CropName = tmp.CropName;
                    break;
                }
            }
        }
        catch(Exception ex) {}

        return crop;
    }

    public static Crop GetAt(int n)
    {
        Crop crop = null;
        try{
            Object[] object = crops.toArray();
            crop = (Crop) object[n];
        }
        catch(Exception ex) {}

        return crop;
    }

    public static int size()
    {
        return crops.size();
    }
    
    public static List<Crop> GetAll(){
        List<Crop> cropList = new ArrayList<>();

        Object[] objects = crops.toArray();

        for (Object object : objects) {
            cropList.add((Crop) object);
        }

        Collections.sort(cropList, (Crop c1, Crop c2) -> c1.CropCode.compareTo(c2.CropCode));
        
        return cropList;
    }

    public static Crop GetAtName(String CropName) {
        Crop crop = null;
        try{
            Object[] object = crops.toArray();
            for(int i = 0;i < object.length;i++)
            {
                if(((Crop)object[i]).CropName.equals(CropName))
                {
                    crop = (Crop) object[i];
                    break;
                }
            }
        }
        catch(Exception ex) {}

        return crop;
    }
}
