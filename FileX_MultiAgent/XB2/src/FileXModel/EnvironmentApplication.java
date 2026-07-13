/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package FileXModel;

import DSSATModel.EnvironmentFactor;
import java.util.Date;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 *
 * @author Jazzy
 */
public class EnvironmentApplication implements Cloneable {
    public Date ODATE;
    public Double EDAY;
    public EnvironmentFactor EDAY_Fact;
    public Double ERAD;
    public EnvironmentFactor ERAD_Fact;
    public Double EMAX;
    public EnvironmentFactor EMAX_Fact;
    public Double EMIN;
    public EnvironmentFactor EMIN_Fact;
    public Double ERAIN;
    public EnvironmentFactor ERAIN_Fact;
    public Double ECO2;
    public EnvironmentFactor ECO2_Fact;
    public Double EDEW;
    public EnvironmentFactor EDEW_Fact;
    public Double EWIND;
    public EnvironmentFactor EWIND_Fact;
    
    public Date getOrder(){
        return ODATE;
    }
    
    public EnvironmentApplication Clone(){
        try {
            return (EnvironmentApplication) this.clone();
        } catch (CloneNotSupportedException ex) {
            Logger.getLogger(EnvironmentApplication.class.getName()).log(Level.SEVERE, null, ex);
        }
        return null;
    }
}
