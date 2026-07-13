/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package FileXModel;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.Date;

/**
 *
 * @author Jazzy
 */
public class SoilAnalysis extends ModelXBase implements Cloneable {
     protected ArrayList<SoilAnalysisLayer>  soilLayer = new ArrayList<>();
     public Date SADAT;
     public String SMHB;;
     public String SMPX;
     public String SMKE;
     public String SANAME;

     public SoilAnalysis() {
     }

     public SoilAnalysis(String SANAME)
     {
         this.SANAME = SANAME;
     }

     public void AddLayer(SoilAnalysisLayer sLayer)
    {
        soilLayer.add(sLayer);
        Collections.sort(soilLayer, Comparator.comparing(SoilAnalysisLayer::getOrder));
    }

    public void RemoveLayer(int level)
    {
        soilLayer.remove(level);
    }

    public void SetAt(int level, SoilAnalysisLayer sLayer)
    {
        soilLayer.set(level, sLayer);
    }

    public ArrayList<SoilAnalysisLayer> GetLayers()
    {
        return soilLayer;
    }

    public SoilAnalysisLayer GetLayer(int level)
    {
        return (SoilAnalysisLayer)soilLayer.get(level);
    }

    public void ClearLayer()
    {
        soilLayer.clear();
    }

    public int GetSize()
    {
        return soilLayer.size();
    }
    
     @Override
    public SoilAnalysis clone() throws CloneNotSupportedException{
        return (SoilAnalysis)super.clone();
    }

    @Override
    public String GetName() {
        return this.SANAME == null ? "" : this.SANAME;
    }
    
    @Override
    public void SetName(String name) {
        SANAME = name;
    }
}
