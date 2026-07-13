package xbuild.Components;

import Extensions.LimitDocument;
import java.awt.Component;
import javax.swing.AbstractCellEditor;
import javax.swing.JTable;
import javax.swing.JTextField;
import javax.swing.table.TableCellEditor;

/**
 *
 * @author JAZZJAIKLA
 */
public class DescriptionTableCellEditor extends AbstractCellEditor implements TableCellEditor  {

    private final JTextField textEditor;
    public DescriptionTableCellEditor(){
        textEditor = new JTextField();
        textEditor.setDocument(new LimitDocument(25));
    }
    
    @Override
    public Component getTableCellEditorComponent(JTable table, Object value, boolean isSelected, int row, int column) {
        textEditor.setText(value.toString());
        
        return textEditor;
    }

    @Override
    public Object getCellEditorValue() {
        return textEditor.getText();
    }
}
