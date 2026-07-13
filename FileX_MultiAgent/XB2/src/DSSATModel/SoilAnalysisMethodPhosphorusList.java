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
public class SoilAnalysisMethodPhosphorusList {

    protected static HashMap methods = new HashMap();

    public static void AddNew(SoilAnalysisMethodPhosphorus phos)
    {
        methods.put(phos.Code, phos);
    }
    
    public static void Clear(){
        methods.clear();
    }

    public static SoilAnalysisMethodPhosphorus GetAt(String Code)
    {
        SoilAnalysisMethodPhosphorus ph = null;
        try{
            ph = (SoilAnalysisMethodPhosphorus) methods.get(Code);
        }
        catch(Exception ex) {}

        return ph;
    }

    public static SoilAnalysisMethodPhosphorus GetAt(int n)
    {
        SoilAnalysisMethodPhosphorus ph = null;
        try{
            Object[] object = methods.values().toArray();
            ph = (SoilAnalysisMethodPhosphorus) object[n];
        }
        catch(Exception ex) {}

        return ph;
    }
    
    public static List<SoilAnalysisMethodPhosphorus> GetAll()
    {
        List<SoilAnalysisMethodPhosphorus> soilAnalysisList = new ArrayList<>();
        
        for(Object object : methods.values().toArray()){
            soilAnalysisList.add((SoilAnalysisMethodPhosphorus) object);
        }
        
        Collections.sort(soilAnalysisList, (SoilAnalysisMethodPhosphorus s1, SoilAnalysisMethodPhosphorus s2) -> s1.Description.compareTo(s2.Description));

        return soilAnalysisList;
    }

    public static int size()
    {
        return methods.size();
    }
}
