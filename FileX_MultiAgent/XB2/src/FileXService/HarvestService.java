package FileXService;

import Extensions.Utils;
import FileXModel.Comment;
import static FileXModel.FileX.comments;
import static FileXModel.FileX.harvestList;
import FileXModel.Harvest;
import FileXModel.HarvestApplication;
import FileXModel.Section;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.PrintWriter;

/**
 *
 * @author Jazzy
 */
public class HarvestService {
    public static void Read(File fileName) {
        try {
            FileReader fReader = new FileReader(fileName);
            BufferedReader br = new BufferedReader(fReader);
            String strRead = null;
            
            String harvestHeader = "";
            boolean bHarvestHeader = false;
            boolean bHarvest = false;
            
            while ((strRead = br.readLine()) != null) {
                String tmp = strRead;
                
                if (tmp.trim().startsWith("*HARVEST DETAILS")) {
                    bHarvest = true;

                } else if (bHarvest && !bHarvestHeader && tmp.trim().startsWith("@")) {
                    harvestHeader = tmp.trim();
                    bHarvestHeader = true;
                } else if (bHarvest && bHarvestHeader) {
                    if ("".equals(tmp.trim()) || tmp.trim().startsWith("*")) {
                        bHarvest = false;
                        bHarvestHeader = false;
                        continue;
                    }
                    else if(strRead.trim().startsWith("!")){
                        int l = 1;
                        if(harvestList.GetSize() > 0){
                            l = harvestList.GetAtIndex(harvestList.GetSize() - 1).GetLevel();
                        }
                        comments.addComment(l, Section.Harvest, strRead);
                        continue;
                    }
                    
                    //@H HDATE  HSTG  HCOM HSIZE   HPC  HBPC HNAME
                    Harvest harvest;
                    HarvestApplication harvestApp = new HarvestApplication();
                    Integer level = Integer.valueOf(tmp.substring(0, 2).trim());

                    boolean isAdd = false;
                    if(!harvestList.IsLevelExists(level)) {
                        harvest = new Harvest();
                        harvest.SetLevel(level);
                        isAdd = true;
                    } else {
                        harvest = (Harvest)harvestList.GetAt(level);
                    }

                    try {
                        harvestApp.HDATE = Utils.GetDate(harvestHeader, tmp, "HDATE", 5);
                    } catch (Exception e) {
                        harvestApp.HDAY = Utils.GetInteger(harvestHeader, tmp, "HDATE", 5);
                    }
                    harvestApp.HSTG = Utils.GetString(harvestHeader, tmp, " HSTG", 5);
                    harvestApp.HCOM = Utils.GetString(harvestHeader, tmp, " HCOM", 5);
                    harvestApp.HSIZE = Utils.GetString(harvestHeader, tmp, "HSIZE", 5);
                    harvestApp.HPC = Utils.GetFloat(harvestHeader, tmp, "HPC", 5);
                    harvestApp.HBPC = Utils.GetFloat(harvestHeader, tmp, "HBPC", 5);
                    harvest.HNAME = Utils.GetString(harvestHeader, tmp, "HNAME", tmp.length() - harvestHeader.indexOf("HNAME"));
                    harvest.AddApp(harvestApp);

                    if(isAdd) {
                        harvestList.AddNew(harvest);
                    }
                }
            }
        } catch (Exception ex) {
            System.out.println(ex.getMessage());
        }
    }
    
    public static void Extract(PrintWriter pw) {
        // <editor-fold defaultstate="collapsed" desc="Harvest">
        if (harvestList.GetSize() > 0) {
            pw.println();
            pw.println("*HARVEST DETAILS");
            pw.println("@H HDATE  HSTG  HCOM HSIZE   HPC  HBPC HNAME");
            for (int i = 0; i < harvestList.GetSize(); i++) {
                Harvest harvest = (Harvest)harvestList.GetAtIndex(i);
                Integer level = harvest.GetLevel();
                
                for (int n = 0; n < harvest.GetSize(); n++) {
                    HarvestApplication harvestApp = harvest.GetApp(n);

                    pw.print(Utils.PadLeft(level, 2, ' '));

                    if(harvestApp.HDATE != null)
                        pw.print(" " + Utils.PadRight(Utils.JulianDate(harvestApp.HDATE), 5, ' '));
                    else if(harvestApp.HDAY != null)
                        pw.print(" " + Utils.PadLeft(harvestApp.HDAY, 5, ' '));
                    else
                        pw.print(" " + Utils.PadLeft("-99", 5, ' '));

                    if(harvestApp.HSTG != null)
                        pw.print(" " + Utils.PadRight(harvestApp.HSTG, 5, ' '));
                    else
                        pw.print(" " + ' ' + "-99" + ' ');
                    
                    pw.print(" " + Utils.PadLeft(harvestApp.HCOM, 5, ' '));
                    pw.print(" " + Utils.PadLeft(harvestApp.HSIZE, 5, ' '));
                    pw.print(" " + Utils.PadLeft(harvestApp.HPC, 5, ' '));
                    pw.print(" " + Utils.PadLeft(harvestApp.HBPC, 5, ' '));
                    if (harvest.HNAME != null) {
                        pw.print(" " + harvest.HNAME);
                    } else {
                        pw.print(" -99");
                    }
                    pw.println();
                }
                
                for (Comment comment : comments.getAll(level, Section.Harvest)) {
                    pw.println(comment.description);
                }
            }
        }
        // </editor-fold>
    }
}
