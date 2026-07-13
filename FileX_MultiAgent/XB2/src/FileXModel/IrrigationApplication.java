/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package FileXModel;

import java.util.Date;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 *
 * @author Jazzy
 */
public class IrrigationApplication implements Cloneable {
    public Date IDATE;
    public Integer IDAY;
    public String IROP;
    public Float IRVAL;
    
    public Date getOrder(){
        return IDATE;
    }
    
    public Integer getOrderDay() {
        return IDAY;
    }
    
    public IrrigationApplication Clone(){
        try {
            return (IrrigationApplication) this.clone();
        } catch (CloneNotSupportedException ex) {
            Logger.getLogger(IrrigationApplication.class.getName()).log(Level.SEVERE, null, ex);
        }
        
        return null;
    }
}
