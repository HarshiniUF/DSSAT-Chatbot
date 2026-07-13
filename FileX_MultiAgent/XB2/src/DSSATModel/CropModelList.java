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
public class CropModelList {
    protected static List<CropModel> cropModels = new ArrayList<>();

    public static void AddNew(CropModel cropModel)
    {
        cropModels.add(cropModel);
    }
    
    public static void Clear(){
        cropModels.clear();
    }

    public static CropModel GetAt(String ModelCode)
    {
        for(int i = 0;i < cropModels.size();i++)
        {
            if(cropModels.get(i).ModelCode.equals(ModelCode))
                return cropModels.get(i);
        }
        return null;
    }
    
    public static CropModel GetByCrop(String CropCode)
    {
        for(int i = 0;i < cropModels.size();i++)
        {
            if(cropModels.get(i).Code.equals(CropCode))
                return cropModels.get(i);
        }
        return null;
    }

    public static CropModel GetAt(int n)
    {
        try{
            return cropModels.get(n);
        }
        catch(Exception ex) {}

        return null;
    }
    
    public static List<CropModel> GetAll()
    {
        Collections.sort(cropModels, (CropModel c1, CropModel c2) -> c1.compare(c2));
        
        return cropModels;
    }

    public static int size()
    {
        return cropModels.size();
    }
}
