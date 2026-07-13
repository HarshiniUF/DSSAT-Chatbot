/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package FileXModel;

/**
 *
 * @author Jazzy
 */
public class Cultivar extends ModelXBase {
    public String CR;
    public String INGENO;
    public String CNAME;
    
    public Cultivar(){
    }
    
    public Cultivar(String name){
        CNAME = name;
    }

    @Override
    public String GetName() {
        return this.CNAME == null ? "" : this.CNAME;
    }
    
    @Override
    public void SetName(String name) {
        CNAME = name;
    }
}
