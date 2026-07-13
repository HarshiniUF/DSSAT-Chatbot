/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package DSSATModel;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;

/**
 *
 * @author Jazzy
 */
public class HarvestComponentList {

    protected static HashMap harvestComp = new HashMap();

    public static void AddNew(HarvestComponent harvest)
    {
        harvestComp.put(harvest.Code, harvest);
    }
    
    public static void Clear(){
        harvestComp.clear();
    }

    public static HarvestComponent GetAt(String Code)
    {
        HarvestComponent harvest = null;
        try{
            harvest = (HarvestComponent) harvestComp.get(Code);
        }
        catch(Exception ex) {}

        return harvest;
    }

    public static HarvestComponent GetAt(int n)
    {
        HarvestComponent harvest = null;
        try{
            Object[] object = harvestComp.values().toArray();
            harvest = (HarvestComponent) object[n];
        }
        catch(Exception ex) {}

        return harvest;
    }
    
    public static List<HarvestComponent> GetAll()
    {
        List<HarvestComponent> havestCompList = new ArrayList<>();
        
        for(Object object : harvestComp.values().toArray()){
            havestCompList.add((HarvestComponent) object);
        }
        
        Collections.sort(havestCompList, (HarvestComponent h1, HarvestComponent h2) -> h1.Description.compareTo(h2.Description));

        return havestCompList;
    }

    public static int size()
    {
        return harvestComp.size();
    }
}
