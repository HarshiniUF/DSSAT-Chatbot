/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package FileXModel;

/**
 *
 * @author Jazzy
 */
public class Treatment extends ModelXBase implements Cloneable {
    public Integer N;
    
    public String R;
    public String O;
    public String C;
    
    public String TNAME;
    public Integer CU;
    public Integer FL;
    public Integer SA;
    public Integer IC;
    public Integer MP;
    public Integer MI;
    public Integer MF;
    public Integer MR;
    public Integer MC;
    public Integer MT;
    public Integer ME;
    public Integer MH;
    public Integer SM;
    
    public Treatment(){
    }
    
    public Treatment(String name){
        TNAME = name;
    }
    
    @Override
    public Treatment Clone() throws CloneNotSupportedException {
        try {
            return (Treatment) super.clone();
        } catch (CloneNotSupportedException ex) {
        }
        return null;
    } 

    @Override
    public String GetName() {
        return TNAME;
    }

    @Override
    public void SetName(String name) {
        TNAME = name;
    }
    
    @Override
    public Integer GetLevel(){
        return N;
    }
    
    @Override
    public void SetLevel(int level){
        N = level;
        super.SetLevel(level);
    }
}
