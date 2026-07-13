/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package DSSATModel;

/**
 *
 * @author Jazzy
 */
public class CropModel extends BaseModel {
    public String ModelCode;
    
    @Override
    public String toString(){
        return Description;
    }
    
    public int compare(CropModel c2){
        int compare = this.ModelCode.compareTo(c2.ModelCode);
        
        if(compare == 0){
            compare = this.Code.compareTo(c2.Code);
        }
        
        return compare;
    }
}
