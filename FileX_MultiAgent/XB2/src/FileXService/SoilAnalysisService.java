package FileXService;

import Extensions.Utils;
import FileXModel.Comment;
import static FileXModel.FileX.comments;
import static FileXModel.FileX.soilAnalysis;
import FileXModel.Section;
import FileXModel.SoilAnalysis;
import FileXModel.SoilAnalysisLayer;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.PrintWriter;

/**
 *
 * @author Jazzy
 */
public class SoilAnalysisService {
    public static void Read(File fileName) {
        try {
            FileReader fReader = new FileReader(fileName);
            BufferedReader br = new BufferedReader(fReader);
            String strRead;
            
            String soilHeader1 = "";
            boolean bSoilHeader1 = false;
            String soilHeader2 = "";
            boolean bSoilHeader2 = false;
            boolean bSoil = false;
            
            while ((strRead = br.readLine()) != null) {
                String tmp = strRead;
                
                if (tmp.trim().startsWith("*SOIL ANALYSIS")) {
                    bSoil = true;
                } else if (bSoil && !bSoilHeader1 && !bSoilHeader2 && tmp.trim().startsWith("@")) {
                    soilHeader1 = tmp.trim();
                    bSoilHeader1 = true;
                } else if (bSoil && bSoilHeader1 && tmp.trim().startsWith("@A  SABL  SADM  SAOC  SANI SAPHW SAPHB  SAPX  SAKE  SASC")) {
                    soilHeader2 = tmp.trim();
                    bSoilHeader2 = true;
                } else if (bSoil && bSoilHeader1 && bSoilHeader2 && tmp.trim().startsWith("@") && !tmp.trim().startsWith("@A  SABL  SADM  SAOC  SANI SAPHW SAPHB  SAPX  SAKE  SASC")) {
                    bSoilHeader2 = false;
                }else if (bSoil && bSoilHeader1 && !bSoilHeader2) {
                    if ("".equals(tmp.trim())) {
                        bSoil = false;
                        bSoilHeader1 = false;
                        bSoilHeader2 = false;
                        continue;
                    }
                    else if(strRead.trim().startsWith("!")){
                        int l = 1;
                        if(soilAnalysis.GetSize() > 0){
                            l = soilAnalysis.GetAtIndex(soilAnalysis.GetSize() - 1).GetLevel();
                        }
                        comments.addComment(l, Section.Soil1, strRead);
                        continue;
                    }
                    //@A SADAT  SMHB  SMPX  SMKE  SANAME
                    SoilAnalysis soil = new SoilAnalysis();
                    Integer level = Integer.valueOf(tmp.substring(0, 2).trim());
                    soil.SetLevel(level);
                    soil.SADAT = Utils.GetDate(soilHeader1, tmp, "SADAT", 5);
                    soil.SMHB = Utils.GetString(soilHeader1, tmp, " SMHB", 5);
                    soil.SMPX = Utils.GetString(soilHeader1, tmp, " SMPX", 5);
                    soil.SMKE = Utils.GetString(soilHeader1, tmp, " SMKE", 5);
                    soil.SANAME = Utils.GetString(soilHeader1, tmp, "SANAME", tmp.length() - soilHeader1.indexOf("SANAME"));

                    soilAnalysis.AddNew(soil);
                } else if (bSoil && bSoilHeader1 && bSoilHeader2) {
                    if ("".equals(tmp.trim())) {
                        bSoil = false;
                        bSoilHeader1 = false;
                        bSoilHeader2 = false;
                        continue;
                    }
                    else if(strRead.trim().startsWith("!")){
                        int l = 1;
                        if(soilAnalysis.GetSize() > 0){
                            l = soilAnalysis.GetAtIndex(soilAnalysis.GetSize() - 1).GetLevel();
                        }
                        comments.addComment(l, Section.Soil2, strRead);
                        continue;
                    }
                    //@A  SABL  SADM  SAOC  SANI SAPHW SAPHB  SAPX  SAKE  SASC

                    try {
                        Integer level = Integer.valueOf(tmp.substring(0, 2).trim());
                        SoilAnalysis soil = (SoilAnalysis)soilAnalysis.GetAt(level);
                        SoilAnalysisLayer soilLayer = new SoilAnalysisLayer();

                        soilLayer.SABL = Utils.GetFloat(soilHeader2, tmp, "SABL", 5);
                        soilLayer.SADM = Utils.GetFloat(soilHeader2, tmp, "SADM", 5);
                        soilLayer.SAOC = Utils.GetFloat(soilHeader2, tmp, "SAOC", 5);
                        soilLayer.SANI = Utils.GetFloat(soilHeader2, tmp, "SANI", 5);
                        soilLayer.SAPHW = Utils.GetFloat(soilHeader2, tmp, "SAPHW", 5);
                        soilLayer.SAPHB = Utils.GetFloat(soilHeader2, tmp, "SAPHB", 5);
                        soilLayer.SAPX = Utils.GetFloat(soilHeader2, tmp, "SAPX", 5);
                        soilLayer.SAKE = Utils.GetFloat(soilHeader2, tmp, "SAKE", 5);
                        soilLayer.SASC = Utils.GetFloat(soilHeader2, tmp, "SASC", 5);
                        soil.AddLayer(soilLayer);
//                        bSoilHeader2 = false;

                    } catch (NumberFormatException numberFormatException) {
                    }
                }
            }
        } catch (Exception ex) {
            System.out.println(ex.getMessage());
        }
    }
    
    public static void Extract(PrintWriter pw){
        // <editor-fold defaultstate="collapsed" desc="Soil Analysis">
        if (soilAnalysis.GetSize() > 0) {
            pw.println();
            pw.println("*SOIL ANALYSIS");
            for (int i = 0; i < soilAnalysis.GetSize(); i++) {
                SoilAnalysis soil = (SoilAnalysis)soilAnalysis.GetAtIndex(i);
                Integer level = soil.GetLevel();

                pw.println("@A SADAT  SMHB  SMPX  SMKE  SANAME");
                pw.print(Utils.PadLeft(level, 2, ' '));
                pw.print(" " + Utils.JulianDate(soil.SADAT));
                pw.print(" " + Utils.PadLeft(soil.SMHB, 5, ' '));
                pw.print(" " + Utils.PadLeft(soil.SMPX, 5, ' '));
                pw.print(" " + Utils.PadLeft(soil.SMKE, 5, ' '));
                if (soil.SANAME != null) {
                    pw.print("  " + soil.SANAME);
                } else {
                    pw.print("  -99");
                }
                pw.println();
                
                for (Comment comment : comments.getAll(level, Section.Soil1)) {
                    pw.println(comment.description);
                }
                
                if (soil.GetSize() > 0) {
                    pw.println("@A  SABL  SADM  SAOC  SANI SAPHW SAPHB  SAPX  SAKE  SASC");
                    for (int n = 0; n < soil.GetSize(); n++) {
                        SoilAnalysisLayer soilLayer = soil.GetLayer(n);
                        pw.print(Utils.PadLeft(level, 2, ' '));
                        pw.print(" " + Utils.PadLeft(soilLayer.SABL, 5, ' '));
                        pw.print(" " + Utils.PadLeft(soilLayer.SADM, 5, ' '));
                        pw.print(" " + Utils.PadLeft(soilLayer.SAOC, 5, ' '));
                        pw.print(" " + Utils.PadLeft(soilLayer.SANI, 5, ' '));
                        pw.print(" " + Utils.PadLeft(soilLayer.SAPHW, 5, ' '));
                        pw.print(" " + Utils.PadLeft(soilLayer.SAPHB, 5, ' '));
                        pw.print(" " + Utils.PadLeft(soilLayer.SAPX, 5, ' '));
                        pw.print(" " + Utils.PadLeft(soilLayer.SAKE, 5, ' '));
                        pw.print(" " + Utils.PadLeft(soilLayer.SASC, 5, ' '));
                        pw.println();
                    }
                    
                    for (Comment comment : comments.getAll(level, Section.Soil2)) {
                        pw.println(comment.description);
                    }
                }
            }
        }
        // </editor-fold>
    }
}
