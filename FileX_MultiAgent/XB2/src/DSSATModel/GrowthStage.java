/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package DSSATModel;

/**
 *
 * @author Jazzy
 */
public class GrowthStage {
    public String Code;
    public String Name;
    public String Description;
    public Crop crop;
    
    @Override
    public String toString(){
        return Description;
    } 
}
