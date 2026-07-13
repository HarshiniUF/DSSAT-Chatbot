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
public class OrganicApplication implements Cloneable {
    public Date RDATE;
    public Integer RDAY;
    public String RCOD;
    public Integer RAMT;
    public Float RESN;
    public Float RESP;
    public Float RESK;
    public Integer RINP;
    public Integer RDEP;
    public String RMET;
    
    public Date getOrder(){
        return RDATE;
    }
    
    public int getOrderDay(){
        return RDAY;
    }
    
    public OrganicApplication Clone(){
        try {
            return (OrganicApplication) this.clone();
        } catch (CloneNotSupportedException ex) {
            Logger.getLogger(OrganicApplication.class.getName()).log(Level.SEVERE, null, ex);
        }
        return null;
    }
}
