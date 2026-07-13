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
public class PlantingMethodList {
    /*public static PlantingMethod plantingMethods[];

    public static void setSize(int size)
    {
        PlantingMethod plantingList[] = new PlantingMethod[size];

        PlantingMethodList.plantingMethods = plantingList;
    }
     *
     */

    protected static HashMap pMethod = new HashMap();

    public static void AddNew(PlantingMethod plant)
    {
        pMethod.put(plant.Code, plant);
    }
    
    public static void Clear(){
        pMethod.clear();
    }

    public static PlantingMethod GetAt(String Code)
    {
        PlantingMethod plant = null;
        try{
            plant = (PlantingMethod) pMethod.get(Code);
        }
        catch(Exception ex) {}

        return plant;
    }

    public static PlantingMethod GetAt(int n)
    {
        PlantingMethod plant = null;
        try{
            Object[] object = pMethod.values().toArray();
            plant = (PlantingMethod) object[n];
        }
        catch(Exception ex) {}

        return plant;
    }
    
    public static List<PlantingMethod> GetAll()
    {
        List<PlantingMethod> plantingMethodList = new ArrayList<>();
        
        for(Object object : pMethod.values().toArray()){
            plantingMethodList.add((PlantingMethod) object);
        }
        
        Collections.sort(plantingMethodList, (PlantingMethod p1, PlantingMethod p2) -> p1.Description.compareTo(p2.Description));

        return plantingMethodList;
    }

    public static int size()
    {
        return pMethod.size();
    }
}
