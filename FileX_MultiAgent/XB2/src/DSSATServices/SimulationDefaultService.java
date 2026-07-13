package DSSATServices;

import DSSATModel.ExperimentType;
import DSSATModel.SimulationControlDefaults;
import FileXModel.Simulation;
import FileXService.SimulationControlService;
import FileXModel.SimulationList;

/**
 *
 * @author Jazzy
 */
public class SimulationDefaultService {
    private String rootPath;
    public SimulationDefaultService(String rootPath){
        this.rootPath = rootPath;
    }
    
    public void Parse() throws Exception{
        try {
            for(ExperimentType exp : ExperimentType.values()){
                String fileName = "";
                switch (exp) {
                    case Experimental:
                        fileName = rootPath + "\\Tools\\XBuild\\Simulate.def";
                        break;
                    case Sequential:
                        fileName = rootPath + "\\Tools\\XBuild\\Simulate_Sequence.def";
                        break;
                    case Seasonal:
                        fileName = rootPath + "\\Tools\\XBuild\\Simulate_Seasonal.def";
                        break;
                    case Spatial:
                        fileName = rootPath + "\\Tools\\XBuild\\Simulate_Spatial.def";
                        break;
                    case Forecast:
                        fileName = rootPath + "\\Tools\\XBuild\\Simulate_Forecast.def";
                        break;
                    default:
                        break;
                }
                
                SimulationList sims = SimulationControlService.Read(fileName);
                if(sims != null && sims.GetSize() > 0)
                    SimulationControlDefaults.Update(exp, (Simulation)sims.GetAtIndex(0));
            }
        } catch (Exception ex) {
            throw new Exception("Simulation Default parse failed");
        }
    }
}
