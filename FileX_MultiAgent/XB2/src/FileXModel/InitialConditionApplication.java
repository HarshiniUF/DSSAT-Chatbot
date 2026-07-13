/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package FileXModel;

import java.util.logging.Level;
import java.util.logging.Logger;

/**
 *
 * @author Jazzy
 */
public class InitialConditionApplication implements Cloneable {
    public Float ICBL;
    public Float SH2O;
    public Float SNH4;
    public Float SNO3;
    
    public Float getOrder(){
        return ICBL;
    }
    
    public InitialConditionApplication Clone(){
        try {
            return (InitialConditionApplication) this.clone();
        } catch (CloneNotSupportedException ex) {
            Logger.getLogger(InitialConditionApplication.class.getName()).log(Level.SEVERE, null, ex);
        }
        return null;
    }
}
