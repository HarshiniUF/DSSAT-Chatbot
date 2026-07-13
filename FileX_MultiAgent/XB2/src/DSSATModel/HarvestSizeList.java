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
public class HarvestSizeList {

    protected static HashMap harvestSize = new HashMap();

    public static void AddNew(HarvestSize harvest)
    {
        harvestSize.put(harvest.Code, harvest);
    }
    
    public static void Clear(){
        harvestSize.clear();
    }

    public static HarvestSize GetAt(String Code)
    {
        HarvestSize harvest = null;
        try{
            harvest = (HarvestSize) harvestSize.get(Code);
        }
        catch(Exception ex) {}

        return harvest;
    }

    public static HarvestSize GetAt(int n)
    {
        HarvestSize harvest = null;
        try{
            Object[] object = harvestSize.values().toArray();
            harvest = (HarvestSize) object[n];
        }
        catch(Exception ex) {}

        return harvest;
    }
    
    public static List<HarvestSize> GetAll()
    {
        List<HarvestSize> havestSizeList = new ArrayList<>();
        
        for(Object object : harvestSize.values().toArray()){
            havestSizeList.add((HarvestSize) object);
        }
        
        Collections.sort(havestSizeList, (HarvestSize h1, HarvestSize h2) -> h1.Description.compareTo(h2.Description));

        return havestSizeList;
    }

    public static int size()
    {
        return harvestSize.size();
    }
}
