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
public class DrainageList {
    protected static HashMap drainages = new HashMap();

    public static void AddNew(Drainage drainage)
    {
        drainages.put(drainage.Code, drainage);
    }
    
    public static void Clear(){
        drainages.clear();
    }

    public static Drainage GetAt(String Code)
    {
        Drainage drainage = null;
        try{
            drainage = (Drainage) drainages.get(Code);
        }
        catch(Exception ex) {}

        return drainage;
    }

    public static Drainage GetAt(int n)
    {
        Drainage drainage = null;
        try{
            Object[] object = drainages.values().toArray();
            drainage = (Drainage) object[n];
        }
        catch(Exception ex) {}

        return drainage;
    }
    
    public static List<Drainage> GetAll()
    {
        List<Drainage> drains = new ArrayList<>();
        for(Object drainage : drainages.values().toArray())
        {
            drains.add((Drainage) drainage);
        }
        
        Collections.sort(drains, (Drainage d1, Drainage d2) -> d1.Description.compareTo(d2.Description));
        
        return drains;
    }

    public static int size()
    {
        return drainages.size();
    }
}
