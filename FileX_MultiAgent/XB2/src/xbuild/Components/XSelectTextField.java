/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package xbuild.Components;

import DSSATModel.BaseModel;
import java.lang.reflect.Field;
import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;
import javax.swing.JTextField;

/**
 *
 * @author Jazzy
 */
public class XSelectTextField extends JTextField {

    private Object model;
    private String fieldName;
    private Object value;
    private List<BaseModel> modelList;
    private String keyField;

    public XSelectTextField() {
    }
    
    public void Init(Object model, String fieldName, String value, List<BaseModel> modelList) {
        
        setValue(model, fieldName, value, modelList);

        if (value != null) {
            this.setText(value);
        }
    }
    
    public void Init(Object model, String fieldName, String value, List<BaseModel> modelList, String keyField) {
        setValue(model, fieldName, value, modelList);
        this.keyField = keyField;
        
        if (value != null) {
            this.setText(value);
        }
    }
    
    private void setValue(Object model, String fieldName, String value, List<BaseModel> modelList){
        this.model = model;
        this.fieldName = fieldName;
        this.value = value;
        this.modelList = modelList;
    }

    private void setFocusLost() {
        this.addFocusListener(new java.awt.event.FocusAdapter() {
            public void focusLost(java.awt.event.FocusEvent evt) {
                performFocusLost(evt);
            }
        });
    }

    public void performFocusLost(java.awt.event.FocusEvent evt) {
        String val = this.getText();
        if (val != null && !"".equals(val)) {
            this.value = val;
        } else {
            this.value = null;
        }

        UpdateComponent.updateModel(this, this.model, this.fieldName, this.value);
    }   

    @Override
    public void setText(String value) {
        for(BaseModel m : modelList){
            
            String code = "";
            if(this.keyField != null){
                try {
                    Field field = m.getClass().getDeclaredField(this.keyField);
                    code = field.get(m).toString();
                } 
                catch (IllegalArgumentException | IllegalAccessException | NoSuchFieldException | SecurityException ex) {
                    Logger.getLogger(XSelectTextField.class.getName()).log(Level.SEVERE, null, ex);
                }
            }
            else{
                code = m.Code;
            }
            
            if(code.equals(value)){
                super.setText(m.Description);
                this.value = value;
                UpdateComponent.updateModel(this, this.model, this.fieldName, this.value);
                break;
            }
        }
    }
}
