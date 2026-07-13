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
public class FertilizerApplication implements Cloneable {
    public Date FDATE;
    public Integer FDAY;
    public String FMCD;
    public String FACD;
    public Float FDEP;
    public Float FAMN;
    public Float FAMP;
    public Float FAMK;
    public Float FAMC;
    public Float FAMO;
    public String FOCD;
    
    public Date getOrder(){
        return FDATE;
    }
    
    public Integer getOrderDay(){
        return FDAY;
    }
    
    public FertilizerApplication Clone(){
        try {
            return (FertilizerApplication) this.clone();
        } catch (CloneNotSupportedException ex) {
            Logger.getLogger(FertilizerApplication.class.getName()).log(Level.SEVERE, null, ex);
        }
        return null;
    }
}
