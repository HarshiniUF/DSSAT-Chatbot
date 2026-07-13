package xbuild.Components;

import DSSATModel.CropList;
import FileXModel.Cultivar;
import FileXModel.FileX;
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
public class CultivarTableCellEditor extends AbstractCellEditor implements TableCellEditor  {

    private final XDropdownTableComboBox<CropTreatment> combo;
    
    public CultivarTableCellEditor(){
        combo = new XDropdownTableComboBox<>();        
        
        List<CropTreatment> crList = new ArrayList<>();
        CropTreatment crNone = new CropTreatment();
        crNone.level = 0;
        crNone.cropName = "NONE";
        crNone.cultivar = "";
        crList.add(crNone);
        
        for(int i = 0;i < FileX.cultivars.GetSize();i++)
        {
            Cultivar cul = (Cultivar) FileX.cultivars.GetAtIndex(i);
            CropTreatment cr = new CropTreatment();
            cr.level = cul.GetLevel();
            try {
                cr.cropName = CropList.GetAt(cul.CR).CropName;
            } catch (Exception e) {
                 cr.cropName = "";
            }
            try {
                cr.cultivar = cul.CNAME;
            } catch (Exception e) {
                cr.cultivar = "";
            }
            crList.add(cr);
        }
        
        combo.setInit(null, "level", "0", crList, 
                new XColumn[] { 
                    new  XColumn("level", "Level", 50),
                    new  XColumn("cropName", "Crop Name", 100),
                    new  XColumn("cultivar", "Culltivar", 250)
                }, "level");
    }
    
    @Override
    public Object getCellEditorValue() {        
        return ((CropTreatment)combo.getSelectedItem()).level;
    }

    @Override
    public Component getTableCellEditorComponent(JTable table, Object value, boolean isSelected, int row, int column) {
        if (value != null) {
            combo.setSelectedIndex((int)value);
        }
        
        return combo;
    }
    
    private class CropTreatment{
        public int level;
        public String cropName;
        public String cultivar;
        
        @Override
        public String toString(){
            return "" + level;
        }
    }
}
