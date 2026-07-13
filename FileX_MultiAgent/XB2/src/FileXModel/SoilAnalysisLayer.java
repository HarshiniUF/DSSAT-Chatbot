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
public class SoilAnalysisLayer implements Cloneable {
    public Float SABL;
    public Float SADM;
    public Float SAOC;
    public Float SANI;
    public Float SAPHW;
    public Float SAPHB;
    public Float SAPX;
    public Float SAKE;
    public Float SASC;
    
    public Float getOrder(){
        return SABL;
    }
    
    public SoilAnalysisLayer Clone(){
        try {
            return (SoilAnalysisLayer) this.clone();
        } catch (CloneNotSupportedException ex) {
            Logger.getLogger(SoilAnalysisLayer.class.getName()).log(Level.SEVERE, null, ex);
        }
        return null;
    }
}
