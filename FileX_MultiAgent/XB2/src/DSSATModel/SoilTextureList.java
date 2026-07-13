/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package DSSATModel;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;

/**
 *
 * @author Jazzy
 */
public class SoilTextureList {
    protected static HashMap soils = new HashMap();

    public static void AddNew(SoilTexture soil)
    {
        soils.put(soil.Code, soil);
    }
    
    public static void Clear(){
        soils.clear();
    }

    public static SoilTexture GetAt(String Code)
    {
        SoilTexture soil = null;
        try{
            soil = (SoilTexture) soils.get(Code);
        }
        catch(Exception ex) {}

        return soil;
    }

    public static SoilTexture GetAt(int n)
    {
        SoilTexture soil = new SoilTexture();
        try{
            Object[] object = soils.values().toArray();
            soil = (SoilTexture) object[n];
        }
        catch(Exception ex) {}

        return soil;
    }
    
    public static List<SoilTexture> GetAll()
    {
        List<SoilTexture> soilTextureList = new ArrayList<>();
        
        for(Object object : soils.values().toArray()){
            soilTextureList.add((SoilTexture) object);
        }
        
        Collections.sort(soilTextureList, (SoilTexture s1, SoilTexture s2) -> s1.Description.compareTo(s2.Description));

        return soilTextureList;
    }

    public static int size()
    {
        return soils.size();
    }
}
