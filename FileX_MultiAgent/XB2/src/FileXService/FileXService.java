package FileXService;

import DSSATModel.WstaType;
import FileXModel.*;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 *
 * @author Jazzy
 */
public class FileXService {
    public static void OpenFileX(File fileName) {
        FileX.NewFileX();
        
        GeneralService.Read(fileName);
        TreatmentService.Read(fileName);
        CultivarService.Read(fileName);
        FieldService.Read(fileName);
        SoilAnalysisService.Read(fileName);
        InitialConditionService.Read(fileName);
        PlantingDetailService.Read(fileName);
        IrrigationService.Read(fileName);
        FertilizerService.Read(fileName);
        ResidueService.Read(fileName);
        ChemicalApplicationService.Read(fileName);
        TillageService.Read(fileName);
        EnvironmentService.Read(fileName);
        HarvestService.Read(fileName);
        FileX.simulationList = SimulationControlService.Read(fileName.getAbsolutePath());
        FileX.SetAbsoluteFileName(fileName.getAbsolutePath());
        
        if(FileX.simulationList != null && FileX.simulationList.GetSize() > 0){
            Simulation s = (Simulation)FileX.simulationList.GetAtIndex(0);
            switch (s.WTHER) {
                case "M":
                    FileX.wstaType = WstaType.WTH;
                    break;
                case "S":
                    FileX.wstaType = WstaType.CLI;
                    break;
                case "W":
                    FileX.wstaType = WstaType.WTG;
                    break;
            }
        }
        
        FileX.isFileOpenned = true;
    }
    
    public static void SaveFile(File file) {
        FileWriter writer;
        try {
            writer = new FileWriter(file);
        } catch (IOException ex) {
            System.out.println(ex.getMessage());
            return;
        }
        PrintWriter pw = new PrintWriter(writer);

        GeneralService.Extract(pw);
        TreatmentService.Extract(pw);
        CultivarService.Extract(pw);
        FieldService.Extract(pw);
        SoilAnalysisService.Extract(pw);
        InitialConditionService.Extract(pw);
        PlantingDetailService.Extract(pw);
        IrrigationService.Extract(pw);
        FertilizerService.Extract(pw);
        ResidueService.Extract(pw);
        TillageService.Extract(pw);
        EnvironmentService.Extract(pw);
        HarvestService.Extract(pw);        
        ChemicalApplicationService.Extract(pw);
        SimulationControlService.Extract(pw);        
        
        try {
            writer.close();
        } catch (IOException ex) {
            Logger.getLogger(FileX.class.getName()).log(Level.SEVERE, null, ex);
        }
        FileX.isFileOpenned = false;
    }
}
