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
public class TillageImplementList {

    protected static HashMap tillages = new HashMap();

    public static void AddNew(TillageImplement tillage)
    {
        tillages.put(tillage.Code, tillage);
    }
    
    public static void Clear(){
        tillages.clear();
    }

    public static TillageImplement GetAt(String Code)
    {
        TillageImplement tillage = null;
        try{
            tillage = (TillageImplement) tillages.get(Code);
        }
        catch(Exception ex) {}

        return tillage;
    }

    public static TillageImplement GetAt(int n)
    {
        TillageImplement tillage = null;
        try{
            Object[] object = tillages.values().toArray();
            tillage = (TillageImplement) object[n];
        }
        catch(Exception ex) {}

        return tillage;
    }
    
    public static List<TillageImplement> GetAll()
    {
        List<TillageImplement> tillageList = new ArrayList<>();
        
        for(Object object : tillages.values().toArray()){
            tillageList.add((TillageImplement) object);
        }
        
        Collections.sort(tillageList, (TillageImplement t1, TillageImplement t2) -> t1.Description.compareTo(t2.Description));

        return tillageList;
    }

    public static int size()
    {
        return tillages.size();
    }
}
