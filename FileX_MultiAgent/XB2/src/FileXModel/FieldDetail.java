/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package FileXModel;

/**
 *
 * @author Jazzy
 */
public class FieldDetail extends ModelXBase implements Cloneable {
    public String FLNAME;
    
    public FieldDetail(){
        
    }
    
    public FieldDetail(String FLNAME) {
        this.FLNAME = FLNAME;
    }

    public String ID_FIELD;
    public String WSTA;
    public Float FLSA;
    public Float FLOB;
    public String FLDT;
    public Float FLDD;
    public Float FLDS;
    public String FLST;
    public String SLTX;
    public Float SLDP;
    public String ID_SOIL;
    public Float XCRD;
    public Float YCRD;
    public Float ELEV;
    public Float AREA;
    public Float SLEN;
    public Float FLWR;
    public Float SLAS;
    public String FLHST;
    public Float FHDUR;
    public Float PMALB;
    public Integer BDWD;
    public Integer BDHT;
    
    public FieldDetail clone() throws CloneNotSupportedException {
        return (FieldDetail)super.clone();
    }
    
    @Override
    public String GetName(){
        return this.FLNAME == null ? "" : this.FLNAME;
    }
    
    @Override
    public void SetName(String name) {
        FLNAME = name;
    }
}
