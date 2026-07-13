package FileXModel;

import DSSATModel.WstaType;

/**
 *
 * @author Jazzy
 */
public class FileX {
    public static GeneralInformation general;
    public static FieldList fieldList;
    public static InitialConditionList initialList;
    public static SoilAnalysisList soilAnalysis;
    public static EnvironmentalList environmentals;
    public static CultivarList cultivars;
    public static PlantingList plantings;
    public static IrrigationList irrigations;
    public static FertilizerList fertilizerList;
    public static OrganicList organicList;
    public static TillageList tillageList;
    public static HarvestList harvestList;
    public static ChemicalList chemicalList;
    public static SimulationList simulationList;
    public static TreatmentList treatments;
    public static WstaType wstaType;
    public static FileXCommentList comments;
    
    public static boolean isFileOpenned;
    public static boolean isReady;
    public static boolean isDirty;
    private static String fileName;
    
    public static String GetAbsoluteFileName(){
        return fileName;
    }
    
    public static void SetAbsoluteFileName(String fileName){
        FileX.fileName = fileName;
    }

    public static void NewFileX() {
        isReady = false;
        isDirty = false;
        general = new GeneralInformation();
        fieldList = new FieldList();
        initialList = new InitialConditionList();
        soilAnalysis = new SoilAnalysisList();
        environmentals = new EnvironmentalList();
        cultivars = new CultivarList();
        plantings = new PlantingList();
        irrigations = new IrrigationList();
        fertilizerList = new FertilizerList();
        organicList = new OrganicList();
        tillageList = new TillageList();
        harvestList = new HarvestList();
        chemicalList = new ChemicalList();
        simulationList = new SimulationList();
        treatments = new TreatmentList();
        comments = new FileXCommentList();
        
        

        fileName = null;
    }

    public static void CloseFile() {
        isReady = false;
        isDirty = false;
        general = null;
        fieldList = null;
        initialList = null;
        soilAnalysis = null;
        environmentals = null;
        cultivars = null;
        plantings = null;
        irrigations = null;
        fertilizerList = null;
        organicList = null;
        tillageList = null;
        harvestList = null;
        chemicalList = null;
        simulationList = null;
        treatments = null;
        
        comments = null;

        fileName = null;
        isFileOpenned = false;
    }
}
