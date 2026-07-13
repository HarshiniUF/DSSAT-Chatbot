package xbuild.Events;

/**
 *
 * @author JAZZJAIKLA
 */
public class SelectionEvent extends XBaseEvent {
    
    private boolean canDel;
    
    public SelectionEvent(Object source, boolean canDel) {
        super(source);
        
        this.canDel = canDel;
    }
    
    public boolean canDelete(){
        return canDel;
    }    
}
