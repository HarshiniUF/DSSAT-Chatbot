package FileXService;

import DSSATModel.CropList;
import DSSATModel.ExperimentType;
import Extensions.Utils;
import static FileXModel.FileX.general;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.PrintWriter;

/**
 *
 * @author Jazz
 */
public class GeneralService {
    public static void Read(File fileName){
        try {
            String xFile = fileName.getName();

            general.InstituteCode = xFile.substring(0, 2);
            general.SiteCode = xFile.substring(2, 4);
            general.Year = (Integer.parseInt(xFile.substring(4, 6)) > 60) ? "19" + xFile.substring(4, 6) : "20" + xFile.substring(4, 6);
            general.ExperimentNumber = xFile.substring(6, 8);

            if (xFile.endsWith("SQX")) {
                general.FileType = ExperimentType.Sequential;
            } else if (xFile.endsWith("SNX")) {
                general.FileType = ExperimentType.Seasonal;
            } else if (xFile.endsWith("GSX")) {
                general.FileType = ExperimentType.Spatial;
            } else if (xFile.endsWith("FCX")) {
                general.FileType = ExperimentType.Forecast;
            } else {
                general.FileType = ExperimentType.Experimental;
                try {
                    general.crop = CropList.GetAt(xFile.substring(9, 11));
                } catch (Exception e) {
                }
            }
            
            FileReader fReader = new FileReader(fileName);
            BufferedReader br = new BufferedReader(fReader);
            String strRead = null;
            
            String plotHeader = "@ PAREA  PRNO  PLEN  PLDR  PLSP  PLAY HAREA  HRNO  HLEN  HARM.........";
            boolean bPeople = false;
            boolean bAddress = false;
            boolean bSite = false;
            boolean bNotes = false;
            boolean bPlot = false;
            
            while ((strRead = br.readLine()) != null) {
                if (strRead.trim().startsWith("*EXP.DETAILS:")) {
                    String temp = strRead.substring(13, strRead.length()).trim();
                    String startS = general.InstituteCode + general.SiteCode + general.Year.substring(2, 4) + general.ExperimentNumber + getFileXType();

                    if (temp.startsWith(startS)) {
                        temp = temp.replaceFirst(startS, "").trim();
                    }
                    general.ExperimentName = temp;
                }
                
                // <editor-fold defaultstate="collapsed" desc="PEOPLE">
                else if (strRead.startsWith("@PEOPLE")) {
                    bPeople = true;

                } else if (bPeople) {
                    if(!strRead.equals("-99"))  general.People = strRead.trim();
                    else general.People = null;
                    bPeople = false;
                }
                // </editor-fold>

                // <editor-fold defaultstate="collapsed" desc="@ADDRESS">
                else if (strRead.startsWith("@ADDRESS")) {
                    bAddress = true;
                } else if (bAddress) {
                    if(!strRead.equals("-99"))  general.Adress = strRead.trim();
                    else general.Adress = null;
                    bAddress = false;
                }
                // </editor-fold>
                
                // <editor-fold defaultstate="collapsed" desc="@SITE">
                else if (strRead.startsWith("@SITE")) {
                    bSite = true;
                } else if (bSite) {
                    if (!strRead.equals("-99")) {
                        general.Site = strRead.trim();
                    } else {
                        general.Site = null;
                    }
                    bSite = false;
                }
                // </editor-fold>
                
                // <editor-fold defaultstate="collapsed" desc="@NOTES">
                else if (strRead.startsWith("@NOTES")) {
                    bNotes = true;
                } else if (bNotes) {
                    if (!strRead.trim().equals("-99")) {
                        if(strRead.trim().startsWith("!") || strRead.trim().startsWith("@") || strRead.trim().startsWith("*") || "".equals(strRead.trim())) {
                            bNotes = false;
                        } else {
                            general.Notes = (general.Notes == null || "".equals(general.Notes)) ? strRead.trim() : general.Notes + "\n" + strRead.trim();
                            //bNotes = false;
                        }
                    }
                }
                // </editor-fold>
                
                // <editor-fold defaultstate="collapsed" desc="PLOT (Plot information & Harvest Information)">
                else if (strRead.startsWith(plotHeader)) {
                    bPlot = true;
                } else if (bPlot) {
                    strRead = Utils.PadRight(strRead, plotHeader.length(), ' ');
                    general.PAREA = Utils.GetFloat(plotHeader, strRead, "PAREA", 5);
                    general.PRNO = Utils.GetInteger(plotHeader, strRead, "PRNO", 5);
                    general.PLEN = Utils.GetFloat(plotHeader, strRead, "PLEN", 5);
                    general.PLDR = Utils.GetInteger(plotHeader, strRead, "PLDR", 5);
                    general.PLSP = Utils.GetFloat(plotHeader, strRead, "PLSP", 5);
                    general.PLAY = Utils.GetString(plotHeader, strRead, "PLAY", 5);
                    general.HAREA = Utils.GetFloat(plotHeader, strRead, "HAREA", 5);
                    general.HRNO = Utils.GetInteger(plotHeader, strRead, "HRNO", 5);
                    general.HLEN = Utils.GetFloat(plotHeader, strRead, "HLEN", 5);
                    general.HARM = Utils.GetString(plotHeader, strRead, "HARM", 13);
                    bPlot = false;
                }
                // </editor-fold>
            }
            
            br.close();
            fReader.close();
            

        } catch (Exception ex) {
            System.out.println(ex.getMessage());
        }
    }
    
    public static void Extract(PrintWriter pw){
        
        // <editor-fold defaultstate="collapsed" desc="GENERAL">
        pw.println("*EXP.DETAILS: " + general.InstituteCode + general.SiteCode + general.Year.substring(2,4) + Utils.PadLeft(general.ExperimentNumber, 2, '0')
                + getFileXType()
                + " " + (general.ExperimentName != null && !"".equals(general.ExperimentName) ? general.ExperimentName : ""));
        pw.println();
        pw.println("*GENERAL");

        pw.println("@PEOPLE");
        if (general.People != null && !"".equals(general.People)) {
            pw.println(" " + general.People);

        } else {
            pw.println("-99");


        }
        pw.println("@ADDRESS");
        if (general.Adress != null && !"".equals(general.Adress)) {
            pw.println(" " + general.Adress);

        } else {
            pw.println("-99");

        }
        pw.println("@SITE");
        if (general.Site != null && !"".equals(general.Site)) {
            pw.println(" " + general.Site);

        } else {
            pw.println("-99");
        }

        // <editor-fold defaultstate="collapsed" desc="PLOT">
        
        pw.println("@ PAREA  PRNO  PLEN  PLDR  PLSP  PLAY HAREA  HRNO  HLEN  HARM.........");
        pw.print(Utils.PadLeft(general.PAREA, 7, ' '));

        pw.print(Utils.PadLeft(general.PRNO, 6, ' '));
        pw.print(Utils.PadLeft(general.PLEN, 6, ' '));
        pw.print(Utils.PadLeft(general.PLDR, 6, ' '));
        pw.print(Utils.PadLeft(general.PLSP, 6, ' '));
        pw.print(Utils.PadLeft(general.PLAY, 6, ' '));
        pw.print(Utils.PadLeft(general.HAREA, 6, ' '));
        pw.print(Utils.PadLeft(general.HRNO, 6, ' '));
        pw.print(Utils.PadLeft(general.HLEN, 6, ' '));
        pw.print("  " + general.HARM);
        pw.println();
        // </editor-fold>
        
        if (general.Notes != null && !"".equals(general.Notes)) {
            pw.println("@NOTES");
            String[] tmp = general.Notes.split("\n");
            for(int i = 0;i < tmp.length;i++)
                pw.println(tmp[i]);
        }
        
        // </editor-fold>
    }
    
    private static String getFileXType(){
        String fileXType = "";
        if(general.crop != null && general.crop.CropCode != null && !"".equals(general.crop.CropCode)){
            fileXType = general.crop.CropCode;
        }
        else if(general.FileType == ExperimentType.Seasonal){
            fileXType = "SN";
        }
        else if(general.FileType == ExperimentType.Sequential){
            fileXType = "SQ";
        }
        else if(general.FileType == ExperimentType.Spatial){
            fileXType = "GS";
        }
        else if(general.FileType == ExperimentType.Forecast){
            fileXType = "FC";
        }
        
        return fileXType;
    }
}
