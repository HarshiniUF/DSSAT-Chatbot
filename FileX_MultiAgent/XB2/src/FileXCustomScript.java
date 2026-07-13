import FileXService.*;
import java.io.File;

public class FileXCustomScript {
    
    public static void main(String[] args) {
        if (args.length < 1) {
            System.out.println("Usage: java FileXCustomScript <input_file> [output_file]");
            return;
        }
        
        String inputFilePath = args[0];
        String outputFilePath;
        
        // If output file not provided, auto-generate name
        if (args.length < 2) {
            // Add "_COPY" before the extension
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
            System.out.println("✓ FileX loaded successfully!");
            
            System.out.println("Writing FileX to: " + outputFilePath);
            FileXService.SaveFile(outputFile);
            System.out.println("✓ FileX saved successfully!");
            
        } catch (Exception e) {
            System.out.println("Error: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
