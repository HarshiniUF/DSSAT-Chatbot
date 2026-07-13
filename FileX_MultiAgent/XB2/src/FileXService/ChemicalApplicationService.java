package FileXService;

import Extensions.Utils;
import FileXModel.Chemical;
import FileXModel.ChemicalApplication;
import FileXModel.Comment;
import static FileXModel.FileX.chemicalList;
import static FileXModel.FileX.comments;
import FileXModel.Section;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.PrintWriter;

/**
 *
 * @author Jazzy
 */
public class ChemicalApplicationService {
    public static void Read(File fileName) {
        try {
            FileReader fReader = new FileReader(fileName);
            BufferedReader br = new BufferedReader(fReader);
            String strRead;

            String chemicalHeader = "";
            boolean bChemicalHeader = false;
            boolean bChemical = false;

            while ((strRead = br.readLine()) != null) {
                String tmp = strRead;

                if (tmp.trim().startsWith("*CHEMICAL APPLICATIONS")) {
                    bChemical = true;

                } else if (bChemical && !bChemicalHeader && tmp.trim().startsWith("@")) {
                    chemicalHeader = tmp.trim();
                    bChemicalHeader = true;
                } else if (bChemical && bChemicalHeader) {
                    if ("".equals(tmp.trim()) || tmp.trim().startsWith("*")) {
                        bChemical = false;
                        bChemicalHeader = false;
                        continue;
                    }
                    else if(strRead.trim().startsWith("!")){
                        int l = 1;
                        if(chemicalList.GetSize() > 0){
                            l = chemicalList.GetAtIndex(chemicalList.GetSize() - 1).GetLevel();
                        }
                        comments.addComment(l, Section.Chemical, strRead);
                        continue;
                    }
                    
                    //@C CDATE CHCOD CHAMT  CHME CHDEP   CHT..CHNAME
                    Chemical chem;
                    ChemicalApplication chemApp = new ChemicalApplication();
                    Integer level = Integer.valueOf(tmp.substring(0, 2).trim());

                    boolean isAdd = false;
                    if (!chemicalList.IsLevelExists(level)) {
                        chem = new Chemical();
                        chem.SetLevel(level);
                        isAdd = true;
                    } else {
                        chem = (Chemical)chemicalList.GetAt(level);
                    }
                    try {
                        chemApp.CDATE = Utils.GetDate(chemicalHeader, tmp, "CDATE", 5);
                    } catch (Exception ex) {
                        chemApp.CDAY = Utils.GetInteger(chemicalHeader, tmp, "CDATE", 5);
                    }
                    chemApp.CHCOD = Utils.GetString(chemicalHeader, tmp, "CHCOD", 5);
                    chemApp.CHAMT = Utils.GetFloat(chemicalHeader, tmp, "CHAMT", 5);
                    chemApp.CHME = Utils.GetString(chemicalHeader, tmp, " CHME", 5);
                    chemApp.CHDEP = Utils.GetInteger(chemicalHeader, tmp, "CHDEP", 5);
                    chemApp.CHT = Utils.GetString(chemicalHeader, tmp, "  CHT", 5);
                    chem.CHNAME = Utils.GetString(chemicalHeader, tmp, "CHNAME", tmp.length() - chemicalHeader.indexOf("CHNAME"));
                    chem.AddApp(chemApp);

                    if (isAdd) {
                        chemicalList.AddNew(chem);
                    }
                }
            }
        } catch (Exception ex) {
            System.out.println(ex.getMessage());
        }
    }

    public static void Extract(PrintWriter pw) {
        // <editor-fold defaultstate="collapsed" desc="Chemicals">
        if (chemicalList.GetSize() > 0) {
            pw.println();
            pw.println("*CHEMICAL APPLICATIONS");
            pw.println("@C CDATE CHCOD CHAMT  CHME CHDEP   CHT..CHNAME");
            for (int i = 0; i < chemicalList.GetSize(); i++) {
                Chemical chem = (Chemical)chemicalList.GetAtIndex(i);
                Integer level = chem.GetLevel();
                
                for (int n = 0; n < chem.GetSize(); n++) {
                    ChemicalApplication chemApp = chem.GetApp(n);
    
                    pw.print(Utils.PadLeft(level, 2, ' '));

                    try {
                        if(chemApp.CDATE != null)
                            pw.print(" " + Utils.PadRight(Utils.JulianDate(chemApp.CDATE), 5, ' '));
                        else
                            pw.print(" " + Utils.PadLeft(chemApp.CDAY, 5, ' '));
                    } catch (Exception e) {
                        pw.print(" " + Utils.PadLeft("-99", 5, ' '));
                    }

                    pw.print(" " + Utils.PadRight(chemApp.CHCOD, 5, ' '));
                    pw.print(" " + Utils.PadLeft(chemApp.CHAMT, 5, ' '));
                    pw.print(" " + Utils.PadRight(chemApp.CHME, 5, ' '));
                    pw.print(" " + Utils.PadLeft(chemApp.CHDEP, 5, ' '));
                    pw.print(" " + Utils.PadLeft(chemApp.CHT, 5, ' '));
                    if (chem.CHNAME != null) {
                        pw.print("  " + chem.CHNAME);
                    } else {
                        pw.print("  -99");
                    }
                    pw.println();
                }
                
                for (Comment comment : comments.getAll(level, Section.Chemical)) {
                    pw.println(comment.description);
                }
            }
        }
        // </editor-fold>
    }
}
