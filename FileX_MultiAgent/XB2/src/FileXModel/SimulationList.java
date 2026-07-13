/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package FileXModel;

import DSSATModel.CropModel;
import DSSATModel.CropModelList;
import DSSATModel.SimulationControlDefaults;

/**
 *
 * @author Jazzy
 */
public class SimulationList extends ManagementList {   
    @Override
    public ModelXBase AddNew(String name, int newLevel, ModelXBase currentModel) {
        Simulation model = SimulationControlDefaults.Get(FileX.general.FileType);
        model.SetName(name);
        
        String cropCode = FileX.general.crop.CropCode;
        if("".equals(cropCode) && FileX.cultivars.GetSize() > 0){
            Cultivar cul = (Cultivar) FileX.cultivars.GetAt(newLevel <= FileX.cultivars.GetSize() ? newLevel : FileX.cultivars.GetSize());
            cropCode = cul.CR;
        }
        
        CropModel cm = CropModelList.GetByCrop(cropCode);        
        
        if (cm != null) {
            model.SMODEL = cm.ModelCode;
        }
        if (FileX.plantings.GetSize() > 0 && newLevel <= FileX.plantings.GetSize()) {
            Planting pl = (Planting) FileX.plantings.GetAt(newLevel);
            model.SDATE = pl.PDATE;
        }
        
        modelList.add(model);
        model.SetLevel(newLevel);
        return model;
    }
    
    @Override
    public ModelXBase Clone(int sourceIndex, String newName){
        Simulation source = (Simulation) modelList.get(sourceIndex);
        Simulation newSim = null;
        
        try{
            newSim = source.clone();
            newSim.SNAME = newName;
        }
        catch(CloneNotSupportedException ex){
            
        }
        
        return newSim;
    }
    
    @Override
    public boolean IsUseInTreatment(int level) {
        boolean isUsed = false;
        
        for (ModelXBase treatment : FileX.treatments.GetAll()) {
            Treatment treat = (Treatment) treatment;
            if (treat.SM != null && treat.SM == level) {
                isUsed = true;
                break;
            }
        }
        return isUsed;
    }
}
