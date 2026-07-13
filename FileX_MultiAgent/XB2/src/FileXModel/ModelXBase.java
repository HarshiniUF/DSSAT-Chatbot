package FileXModel;

/**
 *
 * @author Jazz
 */
public abstract class ModelXBase implements IModelXBase, Cloneable {
    private Integer level;
    
    public Integer GetLevel(){
        return level;
    }
    
    public void SetLevel(int level){
        this.level = level;
    }
    
    public ModelXBase Clone() throws CloneNotSupportedException{
        return (ModelXBase) clone();
    }
}
