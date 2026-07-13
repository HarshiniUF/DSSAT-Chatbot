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
public class IrrigationMethodList {
    protected static HashMap irrigs = new HashMap();

    public static void AddNew(IrrigationMethod irrig)
    {
        irrigs.put(irrig.Code, irrig);
    }
    
    public static void Clear(){
        irrigs.clear();
    }

    public static IrrigationMethod GetAt(String Code)
    {
        IrrigationMethod irrig = null;
        try{
            irrig = (IrrigationMethod) irrigs.get(Code);
        }
        catch(Exception ex) {}

        return irrig;
    }

    public static IrrigationMethod GetAt(int n)
    {
        IrrigationMethod irrig = null;
        try{
            Object[] object = irrigs.values().toArray();
            irrig = (IrrigationMethod) object[n];
        }
        catch(Exception ex) {}

        return irrig;
    }
    
    public static List<BaseModel> GetAll()
    {
        List<BaseModel> irrigList = new ArrayList<>();
        
        for(Object object : irrigs.values().toArray()){
            irrigList.add((IrrigationMethod) object);
        }
        
        Collections.sort(irrigList, (BaseModel i1, BaseModel i2) -> i1.Description.compareTo(i2.Description));

        return irrigList;
    }

    public static int size()
    {
        return irrigs.size();
    }
}
