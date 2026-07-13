package xbuild.Components;

import FileXModel.ManagementList;
import FileXModel.ModelXBase;
import java.awt.Component;
import java.util.ArrayList;
import java.util.List;
import javax.swing.AbstractCellEditor;
import javax.swing.JTable;
import javax.swing.table.TableCellEditor;

/**
 *
 * @author JAZZJAIKLA
 */
public class TreatmentTableCellEditor extends AbstractCellEditor implements TableCellEditor  {
    private final XDropdownTableComboBox<TreatmentDetail> combo;
    
    public TreatmentTableCellEditor(ManagementList modelList){
        combo = new XDropdownTableComboBox<>();        
        
        List<TreatmentDetail> list = new ArrayList<>();
        TreatmentDetail crNone = new TreatmentDetail();
        crNone.level = 0;
        crNone.description = "NONE";
        list.add(crNone);
        
        for(int i = 0;i < modelList.GetSize();i++)
        {
            ModelXBase model = (ModelXBase) modelList.GetAtIndex(i);
            TreatmentDetail s = new TreatmentDetail();
            s.level = model.GetLevel();
            s.description = model.GetName();
            list.add(s);
        }
        
        combo.setInit(null, "level", "0", list, 
                new XColumn[] { 
                    new  XColumn("level", "Level", 50),
                    new  XColumn("description", "Description", 250)
                }, "level");
    }
    
    @Override
    public Object getCellEditorValue() {        
        return ((TreatmentDetail)combo.getSelectedItem()).level;
    }

    @Override
    public Component getTableCellEditorComponent(JTable table, Object value, boolean isSelected, int row, int column) {
        if (value != null) {
            combo.setSelectedIndex((int)value);
        }
        
        return combo;
    }
    
    private class TreatmentDetail {
        public int level;
        public String description;
        
        @Override
        public String toString(){
            return "" + level;
        }
    }
}
