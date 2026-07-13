/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package FileXModel;

import java.util.ArrayList;

/**
 *
 * @author Jazzy
 */
public class OrganicList extends ManagementList {
    
    @Override
    public ModelXBase AddNew(String name, int newLevel, ModelXBase currentModel) {
        Organic model = new Organic(name);
        modelList.add(model);
        model.SetLevel(newLevel);
        return model;
    }
    
    public ModelXBase Clone(int sourceIndex, String newName){
        Organic source = (Organic) modelList.get(sourceIndex);
        Organic newSource = null;
        
        try {
            newSource = new Organic();
            newSource.RENAME = newName;
            
            for(OrganicApplication c : source.GetApps()) {
                OrganicApplication ca = (OrganicApplication) c.Clone();           
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
            if (treat.MR != null && treat.MR == level) {
                isUsed = true;
                break;
            }
        }
        return isUsed;
    }
}
