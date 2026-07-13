package xbuild.Components;

import DSSATModel.Setup;
import FileXModel.ManagementList;
import FileXModel.ModelXBase;
import java.awt.EventQueue;
import java.awt.Image;
import java.awt.image.BufferedImage;
import java.io.File;
import java.io.IOException;
import java.util.logging.Level;
import java.util.logging.Logger;
import javax.imageio.ImageIO;
import javax.swing.ImageIcon;
import javax.swing.JInternalFrame;
import javax.swing.JLabel;
import xbuild.Events.AddLevelEvent;
import xbuild.Events.FieldUpdateEvent;
import xbuild.Events.LevelSelectionChangedEvent;
import xbuild.Events.NewFrameEvent;
import xbuild.Events.RemoveLevelEvent;
import xbuild.Events.SelectionEvent;
import xbuild.Events.UpdateLevelEvent;
import xbuild.Events.ValidationEvent;
import xbuild.Events.XEvent;
import xbuild.Events.XEventListener;

/**
 *
 * @author Jazz
 */
public abstract class IXInternalFrame extends JInternalFrame implements XEventListener {

    protected XEventListener listener;
    protected Setup setup = new Setup();
    protected ModelXBase model;
    
    protected Integer level;
    
    protected boolean isDirty = false;
    
    public abstract String getParentName();
    public abstract ModelXBase newModel();
    public abstract boolean isModelValid();
   
    public IXInternalFrame(){
        ManagementList managementList = getManagementList();
        if(managementList != null) {
            level = managementList.GetSize() + 1;
            setTitle("UNKNOWN_" + (managementList.GetSize() + 1));
            
            model = newModel();
        }        

        listener = this;
        UpdateComponent.setEventListener(this);
        
        initFrame();
    }
    
    public IXInternalFrame(String name){
        level = 0;
        
        ManagementList managementList = getManagementList();
        
        if(managementList != null && !"".equals(name) ){
            for (ModelXBase xModel : managementList.GetAll()) {
                level++;
                if (getLevel(name) == level) {
                    model = xModel;
                    break;
                }
            }
        }
        
        if(model == null){
            model = newModel();
            model.SetName(name);
        }
        
        if(!"".equals(name)){
            setTitle(name);
        }

        initFrame();
    }
    
    public ManagementList getManagementList(){
        return null;
    }
    
    protected void initFrame(){
        
    }
    
    public String getManagementName(){
        return "";
    }
    
    public int getLevel(){
        return level;
    }
    
    public void setSelection(int level){
        this.level = level;
    }

    public void updatePanelName(String name) {

    }

    public void updatePanelList() {

    }

    public void addMyEventListener(XEventListener l) {
        if (this.listener == null) {
            this.listener = l;
        }
    }
    
    public boolean isPrevButtonEnabled(){
        return false;
    }
    
    public boolean isNextButtonEnabled(){
        return false;
    }
    
    public boolean isAddButtonEnabled(){
        return false;
    }
    
    public boolean isDeleteButtonEnabled(){
        return false;
    }
    
    public void initialData(){
        
    }
    
    public String getDescription(){
        return model.GetName();
    }
    
    public ModelXBase getModel(){
        return model;
    }
    
    public boolean isFormDirty(){
        return isDirty;
    }
    
    public void setFormDirty(boolean isDirty){
        this.isDirty = isDirty;
    }
    
    public ModelXBase addNewModel(){        
        ManagementList ml = getManagementList();
        model.SetLevel(ml.GetSize() + 1);
        ml.AddNew(model);
        
        return model;
    }
    
    public int getIndex(){
        return getManagementList().GetIndex(model);
    }
    
    protected int getLevel(String nodeName) {
        String[] level1 = nodeName.split(":");
        String[] level2 = level1[0].split(" ");

        return level2.length > 1 ? Integer.parseInt(level2[1]) : -1;
    }
    

    protected String getDescription(String nodeName) {
        String[] level1 = nodeName.split(":");

        return level1[1].trim();
    }

    protected void setImage(JLabel imagePanel, String imageFile) {
        EventQueue.invokeLater(() -> {
            File playerimage = new File(setup.GetDSSATPath() + "\\Tools\\XBuild\\" + imageFile);

            if (playerimage.exists()) {
                BufferedImage img;
                try {
                    img = ImageIO.read(playerimage);
                    
                    int imgWidth = img.getWidth();
                    int imgHeight = img.getHeight();
                    int panelWidth = imagePanel.getWidth();
                    int panelHeight = imagePanel.getHeight();
                    
                    if(imgWidth != imgHeight){
                        if(imgWidth > imgHeight){
                            panelHeight = (int)((float)imgHeight * ((float)panelWidth / (float)imgWidth));
                        }
                        else{
                            panelWidth = (int)((float)imgWidth * ((float)panelHeight / (float)imgHeight));
                        }
                    }                    
                    
                    Image scaledImage = img.getScaledInstance(panelWidth, panelHeight, Image.SCALE_SMOOTH);
                    ImageIcon imageIcon = new ImageIcon(scaledImage);
                    imagePanel.setIcon(imageIcon);
                } catch (IOException ex) {
                    Logger.getLogger(this.getName()).log(Level.SEVERE, null, ex);
                }
            }
        });
    }
    
    @Override
    public void myAction(FieldUpdateEvent e) {
        EventQueue.invokeLater(() -> {
                    isDirty = true;
                });
    }

    @Override
    public void myAction(XEvent e) {
        //throw new UnsupportedOperationException("Not supported yet."); // Generated from nbfs://nbhost/SystemFileSystem/Templates/Classes/Code/GeneratedMethodBody
    }

    @Override
    public void myAction(AddLevelEvent e) {
        //throw new UnsupportedOperationException("Not supported yet."); // Generated from nbfs://nbhost/SystemFileSystem/Templates/Classes/Code/GeneratedMethodBody
    }

    @Override
    public void myAction(RemoveLevelEvent e) {
        //throw new UnsupportedOperationException("Not supported yet."); // Generated from nbfs://nbhost/SystemFileSystem/Templates/Classes/Code/GeneratedMethodBody
    }

    @Override
    public void myAction(UpdateLevelEvent e) {
        //throw new UnsupportedOperationException("Not supported yet."); // Generated from nbfs://nbhost/SystemFileSystem/Templates/Classes/Code/GeneratedMethodBody
    }

    @Override
    public void myAction(ValidationEvent e) {
        //throw new UnsupportedOperationException("Not supported yet."); // Generated from nbfs://nbhost/SystemFileSystem/Templates/Classes/Code/GeneratedMethodBody
    }

    @Override
    public void myAction(NewFrameEvent e) {
        //throw new UnsupportedOperationException("Not supported yet."); // Generated from nbfs://nbhost/SystemFileSystem/Templates/Classes/Code/GeneratedMethodBody
    }

    @Override
    public void myAction(SelectionEvent e) {
        //throw new UnsupportedOperationException("Not supported yet."); // Generated from nbfs://nbhost/SystemFileSystem/Templates/Classes/Code/GeneratedMethodBody
    }

    @Override
    public void myAction(LevelSelectionChangedEvent e) {
        throw new UnsupportedOperationException("Not supported yet."); // Generated from nbfs://nbhost/SystemFileSystem/Templates/Classes/Code/GeneratedMethodBody
    }
}
