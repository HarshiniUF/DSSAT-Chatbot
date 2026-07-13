/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package DSSATModel;

/**
 *
 * @author Jazzy
 */
public class Crop implements Cloneable {
    public String CropCode;
    public String CropName;
    public boolean Enabled;
    
    public Crop(){
        CropCode = "";
        CropName = "";
        Enabled = true;
    }
    
    @Override
    public String toString(){
        return CropName;
    }
    
    @Override
    public Crop clone() throws CloneNotSupportedException{
        return (Crop)super.clone();
    }
}
