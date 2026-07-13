/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package xbuild.Components;

import Extensions.Utils;
import java.awt.EventQueue;
import java.util.ArrayList;
import java.util.List;
import javax.swing.DefaultComboBoxModel;
import javax.swing.JComboBox;

/**
 *
 * @author Jazzy
 */
public class XComboBox extends JComboBox {

    private Object model;
    private String fieldName;
    private String value;
    private List<XComboBoxItem> items;
    private int index;

    public XComboBox() {
    }

    public XComboBox(Object model, String fieldName, String value, List<XComboBoxItem> items) {
        this.model = model;
        this.fieldName = fieldName;
        this.value = value;
        this.items = items;

        List<String> modelItems = new ArrayList();
        items.forEach(x -> modelItems.add(x.item));

        this.setModel(new javax.swing.DefaultComboBoxModel(modelItems.toArray()));

        if (value == null || "".equals(value)) {
            this.value = items.get(0).index;
            UpdateComponent.updateModel(this, this.model, this.fieldName, this.value);
        } else {
            for (int i = 0; i < items.size(); i++) {
                if (items.get(i).index.equals(value)) {
                    index = i;
                    Utils.setTimeout(() -> this.setSelectedIndex(index), 100);
                    break;
                }
            }
        }

        setAction();
    }
    
    public void setInit(Object model, String fieldName, String value, List<String> items) {
        this.model = model;
        this.fieldName = fieldName;
        this.value = value;
        this.items = new ArrayList<>();
        for(Integer i = 0; i< items.size();i++){
            this.items.add(new XComboBoxItem(i.toString(), items.get(i)));
        }

        List<String> modelItems = new ArrayList();
        this.items.forEach(x -> modelItems.add(x.item));

        this.setModel(new javax.swing.DefaultComboBoxModel(modelItems.toArray()));

        if(model != null){
            if (value == null || "".equals(value)) {
                this.value = !this.items.isEmpty() ? this.items.get(0).index : "";
                UpdateComponent.updateModel(this, this.model, this.fieldName, this.value);
            } else {
                for (int i = 0; i < this.items.size(); i++) {
                    if (this.items.get(i).index.equals(value) || this.items.get(i).item.equals(value)) {
                        index = i;
                        EventQueue.invokeLater(() -> this.setSelectedIndex(index));
                        break;
                    }
                }
            }

            setAction();
        }
    }
    
    public void setInit(Object model, String fieldName, String value){
        DefaultComboBoxModel<String> d = (DefaultComboBoxModel) this.getModel();
        List<String> modelItems = new ArrayList();
        for(int i = 0; i < d.getSize();i++){
            modelItems.add(d.getElementAt(i));
        }
        setInit(model, fieldName, value, modelItems);
    }
    public void setModel(List<String> items, String selectedCode){
        this.items = new ArrayList<>();
        for(Integer i = 0; i< items.size();i++){
            this.items.add(new XComboBoxItem(i.toString(), items.get(i)));
        }

        List<String> modelItems = new ArrayList();
        this.items.forEach(x -> modelItems.add(x.item));

        this.setModel(new javax.swing.DefaultComboBoxModel(modelItems.toArray()));

        this.setSelectedItem(selectedCode);
        
        if (value == null || "".equals(value)) {
            this.value = this.items.get(0).index;
            UpdateComponent.updateModel(this, this.model, this.fieldName, this.value);
        } else {
            for (int i = 0; i < this.items.size(); i++) {
                if (this.items.get(i).index.equals(value)) {
                    index = i;
                    EventQueue.invokeLater(() -> this.setSelectedIndex(index));
                    break;
                }
            }
        }
    }

    private void setAction() {
        this.addActionListener((java.awt.event.ActionEvent evt) -> {
            performFocusLost(evt);
        });
    }

    public void performFocusLost(java.awt.event.ActionEvent evt) {
        int index = this.getSelectedIndex();
        if(index >= 0){
                this.value = items.get(index).item;
            UpdateComponent.updateModel(this, this.model, this.fieldName, this.value);
        }
        else{
            UpdateComponent.updateModel(this, this.model, this.fieldName, "");
        }
    }
}
