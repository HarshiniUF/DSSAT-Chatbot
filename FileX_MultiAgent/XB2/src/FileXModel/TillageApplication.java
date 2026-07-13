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
public class TillageApplication implements Cloneable {
    public Date TDATE;
    public Integer TDAY;
    public String TIMPL;
    public Integer TDEP;
    
    public Date getOrder(){
        return TDATE;
    }
    
    public Integer getOrderDay(){
        return TDAY;
    }
    
    public TillageApplication Clone(){
        try {
            return (TillageApplication) this.clone();
        } catch (CloneNotSupportedException ex) {
            Logger.getLogger(TillageApplication.class.getName()).log(Level.SEVERE, null, ex);
        }
        
        return null;
    }
}
