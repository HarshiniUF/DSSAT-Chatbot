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
public class HarvestApplication implements Cloneable {
    public Date HDATE;
    public Integer HDAY;
    public String HSTG;
    public String HCOM;
    public String HSIZE;
    public Float HPC;
    public Float HBPC;
    
    public Date getOrder(){
        return HDATE;
    }
    
    public Integer getOrderDay(){
        return HDAY;
    }
    
    public HarvestApplication Clone(){
        try {
            return (HarvestApplication) this.clone();
        } catch (CloneNotSupportedException ex) {
            Logger.getLogger(HarvestApplication.class.getName()).log(Level.SEVERE, null, ex);
        }
        return null;
    }
}
