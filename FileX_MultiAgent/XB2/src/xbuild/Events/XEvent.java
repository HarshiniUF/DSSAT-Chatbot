/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package xbuild.Events;

/**
 *
 * @author Jazzy
 */
public class XEvent extends XBaseEvent {
    String n;
    public XEvent(Object o, String n)
    {
        super(o);
        this.n = n;
    }
    
    XEvent(Object o)
    {
        super(o);
    }

    public String getN()
    {
        return n;
    }
}
