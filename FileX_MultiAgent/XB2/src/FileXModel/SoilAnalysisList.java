/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package FileXModel;

/**
 *
 * @author Jazzy
 */
public class SoilAnalysisList extends ManagementList {   
       
    @Override
    public ModelXBase AddNew(String name, int newLevel, ModelXBase currentModel) {
        SoilAnalysis model = new SoilAnalysis(name);
        modelList.add(model);
        model.SetLevel(newLevel);
        return model;
    }
    
    @Override
    public ModelXBase Clone(int sourceIndex, String newName){
        SoilAnalysis source = (SoilAnalysis) modelList.get(sourceIndex);
        SoilAnalysis newSource = null;
        
        try{            
            newSource = new SoilAnalysis();
            newSource.SANAME = newName;
            newSource.SADAT = source.SADAT;
            newSource.SMHB = source.SMHB;
            newSource.SMPX = source.SMPX;
            newSource.SMKE = source.SMKE;
            
            for(SoilAnalysisLayer c : source.GetLayers()) {
                SoilAnalysisLayer ca = (SoilAnalysisLayer) c.Clone();           
                newSource.AddLayer(ca);
            }
        }
        catch(Exception ex){
            
        }
        
        return newSource;
    }

    @Override
    public boolean IsUseInTreatment(int level) {
        boolean isUsed = FileX.treatments.treatments.stream().anyMatch(treatment -> treatment.SA != null && treatment.SA == level);
        return isUsed;
    }    
}
