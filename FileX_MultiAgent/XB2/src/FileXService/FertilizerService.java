package FileXService;

import Extensions.Utils;
import FileXModel.Comment;
import FileXModel.Fertilizer;
import FileXModel.FertilizerApplication;
import static FileXModel.FileX.comments;
import static FileXModel.FileX.fertilizerList;
import FileXModel.Section;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.PrintWriter;

/**
 *
 * @author Jazzy
 */
public class FertilizerService {
    public static void Read(File fileName) {
        try {
            FileReader fReader = new FileReader(fileName);
            BufferedReader br = new BufferedReader(fReader);
            String strRead;
            
            String fertilizerHeader = "";
            boolean bFertilizerHeader = false;
            boolean bFertilizer = false;
            
            while ((strRead = br.readLine()) != null) {
                String tmp = strRead;
                
                if (tmp.trim().startsWith("*FERTILIZERS (INORGANIC)")) {
                    bFertilizer = true;

                } else if (bFertilizer && !bFertilizerHeader && tmp.trim().startsWith("@")) {
                    fertilizerHeader = tmp.trim();
                    bFertilizerHeader = true;
                } else if (bFertilizer && bFertilizerHeader) {
                    if ("".equals(tmp.trim()) || tmp.trim().startsWith("*")) {
                        bFertilizer = false;
                        bFertilizerHeader = false;
                        continue;
                    }
                    else if(strRead.trim().startsWith("!")){
                        int l = 1;
                        if(fertilizerList.GetSize() > 0){
                            l = fertilizerList.GetAtIndex(fertilizerList.GetSize() - 1).GetLevel();
                        }
                        comments.addComment(l, Section.Fertilizer, strRead);
                        continue;
                    }
                    
                    //@F FDATE  FMCD  FACD  FDEP  FAMN  FAMP  FAMK  FAMC  FAMO  FOCD FERNAME
                    Fertilizer fertil;
                    Integer level = Integer.valueOf(tmp.substring(0, 2).trim());

                    boolean isAdd = false;
                    if(!fertilizerList.IsLevelExists(level)) {
                        fertil = new Fertilizer();
                        fertil.SetLevel(level);
                        isAdd = true;
                    } else {
                        fertil = (Fertilizer)fertilizerList.GetAt(level);
                    }

                    FertilizerApplication fertilApp = new FertilizerApplication();

                    try {
                        fertilApp.FDATE = Utils.GetDate(fertilizerHeader, tmp, "FDATE", 5);
                    } catch (Exception e) {
                        fertilApp.FDAY = Utils.GetInteger(fertilizerHeader, tmp, "FDATE", 5);
                    }

                    fertilApp.FMCD = Utils.GetString(fertilizerHeader, tmp, " FMCD", 5);
                    fertilApp.FACD = Utils.GetString(fertilizerHeader, tmp, " FACD", 5);
                    fertilApp.FDEP = Utils.GetFloat(fertilizerHeader, tmp, "FDEP", 5);
                    fertilApp.FAMN = Utils.GetFloat(fertilizerHeader, tmp, "FAMN", 5);
                    fertilApp.FAMP = Utils.GetFloat(fertilizerHeader, tmp, "FAMP", 5);
                    fertilApp.FAMK = Utils.GetFloat(fertilizerHeader, tmp, "FAMK", 5);
                    fertilApp.FAMC = Utils.GetFloat(fertilizerHeader, tmp, "FAMC", 5);
                    fertilApp.FAMO = Utils.GetFloat(fertilizerHeader, tmp, "FAMO", 5);
                    fertilApp.FOCD = Utils.GetString(fertilizerHeader, tmp, " FOCD", 5);
                    fertil.FERNAME = Utils.GetString(fertilizerHeader, tmp, "FERNAME", tmp.length() - fertilizerHeader.indexOf("FERNAME"));
                    fertil.AddApp(fertilApp);

                    if(isAdd) {
                        fertilizerList.AddNew(fertil);
                    }
                }
            }
        } catch (Exception ex) {
            System.out.println(ex.getMessage());
        }
    }
    
    public static void Extract(PrintWriter pw){
        // <editor-fold defaultstate="collapsed" desc="Fertilizer">
        if (fertilizerList.GetSize() > 0) {
            pw.println();
            pw.println("*FERTILIZERS (INORGANIC)");
            pw.println("@F FDATE  FMCD  FACD  FDEP  FAMN  FAMP  FAMK  FAMC  FAMO  FOCD FERNAME");
            for (int i = 0; i < fertilizerList.GetSize(); i++) {
                Fertilizer fertil = (Fertilizer)fertilizerList.GetAtIndex(i);
                Integer level = fertil.GetLevel();
                
                for (int n = 0; n < fertil.GetSize(); n++) {
                    FertilizerApplication ferApp = fertil.GetApp(n);
                    
                    pw.print(Utils.PadLeft(level, 2, ' '));

                    if(ferApp.FDATE != null)
                        pw.print(" " + Utils.PadLeft(Utils.JulianDate(ferApp.FDATE), 5, ' '));
                    else
                        pw.print(" " + Utils.PadLeft(ferApp.FDAY, 5, ' '));

                    pw.print(" " + Utils.PadLeft(ferApp.FMCD, 5, ' '));
                    pw.print(" " + Utils.PadLeft(ferApp.FACD, 5, ' '));
                    pw.print(" " + Utils.PadLeft(ferApp.FDEP, 5, ' '));
                    pw.print(" " + Utils.PadLeft(ferApp.FAMN, 5, ' '));
                    pw.print(" " + Utils.PadLeft(ferApp.FAMP, 5, ' '));
                    pw.print(" " + Utils.PadLeft(ferApp.FAMK, 5, ' '));
                    pw.print(" " + Utils.PadLeft(ferApp.FAMC, 5, ' '));
                    pw.print(" " + Utils.PadLeft(ferApp.FAMO, 5, ' '));
                    pw.print(" " + Utils.PadLeft(ferApp.FOCD, 5, ' '));
                    if (fertil.FERNAME != null) {
                        pw.print(" " + fertil.FERNAME);
                    } else {
                        pw.print(" -99");
                    }
                    pw.println();
                }
                
                for (Comment comment : comments.getAll(level, Section.Fertilizer)) {
                    pw.println(comment.description);
                }
            }
        }
        // </editor-fold>
    }
}
