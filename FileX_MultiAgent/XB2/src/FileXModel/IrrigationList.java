/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package FileXModel;

/**
 *
 * @author Jazzy
 */
public class IrrigationList extends ManagementList {
    
    @Override
    public ModelXBase AddNew(String name, int newLevel, ModelXBase currentModel) {
        Irrigation model = new Irrigation(name);
        modelList.add(model);
        model.SetLevel(newLevel);
        return model;
    }
    
    public ModelXBase Clone(int sourceIndex, String newName){
        Irrigation source = (Irrigation) modelList.get(sourceIndex);
        Irrigation newSource = null;
        
        try{
            newSource = new Irrigation();
            newSource.IRNAME = newName;
            
            if(source.EFIR != null){
                newSource.EFIR = source.EFIR;
            }
            
            if(source.IAME != null){
                newSource.IAME = source.IAME;
            }
            
            if(source.IAMT != null){
                newSource.IAMT = source.IAMT;
            }
            
            if(source.IDEP != null){
                newSource.IDEP = source.IDEP;
            }
            
            if(source.IEPT != null){
                newSource.IEPT = source.IEPT;
            }
            
            if(source.IOFF != null){
                newSource.IOFF = source.IOFF;
            }
            
            if(source.ITHR != null){
                newSource.ITHR = source.ITHR;
            }
            
            for(IrrigationApplication ir : source.GetApps()) {
                IrrigationApplication ia = (IrrigationApplication) ir.Clone();                
                newSource.AddApp(ia);
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
            if (treat.MI != null && treat.MI == level) {
                isUsed = true;
                break;
            }
        }
        return isUsed;
    }
}
