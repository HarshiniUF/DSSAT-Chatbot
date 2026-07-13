package FileXService;

import Extensions.Utils;
import FileXModel.Comment;
import static FileXModel.FileX.comments;
import static FileXModel.FileX.initialList;
import FileXModel.InitialCondition;
import FileXModel.InitialConditionApplication;
import FileXModel.Section;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.PrintWriter;
import java.text.DecimalFormat;

/**
 *
 * @author Jazzy
 */
public class InitialConditionService {
    public static void Read(File fileName) {
        try {
            FileReader fReader = new FileReader(fileName);
            BufferedReader br = new BufferedReader(fReader);
            String strRead;
            
            String initHeader1 = "";
            String initHeader2 = "";
            boolean bInitHeader1 = false;
            boolean bInitHeader2 = false;
            boolean bInit = false;
            
            while ((strRead = br.readLine()) != null) {
                String tmp = strRead;
                
                if (tmp.trim().startsWith("*INITIAL CONDITIONS")) {
                    bInit = true;
                } else if (bInit && !bInitHeader1 && !bInitHeader2 && tmp.trim().startsWith("@")) {
                    initHeader1 = tmp.trim();
                    bInitHeader1 = true;
                } else if (bInit && bInitHeader1 && !bInitHeader2 && tmp.trim().startsWith("@")) {
                    initHeader2 = tmp.trim();
                    bInitHeader2 = true;
                } else if (bInit && bInitHeader1 && bInitHeader2 && tmp.trim().startsWith("@")) {
                    bInitHeader2 = false;
                }else if (bInit && bInitHeader1 && !bInitHeader2) {
                    if ("".equals(tmp.trim())) {
                        bInit = false;
                        bInitHeader1 = false;
                        bInitHeader2 = false;
                        continue;
                    }
                    else if(strRead.trim().startsWith("!")){
                        int l = 1;
                        if(initialList.GetSize() > 0){
                            l = initialList.GetAtIndex(initialList.GetSize() - 1).GetLevel();
                        }
                        comments.addComment(l, Section.InitialCondition1, strRead);
                        continue;
                    }
                    //@C   PCR ICDAT  ICRT  ICND  ICRN  ICRE  ICWD ICRES ICREN ICREP ICREP ICRID ICNAME
                    InitialCondition init = new InitialCondition();
                    Integer level = Integer.valueOf(tmp.substring(0, 2).trim());
                    init.SetLevel(level);
                    init.PCR = Utils.GetString(initHeader1, tmp, "  PCR", 5);
                    init.ICDAT = Utils.GetDate(initHeader1, tmp, "ICDAT", 5);
                    init.ICRT = Utils.GetFloat(initHeader1, tmp, "ICRT", 5);
                    init.ICND = Utils.GetFloat(initHeader1, tmp, "ICND", 5);
                    init.ICRN = Utils.GetFloat(initHeader1, tmp, "ICRN", 5);
                    init.ICRE = Utils.GetFloat(initHeader1, tmp, "ICRE", 5);
                    init.ICWD = Utils.GetFloat(initHeader1, tmp, "ICWD", 5);
                    init.ICRES = Utils.GetFloat(initHeader1, tmp, "ICRES", 5);
                    init.ICREN = Utils.GetFloat(initHeader1, tmp, "ICREN", 5);
                    init.ICREP = Utils.GetFloat(initHeader1, tmp, "ICREP", 5);
                    init.ICRIP = Utils.GetFloat(initHeader1, tmp, "ICRIP", 5);
                    init.ICRID = Utils.GetFloat(initHeader1, tmp, "ICRID", 5);
                    init.ICNAME = Utils.GetString(initHeader1, tmp, "ICNAME", tmp.length() - initHeader1.indexOf("ICNAME"));

                    initialList.AddNew(init);
                } else if (bInit && bInitHeader1 && bInitHeader2) {
                    if ("".equals(tmp.trim())) {
                        bInit = false;
                        bInitHeader1 = false;
                        bInitHeader2 = false;
                        continue;
                    }
                    else if(strRead.trim().startsWith("!")){
                        int l = 1;
                        if(initialList.GetSize() > 0){
                            l = initialList.GetAtIndex(initialList.GetSize() - 1).GetLevel();
                        }
                        comments.addComment(l, Section.InitialCondition2, strRead);
                        continue;
                    }
                    //@C  ICBL  SH2O  SNH4  SNO3

                    try {
                        Integer level = Integer.valueOf(tmp.substring(0, 2).trim());
                        InitialCondition init = (InitialCondition)initialList.GetAt(level);
                        InitialConditionApplication initApp = new InitialConditionApplication();

                        initApp.ICBL = Utils.GetFloat(initHeader2, tmp, "ICBL", 5);
                        initApp.SH2O = Utils.GetFloat(initHeader2, tmp, "SH2O", 5);
                        initApp.SNH4 = Utils.GetFloat(initHeader2, tmp, "SNH4", 5);
                        initApp.SNO3 = Utils.GetFloat(initHeader2, tmp, "SNO3", 5);
                        init.AddApp(initApp);

                    } catch (NumberFormatException numberFormatException) {
                    }
                }
            }
        } catch (Exception ex) {
            System.out.println(ex.getMessage());
        }
    }
    
    public static void Extract(PrintWriter pw){
        // <editor-fold defaultstate="collapsed" desc="Initial Condition">
        DecimalFormat df1 = new DecimalFormat("0.0");
        DecimalFormat df3 = new DecimalFormat("0.000");
        
        if (initialList.GetSize() > 0) {
            pw.println();
            pw.println("*INITIAL CONDITIONS");
            for (int i = 0; i < initialList.GetSize(); i++) {
                InitialCondition init = (InitialCondition)initialList.GetAtIndex(i);
                Integer level = init.GetLevel();

                pw.println("@C   PCR ICDAT  ICRT  ICND  ICRN  ICRE  ICWD ICRES ICREN ICREP ICRIP ICRID ICNAME");
                pw.print(Utils.PadLeft(level, 2, ' '));
                pw.print(" " + Utils.PadLeft(init.PCR, 5, ' '));
                pw.print(" " + Utils.PadLeft(Utils.JulianDate(init.ICDAT), 5, ' '));
                pw.print(" " + Utils.PadLeft(init.ICRT, 5, ' '));
                pw.print(" " + Utils.PadLeft(init.ICND, 5, ' '));
                pw.print(" " + Utils.PadLeft(init.ICRN, 5, ' '));
                pw.print(" " + Utils.PadLeft(init.ICRE, 5, ' '));
                pw.print(" " + Utils.PadLeft(init.ICWD, 5, ' '));
                pw.print(" " + Utils.PadLeft(init.ICRES, 5, ' '));
                pw.print(" " + Utils.PadLeft(init.ICREN, 5, ' '));
                pw.print(" " + Utils.PadLeft(init.ICREP, 5, ' '));
                pw.print(" " + Utils.PadLeft(init.ICRIP, 5, ' '));
                pw.print(" " + Utils.PadLeft(init.ICRID, 5, ' '));
                if (init.ICNAME != null) {
                    pw.print(" " + init.ICNAME);
                } else {
                    pw.print(" -99");
                }
                pw.println();
                
                for (Comment comment : comments.getAll(level, Section.InitialCondition1)) {
                    pw.println(comment.description);
                }
                
                if (init.GetSize() > 0) {
                    pw.println("@C  ICBL  SH2O  SNH4  SNO3");

                    for (int n = 0; n < init.GetSize(); n++) {
                        InitialConditionApplication initApp = init.GetApp(n);
                        pw.print(Utils.PadLeft(level, 2, ' '));
                        pw.print(" " + Utils.PadLeft(initApp.ICBL.toString(), 5, ' ', false));
                        pw.print(" " + Utils.PadLeft(df3.format(initApp.SH2O), 5, ' ', false));
                        pw.print(" " + Utils.PadLeft(df1.format(initApp.SNH4), 5, ' ', false));
                        pw.print(" " + Utils.PadLeft(df1.format(initApp.SNO3), 5, ' ', false));
                        pw.println();
                    }
                    
                    for (Comment comment : comments.getAll(level, Section.InitialCondition2)) {
                        pw.println(comment.description);
                    }
                }
            }
        }
        // </editor-fold>
    }
}
