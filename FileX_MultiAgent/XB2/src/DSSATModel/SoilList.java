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
public class SoilList {
    protected static ArrayList<Soil> soils = new ArrayList();

    public static void AddNew(Soil soil)
    {
        soils.add(soil);
        
        Collections.sort(soils, (Soil s1, Soil s2) -> s1.Description.compareTo(s2.Description));
    }
    
    public static void Clear(){
        soils.clear();
    }

    public static Soil GetAt(String Code)
    {
        Soil soil = null;
        for(Soil s : soils) {
           if(s.Code.equalsIgnoreCase(Code)){
               soil = s;
               break;
           } 
        }

        return soil;
    }

    public static Soil GetAt(int n)
    {
        Soil soil = null;
        try{
            soil = (Soil) soils.get(n);
        }
        catch(Exception ex) {}

        return soil;
    }

    public static int size()
    {
        return soils.size();
    }
    
    public static List<Soil> GetAll()
    {
        List<Soil> soilList = new ArrayList<>();
        for(int i = 0;i < soils.size();i++){
            soilList.add(GetAt(i));
        }
        
        return soilList;
    }
}
