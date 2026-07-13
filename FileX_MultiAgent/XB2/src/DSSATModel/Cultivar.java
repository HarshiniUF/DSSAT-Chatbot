/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package DSSATModel;

/**
 *
 * @author Jazzy
 */
public class Cultivar extends Crop {
    public String CulCode;
    public String CulName;

    public Cultivar()
    {

    }
    
    @Override
    public String toString(){
        return CulName;
    }

    public Cultivar(Crop crop) {
        CropCode = crop.CropCode;
        CropName = crop.CropName;
    }
}
