package FileXService;

import DSSATModel.ExperimentType;
import Extensions.Utils;
import FileXModel.Cultivar;
import FileXModel.FieldDetail;
import FileXModel.FileX;
import FileXModel.InitialCondition;
import FileXModel.ModelXBase;
import FileXModel.Planting;
import FileXModel.Simulation;
import FileXModel.SoilAnalysis;
import java.util.Date;

/**
 *
 * @author Jazzy
 */
public class FileXValidationService {

    private static String getNodeName(String node) {
        if (node == null || !node.contains(":")) {
            return node;
        }
        
        String[] names = node.split(":");
        
        return names.length > 1 ? node.split(":")[1].trim() : "";
    }

    // public static boolean isGeneralValid() {
    //     boolean isValid = true;

    //     if (FileX.general != null && 
    //             (Utils.IsEmpty(FileX.general.SiteCode) || FileX.general.SiteCode.length() != 2
    //             || Utils.IsEmpty(FileX.general.InstituteCode) || FileX.general.InstituteCode.length() != 2
    //             || Utils.IsEmpty(FileX.general.Year) || FileX.general.Year.length() != 4)) {
    //         isValid = false;
    //     }
    //     if (FileX.general != null && FileX.general.FileType == ExperimentType.Experimental && (FileX.general.crop == null || Utils.IsEmpty(FileX.general.crop.CropCode))) {
    //         isValid = false;
    //     }
    //     return isValid;
    // }

    public static boolean isGeneralValid() {
    boolean isValid = true;

    if (FileX.general == null) {
        System.out.println("[General Validation] FileX.general is NULL");
        return false;
    }

    // SiteCode checks
    if (Utils.IsEmpty(FileX.general.SiteCode)) {
        System.out.println("[General Validation] SiteCode is empty or null");
        isValid = false;
    } else if (FileX.general.SiteCode.length() != 2) {
        System.out.println("[General Validation] SiteCode '" + FileX.general.SiteCode 
                           + "' must be exactly 2 characters (current length: " 
                           + FileX.general.SiteCode.length() + ")");
        isValid = false;
    }

    // InstituteCode checks
    if (Utils.IsEmpty(FileX.general.InstituteCode)) {
        System.out.println("[General Validation] InstituteCode is empty or null");
        isValid = false;
    } else if (FileX.general.InstituteCode.length() != 2) {
        System.out.println("[General Validation] InstituteCode '" + FileX.general.InstituteCode 
                           + "' must be exactly 2 characters (current length: " 
                           + FileX.general.InstituteCode.length() + ")");
        isValid = false;
    }

    // Year checks
    if (Utils.IsEmpty(FileX.general.Year)) {
        System.out.println("[General Validation] Year is empty or null");
        isValid = false;
    } else if (FileX.general.Year.length() != 4) {
        System.out.println("[General Validation] Year '" + FileX.general.Year 
                           + "' must be exactly 4 characters (current length: " 
                           + FileX.general.Year.length() + ")");
        isValid = false;
    }

    // Crop code checks (only if experimental file)
    if (FileX.general.FileType == ExperimentType.Experimental) {
        if (FileX.general.crop == null) {
            System.out.println("[General Validation] Crop object is NULL for experimental file");
            isValid = false;
        } else if (Utils.IsEmpty(FileX.general.crop.CropCode)) {
            System.out.println("[General Validation] CropCode is empty or null for experimental file");
            isValid = false;
        }
    }

    if (isValid) {
        System.out.println("[General Validation] General section is valid");
    } else {
        System.out.println("[General Validation] General section is INVALID");
    }

    return isValid;
}


    public static boolean IsMinimumRequired() {
        boolean isValid = isGeneralValid() &&
                FileX.fieldList != null && FileX.fieldList.GetSize() > 0
                && !Utils.IsEmpty(((FieldDetail) FileX.fieldList.GetAtIndex(0)).WSTA)
                && !Utils.IsEmpty(((FieldDetail) FileX.fieldList.GetAtIndex(0)).ID_SOIL)
                && FileX.cultivars != null && FileX.cultivars.GetSize() > 0
                && FileX.plantings != null && FileX.plantings.GetSize() > 0 && isPlantingValid(FileX.plantings.GetAtIndex(0).GetName())
                && FileX.simulationList != null && FileX.simulationList.GetSize() > 0 && isSimulationControlValid(FileX.simulationList.GetAtIndex(0).GetName());

        return isValid;
    }
    
    public static boolean IsCropEnabled(){
        return FileX.general != null && FileX.general.crop != null && FileX.general.crop.Enabled;
    }

    public static boolean isFieldsValid() {
        boolean isValid = true;

        if (FileX.fieldList == null || FileX.fieldList.GetSize() == 0) {
            isValid = false;
        } else {
            for (ModelXBase field : FileX.fieldList.GetAll()) {
                FieldDetail f = (FieldDetail) field;
                isValid &= isFieldValid(f);
            }
        }
        return isValid;
    }

    public static boolean isFieldValid(String node) {
        boolean isValid = true;

        for (ModelXBase field : FileX.fieldList.GetAll()) {
            FieldDetail f = (FieldDetail) field;
            if (f.FLNAME == null ? getNodeName(node) == null : f.FLNAME.equals(getNodeName(node))) {
                isValid &= isFieldValid(f);
            }
        }

        return isValid;
    }
    
    public static boolean isFieldValid(FieldDetail field) {
        boolean isValid = true;
        
        if (field.WSTA == null || "".equals(field.WSTA)) {
            isValid = false;
        } else if (field.ID_SOIL == null || "".equals(field.ID_SOIL)) {
            isValid = false;
        }

        return isValid;
    }
    
    public static boolean isInitialConditionValid(){
        boolean isValid = true;

        if (FileX.initialList != null) {
            for (ModelXBase init : FileX.initialList.GetAll()) {
                InitialCondition initc = (InitialCondition) init;
                isValid &= isInitialConditionValid(initc);
            }
        }

        return isValid;
    }
    
    public static boolean isInitialConditionValid(String node){
        boolean isValid = true;
        
        for (ModelXBase init : FileX.initialList.GetAll()) {
            InitialCondition initc = (InitialCondition) init;
            if (initc.ICNAME == null ? getNodeName(node) == null : initc.ICNAME.equals(getNodeName(node))) {
                isValid &= isInitialConditionValid(initc);
            }
        }
        
        return isValid;
    }
    
    public static boolean isInitialConditionValid(InitialCondition init){
        boolean isValid = true;
        
        isValid &= init.ICDAT != null;
        
        return isValid;
    }
    
    public static boolean isSoilAnalysisValid(){
        boolean isValid = true;

        if (FileX.soilAnalysis != null) {
            for (ModelXBase soil : FileX.soilAnalysis.GetAll()) {
                isValid &= isSoilAnalysisValid((SoilAnalysis) soil);
            }
        }

        return isValid;
    }
    
    public static boolean isSoilAnalysisValid(String node){
        boolean isValid = true;
        
        for (ModelXBase soil : FileX.soilAnalysis.GetAll()) {
            SoilAnalysis s = (SoilAnalysis) soil;
            if (s.SANAME == null ? getNodeName(node) == null : s.SANAME.equals(getNodeName(node))) {
                isValid &= isSoilAnalysisValid(s);
            }
        }
        
        return isValid;
    }
    
    public static boolean isSoilAnalysisValid(SoilAnalysis soil){
        boolean isValid = true;
        
        isValid &= soil.SADAT != null;
        
        return isValid;
    }

    public static boolean isCultivarsValid() {
        boolean isValid = true;

        if (FileX.cultivars == null || FileX.cultivars.GetSize() == 0) {
            isValid = false;
        } else {
            for (ModelXBase cul : FileX.cultivars.GetAll()) {
                Cultivar c = (Cultivar) cul;
                isValid &= isCultivarsValid(c);
            }
        }
        return isValid;
    }
    
    public static boolean isCultivarsValid(Cultivar cultivar) {
        boolean isValid = true;

        if (cultivar.CR == null || "".equals(cultivar.CR)) {
            isValid = false;
        }

        return isValid;
    }

    public static boolean isPlantingsValid() {
        boolean isValid = true;

        if (FileX.plantings == null || FileX.plantings.GetSize() == 0) {
            isValid = false;
        } else {
            for (ModelXBase planting : FileX.plantings.GetAll()) {
                Planting p = (Planting) planting;
                isValid &= isPlantingValid(p);
            }
        }
        return isValid;
    }

    public static boolean isPlantingValid(String node) {
        boolean isValid = true;

        for (ModelXBase planting : FileX.plantings.GetAll()) {
            Planting p = (Planting) planting;
            if (p.PLNAME.equals(getNodeName(node))) {
                isValid &= isPlantingValid(p);
            }
        }
        return isValid;
    }

    public static boolean isPlantingValid(Planting planting) {
        boolean isValid = true;

        if (planting.PDATE == null) {
            isValid = false;
        } else if (planting.PLME == null || "".equals(planting.PLME)) {
            isValid = false;
        } else if (planting.PLDS == null || "".equals(planting.PLDS)) {
            isValid = false;
        } else if (planting.PLRS == null) {
            isValid = false;
        } else if (planting.PLRD == null) {
            isValid = false;
        } else if (planting.PLDP == null) {
            isValid = false;
        } else if (planting.PPOP == null) {
            isValid = false;
        }
        return isValid;
    }
    
    public static boolean isSimulationControlsValid() {
        boolean isValid = true;
        if (FileX.simulationList == null || FileX.simulationList.GetSize() == 0) {
            isValid = false;
        } else {
            for (ModelXBase simulation : FileX.simulationList.GetAll()) {
                Simulation s = (Simulation) simulation;
                if (s.SDATE == null) {
                    isValid &= isSimulationControlValid(s);
                }
            }
        }
        return isValid;
    }

    public static boolean isSimulationControlValid(String node) {
        boolean isValid = true;

        for (ModelXBase simulation : FileX.simulationList.GetAll()) {
            Simulation s = (Simulation) simulation;
            if (s.SNAME.equals(getNodeName(node))) {
                isValid = isSimulationControlValid(s);
            }
        }
        return isValid;
    }
    
    public static boolean isSimulationControlValid(Simulation simulation) {
        boolean isValid = true;
        
        if (simulation.SDATE == null) {
            isValid = false;
        }

        return isValid;
    }
    
    public static boolean isSimulationDateValid(Date simulationDate) {
        boolean isValid = true;
        
        if(FileX.plantings != null){
            for (ModelXBase planting : FileX.plantings.GetAll()) {
                Planting p = (Planting) planting;
                isValid &= simulationDate.before(p.PDATE) || simulationDate.equals(p.PDATE);
            }
        }

        return isValid;
    }
    
    public static boolean isAfterSimulationDate(Date date) {
        boolean isValid = true;
        
        if(FileX.simulationList != null){
            for (ModelXBase sim : FileX.simulationList.GetAll()) {
                Simulation s = (Simulation) sim;
                isValid &= date.after(s.SDATE) || date.equals(s.SDATE);
            }
        }

        return isValid;
    }
    
    public static boolean isTreatmentValid(String node) {
        return FileX.treatments != null && FileX.treatments.GetSize() > 0;
    }
}
