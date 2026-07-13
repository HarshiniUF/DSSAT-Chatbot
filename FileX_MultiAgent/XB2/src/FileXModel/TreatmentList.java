/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package FileXModel;

import DSSATModel.ExperimentType;
import Extensions.Utils;
import java.util.ArrayList;
import java.util.Collections;

/**
 *
 * @author Jazzy
 */
public class TreatmentList extends ManagementList {
    protected ArrayList<Treatment> treatments = new ArrayList<>();

    @Override
    public ModelXBase AddNew(String name, int newLevel, ModelXBase currentModel) {
        Treatment model;//new Treatment(name);
        
        if(currentModel != null){
            try {
                model = (Treatment) currentModel.Clone();
            } catch (CloneNotSupportedException ex) {
                model = new Treatment(name);
                model.SetLevel(FileX.general.FileType == ExperimentType.Sequential ? 1 : newLevel);
            }
            
            if(FileX.general.FileType != ExperimentType.Sequential){
                model.SetLevel(FileX.treatments.GetSize() + 1);
            }
            else{
                //Integer r = Utils.ParseInteger(((Treatment)FileX.treatments.GetAtIndex(FileX.treatments.GetSize() - 1)).R);
                newLevel = model.GetLevel();
                model.R = getRotationNumber(newLevel);
            }
            
            model.TNAME = name;
        }
        else{
            model = new Treatment(name);
            model.SetLevel(FileX.general.FileType == ExperimentType.Sequential ? 1 : newLevel);
        }
        
        if(FileX.treatments.GetSize() == 0){
            model.CU = FileX.cultivars.GetAtIndex(0).GetLevel();
            model.FL = FileX.fieldList.GetAtIndex(0).GetLevel();
            model.MP = FileX.plantings.GetAtIndex(0).GetLevel();
            model.SM = FileX.simulationList.GetAtIndex(0).GetLevel();
        }
        model.SetLevel(newLevel);
        modelList.add(model);
        
        if(FileX.general.FileType == ExperimentType.Sequential){
            Collections.sort(modelList, (Object o1, Object o2) -> {
                Treatment t1 = (Treatment) o1;
                Treatment t2 = (Treatment) o2;

                if(t1.GetLevel().compareTo(t2.GetLevel()) == 0)
                    return Utils.ParseInteger(t1.R).compareTo(Utils.ParseInteger(t2.R));
                else
                    return t1.GetLevel().compareTo(t2.GetLevel());
            });
            
            Integer r = 1;
            for(ModelXBase m : modelList) {
                Treatment t = (Treatment) m;
                t.R = r.toString();
                r++;
            }
        }
        
        return model;
    }

    @Override
    public ModelXBase Clone(int sourceIndex, String newName){
        Treatment source = (Treatment) modelList.get(sourceIndex);
        Treatment newSource = null;
        
        try{            
            newSource = source.Clone();
            newSource.TNAME = newName;
        }
        catch(Exception ex){
            
        }
        
        return newSource;
    }
    
    @Override
    public ModelXBase GetAt(int level)
    {
        return modelList.get(level - 1);
    }

    @Override
    public boolean IsUseInTreatment(int level) {
        return false;
    }
    
    private String getRotationNumber(int level){
        Integer r = 0;
        for(ModelXBase model : modelList){
            Treatment treatment = (Treatment)model;
            if(treatment.GetLevel() == level && r < Utils.ParseInteger(treatment.R)){
                r = Utils.ParseInteger(treatment.R);
            }
        }
        r++;
        
        return r.toString();
    }
}
