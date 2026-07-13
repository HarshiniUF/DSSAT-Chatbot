/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package xbuild.Components;

import java.awt.Color;
import java.util.ArrayList;
import java.util.List;
import javax.swing.AbstractButton;
import javax.swing.ButtonGroup;
import javax.swing.GroupLayout;
import javax.swing.JRadioButton;
import org.jdesktop.swingx.JXRadioGroup;
import xbuild.ModelItem;

/**
 *
 * @author Jazzy
 */
public class XButtonGroup extends ButtonGroup {

    private Object model;
    private String fieldName;
    private String value;
    private List<ModelItem> modelItems;

    public XButtonGroup() {
    }

    public void Init(Object model, String fieldName, String value, ArrayList<String[]> items, RadioButtonAlignment aligment, JXRadioGroup groupButton) {
        this.model = model;
        this.fieldName = fieldName;
        this.value = value;

        this.modelItems = new ArrayList<>();
        items.forEach(sim -> {
            modelItems.add(new ModelItem(sim[0], sim[1]));
        });
        
        if (aligment == RadioButtonAlignment.Vertical)
            addRadioButtonVertical(groupButton);
        else if (aligment == RadioButtonAlignment.Horizontal)
            addRadioButtonHorizontal(groupButton);
        
        setSelectItem();
    }

    public void Init(Object model, String fieldName, String value, List<ModelItem> modelItems) {
        this.model = model;
        this.fieldName = fieldName;
        this.value = value;
        this.modelItems = modelItems;
        setSelectItem();
    }

    private void addRadioButtonVertical(JXRadioGroup groupButton) {
        javax.swing.GroupLayout jXRadioGroup1Layout = new javax.swing.GroupLayout(groupButton);
        groupButton.setLayout(jXRadioGroup1Layout);

        GroupLayout.ParallelGroup pp = jXRadioGroup1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING);
        GroupLayout.SequentialGroup sg = jXRadioGroup1Layout.createSequentialGroup().addContainerGap();

        this.modelItems.forEach(item -> {
            XRadioButton b = new XRadioButton();
            b.setText(item.description);
            groupButton.add(b);
            this.add(b);

            pp.addComponent(b, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE);

            sg.addComponent(b, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                    .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED);
        });

        jXRadioGroup1Layout.setHorizontalGroup(
                jXRadioGroup1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                        .addGroup(jXRadioGroup1Layout.createSequentialGroup()
                                .addContainerGap()
                                .addGroup(pp)
                                .addContainerGap(18, Short.MAX_VALUE))
        );

        jXRadioGroup1Layout.setVerticalGroup(
                jXRadioGroup1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                        .addGroup(sg)
        );
    }

    private void addRadioButtonHorizontal(JXRadioGroup groupButton) {

        javax.swing.GroupLayout jXRadioGroup2Layout = new javax.swing.GroupLayout(groupButton);
        groupButton.setLayout(jXRadioGroup2Layout);

        GroupLayout.SequentialGroup sg2 = jXRadioGroup2Layout.createSequentialGroup().addContainerGap();
        GroupLayout.ParallelGroup pl2 = jXRadioGroup2Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE);
        
        this.modelItems.forEach(item -> {
                    XRadioButton b = new XRadioButton();
                    b.setText(item.description);
                    groupButton.add(b);
                    this.add(b);

                    sg2.addComponent(b, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                    .addGap(18, 18, 18);

            pl2.addComponent(b, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE);
                });

        sg2.addContainerGap(102, Short.MAX_VALUE);

        jXRadioGroup2Layout.setHorizontalGroup(
                jXRadioGroup2Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                        .addGroup(sg2)
        );
        jXRadioGroup2Layout.setVerticalGroup(
                jXRadioGroup2Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                        .addGroup(pl2)
        );
    }

    private void setSelectItem() {
        for (int i = 0; i < this.getButtonCount(); i++) {
            AbstractButton b = this.buttons.get(i);
            String desc = "";
            for (ModelItem item : modelItems) {
                if (item.key.equalsIgnoreCase(value)) {
                    desc = item.description;
                    break;
                }
            }
            if (b.getText().equalsIgnoreCase(desc)) {
                ((XRadioButton) b).setSelectedItem(this.modelItems, value);
                b.setSelected(true);
                break;
            }
        }
    }
    
    public ArrayList<AbstractButton> GetButtons(){
        ArrayList<AbstractButton> btList = new ArrayList<>();
        for (int i = 0; i < this.getButtonCount(); i++) {
            btList.add(this.buttons.get(i));
        }
        return btList;
    }
    
    public AbstractButton GetSelected(){
        for (int i = 0; i < this.getButtonCount(); i++) {
            if(this.buttons.get(i).isSelected())
                return this.buttons.get(i);
        }
        
        return null;
    }

    @Override
    public void add(AbstractButton b) {
        super.add(b);

        ((XRadioButton) b).setSelectedItem(modelItems, value);

        b.addChangeListener((javax.swing.event.ChangeEvent evt) -> {
            buttonStateChanged(evt, (JRadioButton) b);
        });
    }

    private void buttonStateChanged(javax.swing.event.ChangeEvent evt, JRadioButton rdButton) {
        if (rdButton.isSelected()) {
            rdButton.setForeground(new Color(0, 150, 0));

            for (ModelItem item : modelItems) {
                if (rdButton.getText().equalsIgnoreCase(item.description)) {
                    this.value = item.key;
                    UpdateComponent.updateModel(this, model, fieldName, value);
                    break;
                }
            }
        } else {
            rdButton.setForeground(Color.BLACK);
        }
    }
}
