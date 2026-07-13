package FileXService;

import DSSATModel.EnvironmentFactorList;
import Extensions.Utils;
import FileXModel.Comment;
import FileXModel.EnvironmentApplication;
import FileXModel.Environmental;
import static FileXModel.FileX.comments;
import static FileXModel.FileX.environmentals;
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
public class EnvironmentService {
    public static void Read(File fileName) {
        try {
            FileReader fReader = new FileReader(fileName);
            BufferedReader br = new BufferedReader(fReader);
            String strRead;
            
            String environmentHeader = "";
            boolean bEnvironmentHeader = false;
            boolean bEnvironment = false;
            
            while ((strRead = br.readLine()) != null) {
                String tmp = strRead;
                
                if (tmp.trim().startsWith("*ENVIRONMENT MODIFICATIONS")) {
                    bEnvironment = true;

                } else if (bEnvironment && !bEnvironmentHeader && tmp.trim().startsWith("@")) {
                    environmentHeader = tmp.trim();
                    bEnvironmentHeader = true;
                } else if (bEnvironment && bEnvironmentHeader) {
                    if ("".equals(tmp.trim()) || tmp.trim().startsWith("*")) {
                        bEnvironment = false;
                        bEnvironmentHeader = false;
                        continue;
                    }
                    else if(strRead.trim().startsWith("!")){
                        int l = 1;
                        if(environmentals.GetSize() > 0){
                            l = environmentals.GetAtIndex(environmentals.GetSize() - 1).GetLevel();
                        }
                        comments.addComment(l, Section.Environment, strRead);
                        continue;
                    }
                    //@E ODATE EDAY  ERAD  EMAX  EMIN  ERAIN ECO2  EDEW  EWIND ENVNAME
                    Environmental env;
                    EnvironmentApplication envApp = new EnvironmentApplication();
                    Integer level = Integer.valueOf(tmp.substring(0, 2).trim());

                    boolean isAdd = false;
                    if(!environmentals.IsLevelExists(level)) {
                        env = new Environmental();
                        env.SetLevel(level);
                        isAdd = true;
                    } else {
                        env = (Environmental)environmentals.GetAt(level);
                    }

                    try{
                        envApp.ODATE = Utils.GetDate(environmentHeader, tmp, "ODATE", 5);
                        envApp.EDAY_Fact = EnvironmentFactorList.GetAt(0, Utils.GetString(environmentHeader, tmp, "EDAY", 1));
                        envApp.EDAY = Utils.GetDouble(environmentHeader, tmp, "EDAY ", 3);
                        envApp.ERAD_Fact = EnvironmentFactorList.GetAt(0, Utils.GetString(environmentHeader, tmp, "ERAD", 1));
                        envApp.ERAD = Utils.GetDouble(environmentHeader, tmp, "ERAD ", 3);
                        envApp.EMAX_Fact = EnvironmentFactorList.GetAt(0, Utils.GetString(environmentHeader, tmp, "EMAX", 1));
                        envApp.EMAX = Utils.GetDouble(environmentHeader, tmp, "EMAX ", 3);
                        envApp.EMIN_Fact = EnvironmentFactorList.GetAt(0, Utils.GetString(environmentHeader, tmp, "EMIN", 1));
                        envApp.EMIN = Utils.GetDouble(environmentHeader, tmp, "EMIN ", 3);
                        envApp.ERAIN_Fact = EnvironmentFactorList.GetAt(0, Utils.GetString(environmentHeader, tmp, "ERAIN", 1));
                        envApp.ERAIN = Utils.GetDouble(environmentHeader, tmp, "ERAIN", 3);
                        envApp.ECO2_Fact = EnvironmentFactorList.GetAt(0, Utils.GetString(environmentHeader, tmp, "ECO2", 1));
                        envApp.ECO2 = Utils.GetDouble(environmentHeader, tmp, "ECO2 ", 3);
                        envApp.EDEW_Fact = EnvironmentFactorList.GetAt(0, Utils.GetString(environmentHeader, tmp, "EDEW", 1));
                        envApp.EDEW = Utils.GetDouble(environmentHeader, tmp, "EDEW ", 3);
                        envApp.EWIND_Fact = EnvironmentFactorList.GetAt(0, Utils.GetString(environmentHeader, tmp, "EWIND", 1));
                        envApp.EWIND = Utils.GetDouble(environmentHeader, tmp, " EWIND", 3);
                        env.ENVNAME = Utils.GetString(environmentHeader, tmp, "ENVNAME", tmp.length() - environmentHeader.indexOf("ENVNAME"));
                        env.AddApp(envApp);
                    }catch(Exception ee){
                        System.out.println(ee.getMessage());
                    }

                    if(isAdd) {
                        environmentals.AddNew(env);
                    }
                }
            }
        } catch (Exception ex) {
            System.out.println(ex.getMessage());
        }
    }
    
    public static void Extract(PrintWriter pw) {
        // <editor-fold defaultstate="collapsed" desc="Environmental">
        if (environmentals.GetSize() > 0) {
            pw.println();
            pw.println("*ENVIRONMENT MODIFICATIONS");
            pw.println("@E ODATE EDAY  ERAD  EMAX  EMIN  ERAIN ECO2  EDEW  EWIND ENVNAME");
            
            DecimalFormat df1 = new DecimalFormat("0.0");

            for (int i = 0; i < environmentals.GetSize(); i++) {
                Environmental env = (Environmental) environmentals.GetAtIndex(i);
                Integer level = env.GetLevel();
                
                for (int n = 0; n < env.GetSize(); n++) {
                    EnvironmentApplication envApp = env.GetApp(n);

                    
                    pw.print(Utils.PadLeft(level, 2, ' '));

                    try {
                        pw.print(" " + Utils.PadRight(Utils.JulianDate(envApp.ODATE), 5, ' '));
                    } catch (Exception e) {
                        pw.print(" " + Utils.PadLeft("-99", 5, ' '));
                    }

                    pw.print(" " + envApp.EDAY_Fact.Code);
                    pw.print(Utils.PadLeft(envApp.EDAY.toString(), 4, ' ', false));
                    pw.print(" " + envApp.ERAD_Fact.Code);
                    pw.print(Utils.PadLeft(envApp.ERAD.toString(), 4, ' ', false));
                    pw.print(" " + envApp.EMAX_Fact.Code);
                    pw.print(Utils.PadLeft(envApp.EMAX.toString(), 4, ' ', false));
                    pw.print(" " + envApp.EMIN_Fact.Code);
                    pw.print(Utils.PadLeft(envApp.EMIN.toString(), 4, ' ', false));
                    pw.print(" " + envApp.ERAIN_Fact.Code);
                    pw.print(Utils.PadLeft(df1.format(envApp.ERAIN), 4, ' '));
                    pw.print(" " + envApp.ECO2_Fact.Code);
                    pw.print(Utils.PadLeft(envApp.ECO2.toString(), 4, ' ', false));
                    pw.print(" " + envApp.EDEW_Fact.Code);
                    pw.print(Utils.PadLeft(envApp.EDEW.toString(), 4, ' ', false));
                    pw.print(" " + envApp.EWIND_Fact.Code);
                    pw.print(Utils.PadLeft(envApp.EWIND.toString(), 4, ' ', false));
                    if (env.ENVNAME != null) {
                        pw.print(" " + env.ENVNAME);
                    } else {
                        pw.print(" -99");
                    }
                    pw.println();
                }
                
                for (Comment comment : comments.getAll(level, Section.Environment)) {
                    pw.println(comment.description);
                }
            }
        }
        // </editor-fold>
    }
}
