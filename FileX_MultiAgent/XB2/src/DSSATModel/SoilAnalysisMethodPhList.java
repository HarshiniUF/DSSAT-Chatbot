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
public class SoilAnalysisMethodPhList {
    protected static HashMap methods = new HashMap();

    public static void AddNew(SoilAnalysisMethodPh ph)
    {
        methods.put(ph.Code, ph);
    }
    
    public static void Clear(){
        methods.clear();
    }

    public static SoilAnalysisMethodPh GetAt(String Code)
    {
        SoilAnalysisMethodPh ph = null;
        try{
            ph = (SoilAnalysisMethodPh) methods.get(Code);
        }
        catch(Exception ex) {}

        return ph;
    }

    public static SoilAnalysisMethodPh GetAt(int n)
    {
        SoilAnalysisMethodPh ph = null;
        try{
            Object[] object = methods.values().toArray();
            ph = (SoilAnalysisMethodPh) object[n];
        }
        catch(Exception ex) {}

        return ph;
    }
    
    public static List<SoilAnalysisMethodPh> GetAll()
    {
        List<SoilAnalysisMethodPh> soilAnalysisList = new ArrayList<>();
        
        for(Object object : methods.values().toArray()){
            soilAnalysisList.add((SoilAnalysisMethodPh) object);
        }
        
        Collections.sort(soilAnalysisList, (SoilAnalysisMethodPh s1, SoilAnalysisMethodPh s2) -> s1.Description.compareTo(s2.Description));

        return soilAnalysisList;
    }

    public static int size()
    {
        return methods.size();
    }
}
