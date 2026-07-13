/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package xbuild.Components;

import java.util.List;
import javax.swing.JRadioButton;
import xbuild.ModelItem;

/**
 *
 * @author Jazzy
 */
public class XRadioButton extends JRadioButton {
    
    private List<ModelItem> modelItems;
    private String value;

    public XRadioButton() {
    }
    
    public void setSelectedItem(List<ModelItem> modelItems, String value){
        this.modelItems = modelItems;
        this.value = value;
    }
    
    @Override
    public void setText(String text){
        super.setText(text);
        
        if(value != null && !"".equals(value)){
            for(ModelItem item : modelItems){
                if(text.equalsIgnoreCase(item.description) && value.equalsIgnoreCase(item.key)){
                    this.setSelected(true);
                    break;
                }
            }
        }
    }
}
