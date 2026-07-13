package DSSATModel;

import FileXModel.Simulation;
import java.util.HashMap;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 *
 * @author Jazzy
 */
public class SimulationControlDefaults {
    
    private static final HashMap<ExperimentType, Simulation> simulations = new HashMap<ExperimentType, Simulation>() {};
    static {
        for (ExperimentType exp : ExperimentType.values()) {
            simulations.put(exp, new Simulation());
        }
    }
    
    public static Simulation Get(ExperimentType experimentType){
        Simulation sim = simulations.get(experimentType);
        
        Simulation newSim = null;
        try {
            newSim = sim.clone();
        } catch (CloneNotSupportedException ex) {
            Logger.getLogger(SimulationControlDefaults.class.getName()).log(Level.SEVERE, null, ex);
        }
        return newSim; 
    }
    
    public static void Update(ExperimentType experimentType, Simulation sim){
        for(ExperimentType exp : ExperimentType.values()){
            if(exp == experimentType){
                simulations.put(exp, sim);
            }
        }
    }
    
}
