package FileXService;

import Extensions.Utils;
import FileXModel.Comment;
import static FileXModel.FileX.comments;
import FileXModel.Treatment;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.PrintWriter;
import static FileXModel.FileX.treatments;
import FileXModel.Section;

/**
 *
 * @author PCMIWS16
 */
public class TreatmentService {
    public static void Read(File fileName) {
        try {
            FileReader fReader = new FileReader(fileName);
            BufferedReader br = new BufferedReader(fReader);
            String strRead;
            
            String treatmentHeader = "";
            boolean bTreatmentHeader = false;
            boolean bTreatment = false;
            
            while ((strRead = br.readLine()) != null) {
                if (strRead.trim().startsWith("*TREATMENTS")) {
                    bTreatment = true;

                } else if (bTreatment && !bTreatmentHeader && strRead.trim().startsWith("@")) {
                    treatmentHeader = strRead.trim();
                    bTreatmentHeader = true;
                } 
                else if(bTreatment && bTreatmentHeader && strRead.trim().startsWith("*")){
                    bTreatment = false;
                    bTreatmentHeader = false;
                }
                else if (bTreatment && bTreatmentHeader && !"".equals(strRead.trim())) {
                    if(strRead.trim().startsWith("!")){
                        int l = 1;
                        if(treatments.GetSize() > 0){
                            l = treatments.GetAtIndex(treatments.GetSize() - 1).GetLevel();
                        }
                        comments.addComment(l, Section.Treatment, strRead);
                        continue;
                    }
                    //TNAME.................... CU FL SA IC MP MI MF MR MC MT ME MH SM
                    Treatment treatment = new Treatment();
                    //treatment.N = Utils.GetInteger(treatmentHeader, strRead, "@N", 2);
                    treatment.SetLevel(Utils.GetInteger(treatmentHeader, strRead, "@N", 2));
                    
                    treatment.R = Utils.GetString(treatmentHeader, strRead, " R", 2);
                    treatment.O = Utils.GetString(treatmentHeader, strRead, " O", 2);
                    treatment.C = Utils.GetString(treatmentHeader, strRead, " C", 2);
                    
                    treatment.TNAME = Utils.GetString(treatmentHeader, strRead, "TNAME", 25);
                    treatment.CU = Utils.GetInteger(treatmentHeader, strRead, " CU", 3);
                    treatment.FL = Utils.GetInteger(treatmentHeader, strRead, " FL", 3);
                    treatment.SA = Utils.GetInteger(treatmentHeader, strRead, " SA", 3);
                    treatment.IC = Utils.GetInteger(treatmentHeader, strRead, " IC", 3);
                    treatment.MP = Utils.GetInteger(treatmentHeader, strRead, " MP", 3);
                    treatment.MI = Utils.GetInteger(treatmentHeader, strRead, " MI", 3);
                    treatment.MF = Utils.GetInteger(treatmentHeader, strRead, " MF", 3);
                    treatment.MR = Utils.GetInteger(treatmentHeader, strRead, " MR", 3);
                    treatment.MC = Utils.GetInteger(treatmentHeader, strRead, " MC", 3);
                    treatment.MT = Utils.GetInteger(treatmentHeader, strRead, " MT", 3);
                    treatment.ME = Utils.GetInteger(treatmentHeader, strRead, " ME", 3);
                    treatment.MH = Utils.GetInteger(treatmentHeader, strRead, " MH", 3);
                    treatment.SM = Utils.GetInteger(treatmentHeader, strRead, " SM", 3);
                    treatments.AddNew(treatment);
                }
            }
        } catch (Exception ex) {
            System.out.println(ex.getMessage());
        }
    }
    
    public static void Extract(PrintWriter pw){
        // <editor-fold defaultstate="collapsed" desc="Treatment">
        if (treatments.GetSize() > 0) {
            pw.println();
            pw.println("*TREATMENTS                        -------------FACTOR LEVELS------------");
            pw.println("@N R O C TNAME.................... CU FL SA IC MP MI MF MR MC MT ME MH SM");
            for (int i = 0; i < treatments.GetSize(); i++) {
                Treatment treat = (Treatment) treatments.GetAtIndex(i);
                int level = treat.GetLevel();
                pw.print(Utils.PadLeft(level, 2, ' '));
                
//                if(FileX.general.FileType != ExperimentType.Sequential)
//                    pw.print(" 1 0 0");
//                else{
                    try {
                        if (!"".equals(treat.R)) {
                            pw.print(' ' + treat.R.substring(0, 1));
                        } else {
                            pw.print(' ' + "0");
                        }
                    } catch (Exception e) {
                        pw.print(' ' + "0");
                    }
                    try {
                        if (!"".equals(treat.O)) {
                            pw.print(' ' + treat.O.substring(0, 1));
                        } else {
                            pw.print(' ' + "0");
                        }
                    } catch (Exception e) {
                        pw.print(' ' + "0");
                    }
                    try {
                        if (!"".equals(treat.C)) {
                            pw.print(' ' + treat.C.substring(0, 1));
                        } else {
                            pw.print(' ' + "0");
                        }
                    } catch (Exception e) {
                        pw.print(' ' + "0");
                    }
//                }               
                
                try {
                    if (!"".equals(treat.TNAME)) {
                        pw.print(" " + Utils.PadRight(treat.TNAME, 25, ' '));
                    } else {
                        pw.print(" " + Utils.PadRight("", 25, ' '));
                    }
                } catch (Exception e) {
                    pw.print(" " + Utils.PadRight("", 25, ' '));
                }
                try {
                    String tmp = treat.CU.toString();
                    pw.print(" " + Utils.PadLeft(tmp, 2, ' '));
                } catch (Exception e) {
                    pw.print("  0");
                }
                try {
                    String tmp = treat.FL.toString();
                    pw.print(" " + Utils.PadLeft(tmp, 2, ' '));
                } catch (Exception e) {
                    pw.print("  0");
                }
                try {
                    String tmp = treat.SA.toString();
                    pw.print(" " + Utils.PadLeft(tmp, 2, ' '));
                } catch (Exception e) {
                    pw.print("  0");
                }
                try {
                    String tmp = treat.IC.toString();
                    pw.print(" " + Utils.PadLeft(tmp, 2, ' '));
                } catch (Exception e) {
                    pw.print("  0");
                }
                try {
                    String tmp = treat.MP.toString();
                    pw.print(" " + Utils.PadLeft(tmp, 2, ' '));
                } catch (Exception e) {
                    pw.print("  0");
                }
                try {
                    String tmp = treat.MI.toString();
                    pw.print(" " + Utils.PadLeft(tmp, 2, ' '));
                } catch (Exception e) {
                    pw.print("  0");
                }
                try {
                    String tmp = treat.MF.toString();
                    pw.print(" " + Utils.PadLeft(tmp, 2, ' '));
                } catch (Exception e) {
                    pw.print("  0");
                }
                try {
                    String tmp = treat.MR.toString();
                    pw.print(" " + Utils.PadLeft(tmp, 2, ' '));
                } catch (Exception e) {
                    pw.print("  0");
                }
                try {
                    String tmp = treat.MC.toString();
                    pw.print(" " + Utils.PadLeft(tmp, 2, ' '));
                } catch (Exception e) {
                    pw.print("  0");
                }
                try {
                    String tmp = treat.MT.toString();
                    pw.print(" " + Utils.PadLeft(tmp, 2, ' '));
                } catch (Exception e) {
                    pw.print("  0");
                }
                try {
                    String tmp = treat.ME.toString();
                    pw.print(" " + Utils.PadLeft(tmp, 2, ' '));
                } catch (Exception e) {
                    pw.print("  0");
                }
                try {
                    String tmp = treat.MH.toString();
                    pw.print(" " + Utils.PadLeft(tmp, 2, ' '));
                } catch (Exception e) {
                    pw.print("  0");
                }
                try {
                    String tmp = treat.SM.toString();
                    pw.print(" " + Utils.PadLeft(tmp, 2, ' '));
                } catch (Exception e) {
                    pw.print("  0");
                }
                pw.println();
                
                for (Comment comment : comments.getAll(level, Section.Treatment)) {
                    pw.println(comment.description);
                }
            }
        }
        // </editor-fold>
    }
}
