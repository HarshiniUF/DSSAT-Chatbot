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
public class ChemicalMaterialList {

    //public static ChemicalMaterial chemicals[];
    protected static HashMap chemicals = new HashMap();

    public static void Clear()
    {
        chemicals.clear();
    }

    public static void AddNew(ChemicalMaterial chem)
    {
        chemicals.put(chem.Code, chem);
    }

    public static ChemicalMaterial GetAt(String Code)
    {
        ChemicalMaterial chem = null;
        try{
            chem = (ChemicalMaterial) chemicals.get(Code);
        }
        catch(Exception ex) {}

        return chem;
    }

    public static ChemicalMaterial GetAt(int n)
    {
        ChemicalMaterial chem = null;
        try{
            Object[] object = chemicals.values().toArray();
            chem = (ChemicalMaterial) object[n];
        }
        catch(Exception ex) {}

        return chem;
    }
    
    public static List<ChemicalMaterial> GetAll(){
        List<ChemicalMaterial> chemicalList = new ArrayList<>();

        Object[] objects = chemicals.values().toArray();

        for (Object object : objects) {
            chemicalList.add((ChemicalMaterial) object);
        }

        Collections.sort(chemicalList, (ChemicalMaterial c1, ChemicalMaterial c2) -> c1.Description.compareTo(c2.Description));
        
        return chemicalList;
    }

    public static int size()
    {
        return chemicals.size();
    }
}
