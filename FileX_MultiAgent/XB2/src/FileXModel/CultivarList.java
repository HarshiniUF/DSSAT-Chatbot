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
public class CultivarList extends ManagementList {
    protected ArrayList<Cultivar> cultivars = new ArrayList<>();

    @Override
    public ModelXBase AddNew(String name, int newLevel, ModelXBase currentModel) {
        Cultivar model = new Cultivar(name);
        modelList.add(model);
        model.SetLevel(newLevel);
        return model;
    }

    @Override
    public ModelXBase Clone(int sourceIndex, String newName) {
        Cultivar source = (Cultivar) modelList.get(sourceIndex);
        Cultivar newSource = null;
        
        try{
            newSource = new Cultivar();
            newSource.CNAME = source.CNAME;
            newSource.CR = source.CR;
            newSource.INGENO = source.INGENO;
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
            if (treat.CU != null && treat.CU == level) {
                isUsed = true;
                break;
            }
        }
        return isUsed;
    }
}
