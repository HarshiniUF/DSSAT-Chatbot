package FileXService;

import Extensions.Utils;
import FileXModel.Comment;
import static FileXModel.FileX.comments;
import static FileXModel.FileX.plantings;
import FileXModel.Planting;
import FileXModel.Section;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.PrintWriter;

/**
 *
 * @author Jazzy
 */
public class PlantingDetailService {
    public static void Read(File fileName) {
        try {
            FileReader fReader = new FileReader(fileName);
            BufferedReader br = new BufferedReader(fReader);
            String strRead;
            
            String plantingHeader = "";
            boolean bPlantingHeader = false;
            boolean bPlanting = false;
            
            while ((strRead = br.readLine()) != null) {
                String tmp = strRead;
                
                if (tmp.trim().startsWith("*PLANTING DETAILS")) {
                    bPlanting = true;

                } else if (bPlanting && !bPlantingHeader && tmp.trim().startsWith("@")) {
                    plantingHeader = tmp.trim();
                    bPlantingHeader = true;
                } else if (bPlanting && bPlantingHeader) {
                    if ("".equals(tmp.trim()) || tmp.trim().startsWith("*")) {
                        bPlanting = false;
                        bPlantingHeader = false;
                        continue;
                    }
                    else if(strRead.trim().startsWith("!")){
                        int l = 1;
                        if(plantings.GetSize() > 0){
                            l = plantings.GetAtIndex(plantings.GetSize() - 1).GetLevel();
                        }
                        comments.addComment(l, Section.Planting, strRead);
                        continue;
                    }
                    
                    //@P PDATE EDATE  PPOP  PPOE  PLME  PLDS  PLRS  PLRD  PLDP  PLWT  PAGE  PENV  PLPH  SPRL                        PLNAME
                    Planting planting = new Planting();
                    Integer level = Integer.valueOf(tmp.substring(0, 2).trim());

                    planting.SetLevel(level);
                    planting.PDATE = Utils.GetDate(plantingHeader, tmp, "PDATE", 5);
                    planting.EDATE = Utils.GetDate(plantingHeader, tmp, "EDATE", 5);
                    planting.PPOP = Utils.GetFloat(plantingHeader, tmp, "PPOP", 5);
                    planting.PPOE = Utils.GetFloat(plantingHeader, tmp, "PPOE", 5);
                    planting.PLME = Utils.GetString(plantingHeader, tmp, " PLME", 5);
                    planting.PLDS = Utils.GetString(plantingHeader, tmp, " PLDS", 5);
                    planting.PLRS = Utils.GetFloat(plantingHeader, tmp, "PLRS", 5);
                    planting.PLRD = Utils.GetFloat(plantingHeader, tmp, "PLRD", 5);
                    planting.PLDP = Utils.GetFloat(plantingHeader, tmp, "PLDP", 5);
                    planting.PLWT = Utils.GetFloat(plantingHeader, tmp, "PLWT", 5);
                    planting.PAGE = Utils.GetFloat(plantingHeader, tmp, "PAGE", 5);
                    planting.PENV = Utils.GetFloat(plantingHeader, tmp, "PENV", 5);
                    planting.PLPH = Utils.GetFloat(plantingHeader, tmp, "PLPH", 5);
                    planting.SPRL = Utils.GetFloat(plantingHeader, tmp, "SPRL", 5);
                    planting.PLNAME = Utils.GetString(plantingHeader, tmp, "PLNAME", tmp.length() - plantingHeader.indexOf("PLNAME"));
                    plantings.AddNew(planting);
                }
            }
        } catch (Exception ex) {
            System.out.println(ex.getMessage());
        }
    }
    
    public static void Extract(PrintWriter pw){
        // <editor-fold defaultstate="collapsed" desc="Planting">
        if (plantings.GetSize() > 0) {
            pw.println();
            pw.println("*PLANTING DETAILS");
            pw.println("@P PDATE EDATE  PPOP  PPOE  PLME  PLDS  PLRS  PLRD  PLDP  PLWT  PAGE  PENV  PLPH  SPRL                        PLNAME");
            for (int i = 0; i < plantings.GetSize(); i++) {
                Planting plants = (Planting)plantings.GetAtIndex(i);
                Integer level = plants.GetLevel();
                pw.print(Utils.PadLeft(level, 2, ' '));
                pw.print(" " + Utils.PadRight(Utils.JulianDate(plants.PDATE), 5, ' '));
                pw.print(" " + Utils.PadLeft(Utils.JulianDate(plants.EDATE), 5, ' '));
                pw.print(" " + Utils.PadLeft(plants.PPOP, 5, ' '));
                pw.print(" " + Utils.PadLeft(plants.PPOE, 5, ' '));
                pw.print(" " + Utils.PadLeft(plants.PLME, 5, ' '));
                pw.print(" " + Utils.PadLeft(plants.PLDS, 5, ' '));
                pw.print(" " + Utils.PadLeft(plants.PLRS, 5, ' '));
                pw.print(" " + Utils.PadLeft(plants.PLRD, 5, ' '));
                pw.print(" " + Utils.PadLeft(plants.PLDP, 5, ' '));
                pw.print(" " + Utils.PadLeft(plants.PLWT, 5, ' '));
                pw.print(" " + Utils.PadLeft(plants.PAGE, 5, ' '));
                pw.print(" " + Utils.PadLeft(plants.PENV, 5, ' '));
                pw.print(" " + Utils.PadLeft(plants.PLPH, 5, ' '));
                pw.print(" " + Utils.PadLeft(plants.SPRL, 5, ' '));
                if (plants.PLNAME != null) {
                    pw.print("                        " + plants.PLNAME);
                } else {
                    pw.print("                        -99");
                }
                pw.println();
                
                for (Comment comment : comments.getAll(level, Section.Planting)) {
                    pw.println(comment.description);
                }
            }
        }
        // </editor-fold>
    }
}
