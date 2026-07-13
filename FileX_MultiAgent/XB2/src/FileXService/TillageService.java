package FileXService;

import Extensions.Utils;
import FileXModel.Comment;
import static FileXModel.FileX.comments;
import static FileXModel.FileX.tillageList;
import FileXModel.Section;
import FileXModel.Tillage;
import FileXModel.TillageApplication;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.io.PrintWriter;

/**
 *
 * @author Jazz
 */
public class TillageService {
    public static void Read(File fileName) {
        try {
            FileReader fReader = new FileReader(fileName);
            BufferedReader br = new BufferedReader(fReader);
            String strRead;
            
            String tillageHeader = "";
            boolean bTillageHeader = false;
            boolean bTillage = false;
            
            while ((strRead = br.readLine()) != null) {
                String tmp = strRead;
                
                if (tmp.trim().startsWith("*TILLAGE AND ROTATIONS")) {
                    bTillage = true;

                } else if (bTillage && !bTillageHeader && tmp.trim().startsWith("@")) {
                    tillageHeader = tmp.trim();
                    bTillageHeader = true;
                } else if (bTillage && bTillageHeader) {
                    if ("".equals(tmp.trim()) || tmp.trim().startsWith("*")) {
                        bTillage = false;
                        bTillageHeader = false;
                        continue;
                    }
                    else if(strRead.trim().startsWith("!")){
                        int l = 1;
                        if(tillageList.GetSize() > 0){
                            l = tillageList.GetAtIndex(tillageList.GetSize() - 1).GetLevel();
                        }
                        comments.addComment(l, Section.Tillage, strRead);
                        continue;
                    }
                    
                    //@T TDATE TIMPL  TDEP TNAME
                    Tillage tillage;
                    TillageApplication tillageApp = new TillageApplication();
                    Integer level = Integer.valueOf(tmp.substring(0, 2).trim());

                    boolean isAdd = false;
                    if(!tillageList.IsLevelExists(level)) {
                        tillage = new Tillage();
                        tillage.SetLevel(level);
                        isAdd = true;
                    } else {
                        tillage = (Tillage)tillageList.GetAt(level);
                    }

                    try {
                        tillageApp.TDATE = Utils.GetDate(tillageHeader, tmp, "TDATE", 5);
                    } catch (Exception ex) {
                        tillageApp.TDAY = Utils.GetInteger(tillageHeader, tmp, "TDATE", 5);
                    }
                    
                    tillageApp.TIMPL = Utils.GetString(tillageHeader, tmp, "TIMPL", 5);
                    tillageApp.TDEP = Utils.GetInteger(tillageHeader, tmp, "TDEP", 5);
                    tillage.TNAME = Utils.GetString(tillageHeader, tmp, "TNAME", tmp.length() - tillageHeader.indexOf("TNAME"));
                    tillage.AddApp(tillageApp);

                    if(isAdd) {
                        tillageList.AddNew(tillage);
                    }
                }
            }
        } catch (IOException | NumberFormatException ex) {
            System.out.println(ex.getMessage());
        }
    }
    
    public static void Extract(PrintWriter pw) {
        // <editor-fold defaultstate="collapsed" desc="Tillage">
        if (tillageList.GetSize() > 0) {
            pw.println();
            pw.println("*TILLAGE AND ROTATIONS");
            pw.println("@T TDATE TIMPL  TDEP TNAME");
            for (int i = 0; i < tillageList.GetSize(); i++) {
                Tillage tillage = (Tillage)tillageList.GetAtIndex(i);
                Integer level = tillage.GetLevel();
                
                for (int n = 0; n < tillage.GetSize(); n++) {
                    TillageApplication tilApp = tillage.GetApp(n);

                    
                    pw.print(Utils.PadLeft(level, 2, ' '));

                    try {
                        if(tilApp.TDATE != null)
                            pw.print(" " + Utils.PadRight(Utils.JulianDate(tilApp.TDATE), 5, ' '));
                        else
                            pw.print(" " + Utils.PadRight(tilApp.TDAY, 5, ' '));
                    } catch (Exception e) {
                        pw.print(" " + Utils.PadLeft("-99", 5, ' '));
                    }

                    pw.print(" " + Utils.PadLeft(tilApp.TIMPL, 5, ' '));
                    pw.print(" " + Utils.PadLeft(tilApp.TDEP, 5, ' '));
                    if (tillage.TNAME != null) {
                        pw.print(" " + tillage.TNAME);
                    } else {
                        pw.print(" -99");
                    }
                    pw.println();
                }
                
                for (Comment comment : comments.getAll(level, Section.Tillage)) {
                    pw.println(comment.description);
                }
            }
        }
        // </editor-fold>
    }
}
