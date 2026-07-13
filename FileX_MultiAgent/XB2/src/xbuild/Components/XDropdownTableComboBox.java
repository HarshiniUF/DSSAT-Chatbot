package xbuild.Components;

import java.awt.Color;
import java.awt.Component;
import java.awt.Dimension;
import java.awt.EventQueue;
import java.awt.Insets;
import java.awt.Point;
import java.awt.event.ItemEvent;
import java.awt.event.ItemListener;
import java.awt.event.KeyAdapter;
import java.awt.event.KeyEvent;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.lang.reflect.Field;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;
import javax.swing.BorderFactory;
import javax.swing.DefaultComboBoxModel;
import javax.swing.JComboBox;
import javax.swing.JScrollPane;
import javax.swing.JTable;
import javax.swing.ListSelectionModel;
import javax.swing.RowSorter.SortKey;
import javax.swing.SortOrder;
import javax.swing.event.RowSorterEvent;
import javax.swing.plaf.basic.BasicComboPopup;
import javax.swing.plaf.basic.ComboPopup;
import javax.swing.plaf.metal.MetalComboBoxUI;
import javax.swing.table.DefaultTableModel;
import javax.swing.table.TableCellRenderer;
import javax.swing.table.TableRowSorter;
import org.jdesktop.swingx.autocomplete.AutoCompleteDecorator;

/**
 *
 * @author Jazzy
 * @param <E>
 */
public class XDropdownTableComboBox<E extends Object> extends JComboBox<E> {

    //private String fieldName;
    private String value;
    private String codeField;

    protected transient HighlightListener highlighter = new HighlightListener();
    protected JTable table = new JTable() {
        @Override
        public Component prepareRenderer(TableCellRenderer renderer, int row, int column) {
            Component c = super.prepareRenderer(renderer, row, column);
            c.setForeground(Color.BLACK);
            if (highlighter.isHighlightableRow(row)) {
                c.setBackground(new Color(201, 226, 250));
            } else if (isRowSelected(row)) {
                c.setBackground(new Color(184, 207, 229));
            } else {
                c.setBackground(Color.WHITE);
            }

            return c;
        }

        @Override
        public void updateUI() {
            removeMouseListener(highlighter);
            removeMouseMotionListener(highlighter);
            super.updateUI();
            addMouseListener(highlighter);
            addMouseMotionListener(highlighter);
            getTableHeader().setReorderingAllowed(false);
        }
    };
    protected List<E> list;
    protected XColumn[] columns;

    public XDropdownTableComboBox() {
        super();
    }

    public void setInit(E model, String fieldName, String value, List<E> list, XColumn[] columns, String codeField) {
        //this.model = model;
        //this.fieldName = fieldName;
        DefaultComboBoxModel<E> cbModel = (DefaultComboBoxModel<E>) this.getModel();
        cbModel.removeAllElements();

        this.value = value;
        this.codeField = codeField;

        this.list = list;
        this.columns = columns;

        ItemListener[] listens = this.getItemListeners();

        for (ItemListener li : listens) {
            this.removeItemListener(li);
        }

        DefaultTableModel dropDownModel = getDataModel();

        table.setModel(dropDownModel);
        table.setAutoCreateRowSorter(true);

        TableRowSorter<DefaultTableModel> sorter = (TableRowSorter<DefaultTableModel>) table.getRowSorter();
        sorter.addRowSorterListener((RowSorterEvent e) -> {
            List<? extends SortKey> rowSorter = table.getRowSorter().getSortKeys();
            if (rowSorter != null && !rowSorter.isEmpty()) {

                if (rowSorter.get(0).getSortOrder() == SortOrder.ASCENDING) {
                    orderByAscending(rowSorter.get(0).getColumn());
                } else {
                    orderByDescending(rowSorter.get(0).getColumn());
                }
            }
        });

        for (int c = 0; c < table.getColumnCount(); c++) {
            table.getColumnModel().getColumn(c).setPreferredWidth(columns[c].getWidth());
        }

        list.forEach(this::addItem);

        setEditable(true);

        AutoCompleteDecorator.decorate(this);

        int index = -1;
        setSelectedIndex(index);
        for (E dataModel : list) {
            index++;
            try {
                if (getFieldValue(dataModel, this.codeField) == null ? this.value == null : getFieldValue(dataModel, this.codeField).equals(this.value)) {
                    setSelectedIndex(index);
                    break;
                }
            } catch (Exception ex) {

            }
        }

        if (model != null) {
            this.addActionListener((java.awt.event.ActionEvent evt) -> {
                E selectItem = (E) getSelectedItem();

                try {
                    String val = getFieldValue(selectItem, codeField);

                    if (val != null && !"".equals(val)) {
                        UpdateComponent.updateModel(this, model, fieldName, val);
                    }
                } catch (Exception ex) {

                }
            });
        }

        this.getEditor().getEditorComponent().addKeyListener(new KeyAdapter() {

            @Override
            public void keyReleased(KeyEvent event) {
//                JTextComponent jx = (JTextComponent) ((JComboBox) ((Component) event.getSource()).getParent()).getEditor().getEditorComponent();
//                try {
//                    String text = jx.getText(0, jx.getSelectionStart());
//                    setRowFocused(text);
//                } catch (BadLocationException ex) {
//                    Logger.getLogger(XDropdownTableComboBox.class.getName()).log(Level.SEVERE, null, ex);
//                } catch (Exception ex) {
//                    Logger.getLogger(XDropdownTableComboBox.class.getName()).log(Level.SEVERE, null, ex);
//                }

            }
        });

        for (ItemListener li : listens) {
            this.addItemListener(li);
        }
    }

    public void setInit(E model, String fieldName, String value, List<E> list, XColumn[] columns, String codeField, int height) {
        setInit(model, fieldName, value, list, columns, codeField);
        table.setPreferredSize(new Dimension(table.getPreferredSize().width, height));
    }

    public void setInit(E model, String fieldName, String value, List<E> list, XColumn[] columns, String codeField, boolean showHeader) {
        setInit(model, fieldName, value, list, columns, codeField);
        if (!showHeader) {
            table.getTableHeader().setPreferredSize(new Dimension(0, 0));
            table.getTableHeader().setVisible(false);
        }
    }

    private void setRowFocused(String text) throws Exception {
        if (columns.length > 1) {
            int index = getSelectedIndex();

            if (index == -1) {
                String fieldName = columns[1].getFieldName();
                int i = 0;
                for (E m : this.list) {
                    if (this.getFieldValue(m, fieldName).toLowerCase().startsWith(text.toLowerCase())) {
                        setSelectedIndex(i);
                        System.out.println(i);
                        return;
                    }
                    i++;
                }
            }
        }
    }

    private void orderByAscending(int colIndex) {
        XColumn col = columns[colIndex];
        String fieldName = col.getFieldName();

        DefaultComboBoxModel<E> cbModel = (DefaultComboBoxModel<E>) this.getModel();
        cbModel.removeAllElements();

        Collections.sort(this.list, (E o1, E o2) -> {
            try {
                String oo1 = this.getFieldValue(o1, fieldName);
                String oo2 = this.getFieldValue(o2, fieldName);
                return oo1.compareToIgnoreCase(oo2);
            } catch (Exception e) {
            }

            return 0;
        });

        list.forEach(this::addItem);
    }

    private void orderByDescending(int colIndex) {
        XColumn col = columns[colIndex];
        String fieldName = col.getFieldName();

        DefaultComboBoxModel<E> cbModel = (DefaultComboBoxModel<E>) this.getModel();
        cbModel.removeAllElements();

        Collections.sort(this.list, Collections.reverseOrder((E o1, E o2) -> {
            try {
                String oo1 = this.getFieldValue(o1, fieldName);
                String oo2 = this.getFieldValue(o2, fieldName);
                return oo1.compareToIgnoreCase(oo2);
            } catch (Exception e) {
            }

            return 0;
        }));

        list.forEach(this::addItem);
    }

    private DefaultTableModel getDataModel() {
        DefaultTableModel dropDownModel = new DefaultTableModel(null, getColumnNames()) {

            @Override
            public boolean isCellEditable(int row, int column) {
                return false;
            }
        };

        for (E dataModel : list) {
            dropDownModel.addRow(getArray(dataModel, columns));
        }

        return dropDownModel;
    }

    private Object[] getColumnNames() {
        List<String> columnsName = new ArrayList<>();
        for (XColumn c : columns) {
            columnsName.add(c.getCaption());
        }

        return columnsName.toArray();
    }

    private Object[] getArray(E model, XColumn[] columns) {
        List<String> modelValues = new ArrayList<>();

        for (XColumn c : columns) {
            try {
                modelValues.add(getFieldValue(model, c.getFieldName()));
            } catch (Exception ex) {

            }
        }

        return modelValues.toArray();
    }

    private String getFieldValue(E model, String fieldName) throws Exception {
        if (model != null && model.getClass() != String.class) {
            Field field = null;
            try {
                field = model.getClass().getField(fieldName);
            } catch (NoSuchFieldException | SecurityException ex) {
                Logger.getLogger(UpdateComponent.class.getName()).log(Level.SEVERE, null, ex);
                throw ex;

            }

            try {
                if (field != null) {
                    Object obj = field.get(model);
                    String fieldValue = obj.toString();
                    return fieldValue;
                }
            } catch (IllegalArgumentException | IllegalAccessException ex) {
                Logger.getLogger(XDropdownTableComboBox.class.getName()).log(Level.SEVERE, null, ex);
                throw ex;
            }
        } else {
        }

        return "";
    }

    @Override
    public void updateUI() {
        super.updateUI();
        EventQueue.invokeLater(() -> {
            setUI(new MetalComboBoxUI() {
                @Override
                protected ComboPopup createPopup() {
                    return new ComboTablePopup(comboBox, table);
                }
            });
        });
    }

    @Override
    public E getSelectedItem() {
        if (this.getSelectedIndex() > -1) {
            return (E) list.get(this.getSelectedIndex());
        }
        return null;
    }

    public List<Object> getSelectedRow() {
        return (List<Object>) list.get(getSelectedIndex());
    }

    class ComboTablePopup extends BasicComboPopup {

        private final JTable table;
        private final JScrollPane scroll;
        private final int width;

        protected ComboTablePopup(JComboBox<Object> combo, JTable table) {
            super(combo);
            this.table = table;
            int allWidth = 0;
            for (int i = 0; i < table.getColumnModel().getColumnCount(); i++) {
                allWidth += table.getColumnModel().getColumn(i).getPreferredWidth();
            }

            width = allWidth > combo.getWidth() ? allWidth : combo.getWidth();

            ListSelectionModel sm = table.getSelectionModel();
            sm.setSelectionMode(ListSelectionModel.SINGLE_SELECTION);
            sm.addListSelectionListener(e -> combo.setSelectedIndex(table.getSelectedRow()));

            combo.addItemListener(e -> {
                if (e.getStateChange() == ItemEvent.SELECTED) {
                    setRowSelection(combo.getSelectedIndex());
                }
            });

            table.addMouseListener(new MouseAdapter() {
                @Override
                public void mousePressed(MouseEvent e) {
                    combo.setSelectedIndex(table.rowAtPoint(e.getPoint()));
                    setVisible(false);
                }
            });

            scroll = new JScrollPane(table);
            setBorder(BorderFactory.createEmptyBorder());
        }

        @Override
        public void show() {
            if (isEnabled()) {
                Insets ins = scroll.getInsets();
                int tableh = table.getPreferredSize().height;
                int headerh = table.getTableHeader().getPreferredSize().height;
                scroll.setPreferredSize(new Dimension(width, Math.min(500, tableh) + headerh + ins.top + ins.bottom));
                super.removeAll();
                super.add(scroll);
                setRowSelection(comboBox.getSelectedIndex());
                super.show(comboBox, 0, comboBox.getBounds().height);
            }
        }

        private void setRowSelection(int index) {
            if (index != -1) {
                table.setRowSelectionInterval(index, index);
                table.scrollRectToVisible(table.getCellRect(index, 0, true));
            }
        }
    }

    class HighlightListener extends MouseAdapter {

        private int vrow = -1;

        public boolean isHighlightableRow(int row) {
            return this.vrow == row;
        }

        private void setHighlighTableCell(MouseEvent e) {
            Point pt = e.getPoint();
            Component c = e.getComponent();
            if (c instanceof JTable) {
                vrow = ((JTable) c).rowAtPoint(pt);
                c.repaint();
            }
        }

        @Override
        public void mouseMoved(MouseEvent e) {
            setHighlighTableCell(e);
        }

        @Override
        public void mouseDragged(MouseEvent e) {
            setHighlighTableCell(e);
        }

        @Override
        public void mouseExited(MouseEvent e) {
            vrow = -1;
            e.getComponent().repaint();
        }
    }
}
