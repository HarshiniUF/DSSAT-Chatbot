package FileXModel;

import java.util.ArrayList;

/**
 *
 * @author Jazzy
 */
public abstract class ManagementList {
    protected ArrayList<ModelXBase> modelList = new ArrayList<>();
    
    public abstract ModelXBase AddNew(String name, int newLevel, ModelXBase currentModel);
    public abstract ModelXBase Clone(int sourceIndex, String newName);
    public abstract boolean IsUseInTreatment(int level);
    
    public void AddNew(ModelXBase model){
        modelList.add(model);
    }
    
    public ArrayList<ModelXBase> GetAll(){
        return modelList;
    }
    
    public int GetSize(){
        return modelList.size();
    }
    
    public void RemoveAt(String name)
    {
        for(ModelXBase model : GetAll()){
            if(model.GetName().equals(name)){
                modelList.remove(model);
                break;
            }
        }
    }
    
    public void RemoveAt(int level)
    {
        modelList.remove(level);
    }
    
    public ModelXBase GetAt(String name)
    {
        name = ExtractDescription(name);
        for(ModelXBase model : GetAll()){
            if(model.GetName().equals(name)){
                return model;
            }
        }
        return null;
    }
    
    public int GetIndex(int level){
        int index = 0;
        for(ModelXBase model : GetAll()){
            if(model.GetLevel() == level){
                return index;
            }
            index++;
        }
        
        return -1;
    }
    
    public int GetIndex(ModelXBase model){
        int index = 1;
        for(ModelXBase x : GetAll()){
            if(model == x){
                return index;
            }
            index++;
        }
        
        return -1;
    }
    
    public ModelXBase GetAtIndex(int index){
        return modelList.get(index);
    }
    
    public ModelXBase GetAt(int level)
    {
        for(ModelXBase model : GetAll()){
            if(model.GetLevel() == level){
                return model;
            }
        }
        return null;
    }
    
    public int GetLevel(String name)
    {
        for(ModelXBase model : GetAll()){
            if(model.GetName().equals(name)){
                return model.GetLevel();
            }
        }
        return 0;
    }
    
    public boolean IsLevelExists(int level){
        for(ModelXBase model : GetAll()){
            if(model.GetLevel() == level){
                return true;
            }
        }
        return false;
    }
    
    public Boolean MoveUp(int level){
        if(level > 0 && GetSize() > 1){
            ModelXBase tmp = modelList.get(level);
            ModelXBase tmp2 = modelList.get(level - 1);
            int levelTmp1 = tmp.GetLevel();
            int levelTmp2 = tmp2.GetLevel();
            tmp.SetLevel(levelTmp2);
            tmp2.SetLevel(levelTmp1);
            modelList.set(level, tmp2);
            modelList.set(level - 1, tmp);
            return true;
        }
        return false;
    }
    
    public Boolean MoveDown(int level){
        if(level < GetSize() - 1 && GetSize() > 1){

            ModelXBase tmp = modelList.get(level);
            ModelXBase tmp2 = modelList.get(level + 1);
            int levelTmp1 = tmp.GetLevel();
            int levelTmp2 = tmp2.GetLevel();
            tmp.SetLevel(levelTmp2);
            tmp2.SetLevel(levelTmp1);
            modelList.set(level, tmp2);
            modelList.set(level + 1, tmp);
            return true;
        }
        return false;
    }
    
    public String GetCopyName(String name){
        int max = 0;
        for(ModelXBase model : GetAll()){
            if(model.GetName().startsWith(name)){
                max++;
            }
        }
        
        return name + " (" + (max + 1) + ")";
    }
    
    public void Rename(String oldName, String newName){
        for(ModelXBase model : GetAll()){
            if(model.GetName().equals(oldName)){
                model.SetName(newName);
                break;
            }
        }
    }
    
    public String ExtractDescription(String name){
        String description = name;
 
        if(name.matches("^Level\\s[0-9]+?[?::].*")){
            description = name.split(":")[1].trim();
        }
        
        return description;
    }
    
    public int ExtractLevel(String name){
        int level = -1;
        if(name.matches("^Level\\s[0-9]+?[?::].*")){
            level = Integer.parseInt(name.split(":")[0].split(" ")[1].trim());
        }
        
        return level;
    } 
}
