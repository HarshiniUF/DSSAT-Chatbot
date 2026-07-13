package xbuild.Events;

public class LoadingDoneEvent extends XBaseEvent {    
    private boolean valid;
    
    public LoadingDoneEvent(Object source, boolean valid) {
        super(source);
        this.valid = valid;
    }
    
    public boolean isValid(){
        return valid;
    }
}
