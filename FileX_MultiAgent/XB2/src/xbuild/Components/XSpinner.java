/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package xbuild.Components;

import Extensions.Utils;
import javax.swing.JSpinner;
import javax.swing.JTextField;
import javax.swing.event.ChangeListener;

/**
 *
 * @author Jazzy
 */
public class XSpinner extends JSpinner {
    
    private JTextField textField;
    private Object value;
    private Object model;
    private String fieldName;
    private FieldType fieldType;

    public XSpinner() {
    }
    
    public void Init(Object model, String fieldName, Integer value){
        ChangeListener[] listens = this.getListeners(ChangeListener.class);
        for(ChangeListener li : listens)
            this.removeChangeListener(li);
        
        DefaultEditor editor = (DefaultEditor)this.getEditor();
        this.textField = (JTextField)editor.getTextField();
        this.model = model;
        this.fieldName = fieldName;
        this.value = value;
        fieldType = FieldType.Integer;
        
        if(value == null)
            setBlank();
        else
            this.setValue(value);

        setFocusLost();
        
        for(ChangeListener li : listens)
            this.addChangeListener(li);
    }
    
    public void Init(Object model, String fieldName, Float value){
        ChangeListener[] listens = this.getListeners(ChangeListener.class);
        for(ChangeListener li : listens)
            this.removeChangeListener(li);
        
        DefaultEditor editor = (DefaultEditor)this.getEditor();
        this.textField = (JTextField)editor.getTextField();
        this.model = model;
        this.fieldName = fieldName;
        this.value = value;
        fieldType = FieldType.Float;
        
        if(value == null)
            setBlank();
        else
            this.setValue(value);
        
        setFocusLost();
        
        for(ChangeListener li : listens)
            this.addChangeListener(li);
    }
    
    private void setFocusLost(){
        this.textField.addFocusListener(new java.awt.event.FocusAdapter(){
            @Override
            public void focusLost(java.awt.event.FocusEvent evt) {
                performFocusLost(evt);
            }
        });
    }
    
    public void performFocusLost(java.awt.event.FocusEvent evt){
        if("".equals(this.textField.getText())){
            setBlank();
        }
        else{
            Utils.setTimeout(() -> {
                this.value = this.getValue();
                UpdateComponent.updateModel(this, this.model, this.fieldName, this.value.toString());
            }, 100);
        }
    }
    
    private void setBlank(){
        Utils.setTimeout(() -> {
            this.textField.setText("");
            this.value = null;
            UpdateComponent.updateModel(this, this.model, this.fieldName, this.value);
        }, 300);
    }
    
    @Override
    public Object getValue(){
        try{
        if(this.textField == null || "".equals(this.textField.getText())){
            return null;
        }
        else{
            String val = this.textField.getText();
            switch (this.fieldType) {
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
            return this.value;
        }
        }
        catch(Exception ex){
            return null;
        }
    }
    
    @Override
    public void setValue(Object value){
        super.setValue(value);
        if(value != null)
            this.textField.setText(value.toString());
        else
            this.textField.setText("");
    }
}
