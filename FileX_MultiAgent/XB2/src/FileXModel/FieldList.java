/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package FileXModel;

import Extensions.Utils;

/**
 *
 * @author Jazzy
 */
public class FieldList extends ManagementList {
    
    @Override
    public ModelXBase AddNew(String name, int newLevel, ModelXBase currentModel)
    {
        FieldDetail f = new FieldDetail(name);
        int expNo = GetSize() + Utils.ParseInteger(FileX.general.ExperimentNumber);
        f.ID_FIELD = FileX.general.InstituteCode + FileX.general.SiteCode + FileX.general.Year.substring(2) + Utils.PadLeft(expNo, 2, '0');
        modelList.add(f);
        f.SetLevel(newLevel);
        return f;
    }
    
    @Override
    public ModelXBase Clone(int sourceIndex, String newName){
        FieldDetail source = (FieldDetail) modelList.get(sourceIndex);
        FieldDetail newfield = null;
        
        try{
            newfield = source.clone();
            newfield.FLNAME = newName;
        }
        catch(Exception ex){
            
        }
        
        return newfield;
    }
    
    @Override
    public boolean IsUseInTreatment(int level) {
        boolean isUsed = false;
        
        for (ModelXBase treatment : FileX.treatments.GetAll()) {
            Treatment treat = (Treatment) treatment;
            if (treat.FL != null && treat.FL == level) {
                isUsed = true;
                break;
            }
        }
        return isUsed;
    }
}
