/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

/*
 * LoadingData.java
 *
 * Created on 19 ก.พ. 2553, 11:44:27
 */

package xbuild;

import DSSATServices.*;
import Extensions.Icons;
import Extensions.Variables;
import java.awt.Cursor;
import java.awt.Dimension;
import java.awt.Toolkit;
import java.awt.event.AdjustmentEvent;
import java.awt.event.WindowAdapter;
import java.awt.event.WindowEvent;
import java.util.ArrayList;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicBoolean;
import javax.swing.*;
import xbuild.Events.LoadingDoneEvent;
import xbuild.Events.LoadingEventListener;
import xbuild.Events.XEventListener;



/**
 *
 * @author Jazzy
 */
public class LoadingDataFrame extends javax.swing.JFrame {

    /** Creates new form LoadingData */
    private Task task;
    protected String dir;
    private boolean isValid = true;   
    private boolean isDone = false;
    private String validationMessage = ""; 
    private final Object messageLock = new Object();
    private final AtomicBoolean hasError = new AtomicBoolean(false); 
    
    protected XEventListener listener;
    private LoadingEventListener laodingEvent;

    class Task extends SwingWorker<Void, Void> {
        /*
         * Main task. Executed in background thread.
         */
        @Override
        public Void doInBackground() {
            //int progress = 0;
            //Initialize progress property.
            setProgress(0);
            Variables.setLocale(getLocale());
            
            ArrayList<DSSATServiceBase> parseList = new ArrayList<>();            
            
            parseList.add(new CropService(dir));
            parseList.add(new ChemicalService(dir));
            parseList.add(new DrainageService(dir));
            parseList.add(new SoilTextureService(dir));
            parseList.add(new SoilAnalysisService(dir));
            parseList.add(new PlantingMethodService(dir));
            parseList.add(new PlantDistributionService(dir));
            parseList.add(new IrrigationMethodService(dir));
            parseList.add(new FertilizerService(dir));
            parseList.add(new FertilizerMethodService(dir));
            parseList.add(new EnvironmentService(dir));
            parseList.add(new TillageService(dir));
            parseList.add(new ResiduesService(dir));
            parseList.add(new HarvestComponentService(dir));
            parseList.add(new HarvestSizeService(dir));
            parseList.add(new FieldHistoryService(dir));
            parseList.add(new SimulationService(dir));
            parseList.add(new GrowthStageService(dir));
            parseList.add(new SoilService(dir));
            parseList.add(new WeatherService(dir));
            
            jScrollPane2.getVerticalScrollBar().addAdjustmentListener((AdjustmentEvent e) -> {ttt(e);});

            try{
                validationMessage += "Loading DSSAT profile....";
                jLabel1.setText("<html>" + validationMessage + "</html>");
                DSSATProfileService dssatProfileService = new DSSATProfileService(dir);
                dssatProfileService.Parse();
                
                validationMessage += "<font color='green'>!Done</font><br>";
                jLabel1.setText("<html>" + validationMessage + "</html>");
            }
            catch(Exception ex){
                validationMessage += "<font color='red'>!Error</font><br>";
                jLabel1.setText("<html>" + validationMessage + "</html>");
                isValid = false;
            }
            
            // Process services in parallel
//            ConcurrentHashMap<String, String> serviceResults = new ConcurrentHashMap<>();
            
            CompletableFuture<Void>[] futures = parseList.stream()
                .map(service -> CompletableFuture.runAsync(() -> {
                    try {
                        synchronized(messageLock) {
                            validationMessage += "Loading " + service.getName() + "....<br>";
                            SwingUtilities.invokeLater(() -> jLabel1.setText("<html>" + validationMessage + "</html>"));
                        }
                        
                        service.Parse();
                        
                        synchronized(messageLock) {
                            validationMessage += "<font color='green'>" + service.getName() + " Done!</font><br>";
                            SwingUtilities.invokeLater(() -> jLabel1.setText("<html>" + validationMessage + "</html>"));
                        }
                        
                    } catch (Exception ex) {
                        hasError.set(true);
                        synchronized(messageLock) {
                            validationMessage += "<font color='red'>" + service.getName() + " Error!</font><br>";
                            for(String message : ex.getMessage().split("\n")){
                                validationMessage += "<div style='padding-left:25px'><font color='red'>" + message + "</font></div>";
                            }
                            SwingUtilities.invokeLater(() -> jLabel1.setText("<html>" + validationMessage + "</html>"));
                        }
                    }
                }))
                .toArray(CompletableFuture[]::new);
            
            // Wait for all services to complete
            try {
                CompletableFuture.allOf(futures).join();
                if (hasError.get()) {
                    isValid = false;
                }
            } catch (Exception ex) {
                isValid = false;
            }
            
            try{
                validationMessage += "Loading Simulation Default....";
                jLabel1.setText("<html>" + validationMessage + "</html>");
                    
                SimulationDefaultService simulationDefaultService = new SimulationDefaultService(dir);
                simulationDefaultService.Parse();
                
                validationMessage += "<font color='green'>!Done</font><br>";
                jLabel1.setText("<html>" + validationMessage + "</html>");
            }
            catch(Exception ex){
                validationMessage += "<font color='red'>!Error</font><br>";
                jLabel1.setText("<html>" + validationMessage + "</html>");
                isValid = false;
            }
            
            if(isValid){
                validationMessage += "<font color='green'>!Done</font><br>";
                jLabel1.setText("<html>" + validationMessage + "</html>");
            }
            else{
                validationMessage += "<font color='red'>!Some of configurations are failed</font><br>";
                jLabel1.setText("<html>" + validationMessage + "</html>");
            }
            
            Icons.Init(getClass());
            
            isDone = true;

            return null;
        }

        /*
         * Executed in event dispatching thread
         */
        @Override
        public void done() {
            setCursor(Cursor.getPredefinedCursor(Cursor.DEFAULT_CURSOR));
            
            laodingEvent.onLoaded(new LoadingDoneEvent(this, isValid));
            
            if(!isValid){
                setVisible(true);
            }
        }
    }
    
    private void ttt(AdjustmentEvent e) {
        if(!isDone)
            e.getAdjustable().setValue(e.getAdjustable().getMaximum());
    }

    public LoadingDataFrame(String dir) {
        this.dir = dir;

        initComponents();

        Toolkit tk = Toolkit.getDefaultToolkit();
        Dimension screenSize = tk.getScreenSize();
        int screenHeight = screenSize.height;
        int screenWidth = screenSize.width;
        Dimension winSize = getSize();
        setLocation((screenWidth - winSize.width) / 2 , (screenHeight - winSize.height) / 2);
    }
    
    public void addListener(LoadingEventListener lEvent){
        this.laodingEvent = lEvent;
    }

    /** This method is called from within the constructor to
     * initialize the form.
     * WARNING: Do NOT modify this code. The content of this method is
     * always regenerated by the Form Editor.
     */
    @SuppressWarnings("unchecked")
    // <editor-fold defaultstate="collapsed" desc="Generated Code">//GEN-BEGIN:initComponents
    private void initComponents() {

        l = new javax.swing.JLabel();
        jScrollPane2 = new javax.swing.JScrollPane();
        jLabel1 = new javax.swing.JLabel();

        setDefaultCloseOperation(javax.swing.WindowConstants.DISPOSE_ON_CLOSE);
        setIconImage(Variables.getIconImage(getClass()));

        jLabel1.setText("jLabel1");
        jScrollPane2.setViewportView(jLabel1);

        javax.swing.GroupLayout layout = new javax.swing.GroupLayout(getContentPane());
        getContentPane().setLayout(layout);
        layout.setHorizontalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(layout.createSequentialGroup()
                .addComponent(jScrollPane2, javax.swing.GroupLayout.PREFERRED_SIZE, 674, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addComponent(l)
                .addContainerGap())
        );
        layout.setVerticalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(layout.createSequentialGroup()
                .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addGroup(layout.createSequentialGroup()
                        .addGap(27, 27, 27)
                        .addComponent(l))
                    .addGroup(layout.createSequentialGroup()
                        .addContainerGap()
                        .addComponent(jScrollPane2, javax.swing.GroupLayout.PREFERRED_SIZE, 215, javax.swing.GroupLayout.PREFERRED_SIZE)))
                .addContainerGap(javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
        );

        pack();
    }// </editor-fold>//GEN-END:initComponents

    public void startTask() {
        // TODO add your handling code here:
        setCursor(Cursor.getPredefinedCursor(Cursor.WAIT_CURSOR));
        //Instances of javax.swing.SwingWorker are not reusuable, so
        //we create new instances as needed.
        task = new Task();
        task.execute();
    }
   

    // Variables declaration - do not modify//GEN-BEGIN:variables
    private javax.swing.JLabel jLabel1;
    private javax.swing.JScrollPane jScrollPane2;
    private javax.swing.JLabel l;
    // End of variables declaration//GEN-END:variables

}
