/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package FileXModel;

/**
 *
 * @author Jazzy
 */
public class EnvironmentalList extends ManagementList {
    
    @Override
    public ModelXBase AddNew(String name, int newLevel, ModelXBase currentModel) {
        Environmental model = new Environmental(name);
        modelList.add(model);
        model.SetLevel(newLevel);
        return model;
    }
    
    @Override
    public ModelXBase Clone(int sourceIndex, String newName){
        Environmental source = (Environmental) modelList.get(sourceIndex);
        Environmental newSource = null;
        
        try {            
            newSource = new Environmental();
            newSource.ENVNAME = newName;
            
            for(EnvironmentApplication c : source.GetApps()) {
                EnvironmentApplication ca = (EnvironmentApplication) c.Clone();           
                newSource.AddApp(ca);
            }
        }
        catch(Exception ex){
            
        }
        
        return newSource;
    }
    
    @Override
    public boolean IsUseInTreatment(int level) {
        boolean isUsed = false;
        
        for (ModelXBase treatment : FileX.treatments.GetAll()) {
            Treatment treat = (Treatment) treatment;
            if (treat.ME != null && treat.ME == level) {
                isUsed = true;
                break;
            }
        }
        return isUsed;
    }
}
