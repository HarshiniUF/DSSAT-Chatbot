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
public class ChemicalApplication implements Cloneable {
    public Date CDATE;
    public Integer CDAY;
    public String CHCOD;
    public Float CHAMT;
    public String CHME;
    public Integer CHDEP;
    public String CHT;
    
    public Date getOrder(){
        return CDATE;
    }
    
    public Integer getOrderDay(){
        return CDAY;
    }
    
    public ChemicalApplication Clone(){
        try {
            return (ChemicalApplication) this.clone();
        } catch (CloneNotSupportedException ex) {
            Logger.getLogger(ChemicalApplication.class.getName()).log(Level.SEVERE, null, ex);
        }
        return null;
    }
}
