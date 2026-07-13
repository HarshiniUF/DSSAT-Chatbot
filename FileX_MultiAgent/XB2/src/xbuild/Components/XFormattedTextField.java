/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package xbuild.Components;

import javax.swing.JFormattedTextField;

/**
 *
 * @author Jazzy
 */
public class XFormattedTextField extends JFormattedTextField {
    private Object model;
    private String fieldName;
    private Object value;
    private FieldType fieldType;

    public XFormattedTextField() {
    }
    
    public void Init(Object model, String fieldName, String value) {
        setValue(model, fieldName, value);
        fieldType = FieldType.String;
    }

    public void Init(Object model, String fieldName, Float value) {
        setValue(model, fieldName, value);
        fieldType = FieldType.Float;
    }
    
    public void Init(Object model, String fieldName, Integer value) {
        setValue(model, fieldName, value);
        fieldType = FieldType.Integer;
    }

    private void setValue(Object model, String fieldName, Object value) {
        this.model = model;
        this.fieldName = fieldName;
        this.value = value;
        
        if(value != null){
            this.setValue(value);
        }

        setFocusLost();
    }
     
     private void setFocusLost(){
        this.addFocusListener(new java.awt.event.FocusAdapter(){
            @Override
            public void focusLost(java.awt.event.FocusEvent evt) {
                performFocusLost(evt);
            }
        });
    }
     
     public void performFocusLost(java.awt.event.FocusEvent evt) {
        String val = this.getText();
        if (val != null && !"".equals(val)) {
            switch (this.fieldType) {
                case String:
                    this.value = val;
                    break;
                case Float:
                    try {
                        this.value = Float.valueOf(val);
                    } catch (NumberFormatException ex) {
                        this.value = null;
                    }
                    break;

                case Integer:
                    try {
                        this.value = Integer.valueOf(val);
                    } catch (NumberFormatException ex) {
                        this.value = null;
                    }
                    break;

            }
        } else {
            this.value = null;
        }
        
        UpdateComponent.updateModel(this, this.model, this.fieldName, this.value);
    }
}
