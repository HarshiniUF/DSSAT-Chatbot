import FileXService.*;
import java.io.File;

public class FileXCustomScriptV1 {
    
    public static void main(String[] args) {
        if (args.length < 1) {
            System.out.println("Usage: java FileXCustomScript <input_file> [output_file]");
            return;
        }
        
        String inputFilePath = args[0];
        String outputFilePath;
        
        // If output file not provided, auto-generate name
        if (args.length < 2) {
            int dotIndex = inputFilePath.lastIndexOf('.');
            if (dotIndex > 0) {
                outputFilePath = inputFilePath.substring(0, dotIndex) + "_COPY" + inputFilePath.substring(dotIndex);
            } else {
                outputFilePath = inputFilePath + "_COPY";
            }
        } else {
            outputFilePath = args[1];
        }
        
        File inputFile = new File(inputFilePath);
        File outputFile = new File(outputFilePath);
        
        if (!inputFile.exists()) {
            System.out.println("Error: Input file does not exist: " + inputFilePath);
            return;
        }
        
        try {
            System.out.println("Reading FileX from: " + inputFilePath);
            FileXService.OpenFileX(inputFile);
            System.out.println("[OK] FileX loaded successfully");
            
            // Perform validations
            System.out.println("\nValidating FileX...");
            boolean isValid = true;
            
            // 1. General validation
            if (!FileXValidationService.isGeneralValid()) {
                System.out.println("[FAIL] General section is invalid");
                System.out.println("       - Check SiteCode (must be 2 chars)");
                System.out.println("       - Check InstituteCode (must be 2 chars)");
                System.out.println("       - Check Year (must be 4 chars)");
                System.out.println("       - Check Crop Code (if experimental type)");
                isValid = false;
            } else {
                System.out.println("[OK] General section is valid");
            }
            
            // 2. Minimum requirements
            if (!FileXValidationService.IsMinimumRequired()) {
                System.out.println("[FAIL] Minimum requirements not met");
                System.out.println("       - Must have at least one Field with WSTA and ID_SOIL");
                System.out.println("       - Must have at least one Cultivar");
                System.out.println("       - Must have at least one valid Planting");
                System.out.println("       - Must have at least one valid Simulation Control");
                isValid = false;
            } else {
                System.out.println("[OK] Minimum requirements met");
            }
            
            // 3. Fields validation
            if (!FileXValidationService.isFieldsValid()) {
                System.out.println("[FAIL] One or more Fields are invalid");
                System.out.println("       - Each field must have WSTA (Weather Station)");
                System.out.println("       - Each field must have ID_SOIL (Soil ID)");
                isValid = false;
            } else {
                System.out.println("[OK] All Fields are valid");
            }
            
            // 4. Cultivars validation
            if (!FileXValidationService.isCultivarsValid()) {
                System.out.println("[FAIL] One or more Cultivars are invalid");
                System.out.println("       - Each cultivar must have CR (Crop Code)");
                isValid = false;
            } else {
                System.out.println("[OK] All Cultivars are valid");
            }
            
            // 5. Plantings validation
            if (!FileXValidationService.isPlantingsValid()) {
                System.out.println("[FAIL] One or more Plantings are invalid");
                System.out.println("       - Must have PDATE (Planting Date)");
                System.out.println("       - Must have PLME (Planting Method)");
                System.out.println("       - Must have PLDS (Planting Distribution)");
                System.out.println("       - Must have PLRS (Row Spacing)");
                System.out.println("       - Must have PLRD (Row Direction)");
                System.out.println("       - Must have PLDP (Planting Depth)");
                System.out.println("       - Must have PPOP (Plant Population)");
                isValid = false;
            } else {
                System.out.println("[OK] All Plantings are valid");
            }
            
            // 6. Initial Conditions validation
            if (!FileXValidationService.isInitialConditionValid()) {
                System.out.println("[FAIL] One or more Initial Conditions are invalid");
                System.out.println("       - Each initial condition must have ICDAT (Initial Condition Date)");
                isValid = false;
            } else {
                System.out.println("[OK] All Initial Conditions are valid");
            }
            
            // 7. Soil Analysis validation
            if (!FileXValidationService.isSoilAnalysisValid()) {
                System.out.println("[FAIL] One or more Soil Analyses are invalid");
                System.out.println("       - Each soil analysis must have SADAT (Soil Analysis Date)");
                isValid = false;
            } else {
                System.out.println("[OK] All Soil Analyses are valid");
            }
            
            // 8. Simulation Controls validation
            if (!FileXValidationService.isSimulationControlsValid()) {
                System.out.println("[FAIL] One or more Simulation Controls are invalid");
                System.out.println("       - Each simulation must have SDATE (Simulation Start Date)");
                isValid = false;
            } else {
                System.out.println("[OK] All Simulation Controls are valid");
            }
            
            // Summary
            System.out.println("\n" + "=".repeat(60));
            if (isValid) {
                System.out.println("VALIDATION RESULT: PASSED");
                System.out.println("=".repeat(60));
                
                System.out.println("\nWriting FileX to: " + outputFilePath);
                FileXService.SaveFile(outputFile);
                System.out.println("[OK] FileX saved successfully");
                
            } else {
                System.out.println("VALIDATION RESULT: FAILED");
                System.out.println("=".repeat(60));
                System.out.println("\nFile NOT saved due to validation errors.");
                System.out.println("Please fix the errors above and try again.");
                System.exit(1);
            }
            
        } catch (Exception e) {
            System.out.println("\nError: " + e.getMessage());
            e.printStackTrace();
            System.exit(1);
        }
    }
}
