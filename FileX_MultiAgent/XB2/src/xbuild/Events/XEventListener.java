/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package xbuild.Events;

/**
 *
 * @author Jazzy
 */
public interface XEventListener {
    public abstract void myAction (XEvent e);
    public abstract void myAction (AddLevelEvent e);
    public abstract void myAction (RemoveLevelEvent e);
    public abstract void myAction (UpdateLevelEvent e);
    public abstract void myAction (ValidationEvent e);
    public abstract void myAction (NewFrameEvent e);
    public abstract void myAction (SelectionEvent e);
    public abstract void myAction (FieldUpdateEvent e);
    public abstract void myAction (LevelSelectionChangedEvent e);
}
