/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package FileXModel;

/**
 *
 * @author Jazzy
 */
public class PlantingList extends ManagementList {
   
    public ModelXBase Clone(int sourceIndex, String newName){
        Planting source = (Planting) modelList.get(sourceIndex);
        Planting newSource = null;
        
        try{
            newSource = source.clone();
            newSource.PLNAME = newName;
        }
        catch(Exception ex){
            
        }
        
        return newSource;
    }

    @Override
    public ModelXBase AddNew(String name, int newLevel, ModelXBase currentModel) {
        Planting model = new Planting(name);
        modelList.add(model);
        model.SetLevel(newLevel);
        return model;
    }
    
    @Override
    public boolean IsUseInTreatment(int level) {
        boolean isUsed = false;
        
        for (ModelXBase treatment : FileX.treatments.GetAll()) {
            Treatment treat = (Treatment) treatment;
            if (treat.MP != null && treat.MP == level) {
                isUsed = true;
                break;
            }
        }
        return isUsed;
    }
}
