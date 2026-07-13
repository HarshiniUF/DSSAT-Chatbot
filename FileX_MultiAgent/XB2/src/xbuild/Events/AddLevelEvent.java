package xbuild.Events;

/**
 *
 * @author Jazz
 */
public class AddLevelEvent extends XBaseEvent {
    private String name;
    private String parent;
    
    public AddLevelEvent(Object o, String parent, String name){
        super(o);
        this.name = name;
        this.parent = parent;
    }
    
    public String getName(){
        return name;
    }
    
    public String getParent(){
        return parent;
    }
}
