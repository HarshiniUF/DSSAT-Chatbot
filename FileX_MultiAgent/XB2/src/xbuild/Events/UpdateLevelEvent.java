package xbuild.Events;


/**
 *
 * @author Jazz
 */
public class UpdateLevelEvent extends XBaseEvent {
    private String name;
    private String parent;
    private int row;
    
    public UpdateLevelEvent(Object o, String parent, String name, int row){
        super(o);
        this.name = name;
        this.parent = parent;
        this.row = row;
    }
    
    public String getName(){
        return name;
    }
    
    public String getParent(){
        return parent;
    }
    
    public int getRow(){
        return row;
    }
}
