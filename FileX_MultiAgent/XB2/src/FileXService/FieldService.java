package FileXService;

import Extensions.Utils;
import FileXModel.Comment;
import FileXModel.FieldDetail;
import static FileXModel.FileX.comments;
import static FileXModel.FileX.fieldList;
import FileXModel.FileXCommentList;
import FileXModel.Section;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.PrintWriter;

/**
 *
 * @author Jazzy
 */
public class FieldService {
    public static void Read(File fileName) {
        try {
            FileReader fReader = new FileReader(fileName);
            BufferedReader br = new BufferedReader(fReader);
            String strRead = null;
            
            String fieldHeader1 = "";
            String fieldHeader2 = "";
            String fieldHeader3 = "";
            boolean bFieldHeader1 = false;
            boolean bFieldHeader2 = false;
            boolean bFieldHeader3 = false;
            boolean bField = false;
            
            while ((strRead = br.readLine()) != null) {
                String tmp = strRead;
                
                if (tmp.trim().startsWith("*FIELDS")) {
                    bField = true;
                } else if (bField && !bFieldHeader1 && !bFieldHeader2 && tmp.trim().startsWith("@")) {
                    fieldHeader1 = tmp.trim();
                    bFieldHeader1 = true;
                } else if (bField && bFieldHeader1 && !bFieldHeader2 && tmp.trim().startsWith("@")) {
                    fieldHeader2 = tmp.trim();
                    bFieldHeader2 = true;
                } else if(bField && bFieldHeader1 && bFieldHeader2 && tmp.trim().startsWith("@") && tmp.trim().endsWith("PMALB  BDWD  BDHT")){
                    fieldHeader3 = tmp.trim();
                    bFieldHeader3 = true;                    
                } else if (bField && bFieldHeader1 && !bFieldHeader2 && !bFieldHeader3) {
                    FieldDetail field = new FieldDetail();
                    
                    if ("".equals(tmp.trim())) {
                        bField = false;
                        bFieldHeader1 = false;
                        bFieldHeader2 = false;
                        continue;
                    }
                    else if(tmp.trim().startsWith("!")){
                        int l = 1;
                        if(fieldList.GetSize() > 0){
                            l = fieldList.GetAtIndex(fieldList.GetSize() - 1).GetLevel();
                        }
                        comments.addComment(l, Section.Field1, tmp);
                        continue;
                    }
                    
                    //@L ID_FIELD WSTA....  FLSA  FLOB  FLDT  FLDD  FLDS  FLST SLTX  SLDP  ID_SOIL    FLNAME
                    
                    Integer level = Integer.valueOf(tmp.substring(0, 2).trim());
                    field.SetLevel(level);
                    field.ID_FIELD = Utils.GetString(fieldHeader1, tmp, "ID_FIELD", 8);
                    field.WSTA = Utils.GetString(fieldHeader1, tmp, "WSTA", 8);
                    field.FLSA = Utils.GetFloat(fieldHeader1, tmp, "FLSA", 5);
                    field.FLOB = Utils.GetFloat(fieldHeader1, tmp, "FLOB", 5);
                    field.FLDT = Utils.GetString(fieldHeader1, tmp, " FLDT", 5);
                    field.FLDD = Utils.GetFloat(fieldHeader1, tmp, "FLDD", 5);
                    field.FLDS = Utils.GetFloat(fieldHeader1, tmp, "FLDS", 5);
                    field.FLST = Utils.GetString(fieldHeader1, tmp, " FLST", 5);
                    field.SLTX = Utils.GetString(fieldHeader1, tmp, "SLTX", 5);
                    field.SLDP = Utils.GetFloat(fieldHeader1, tmp, "SLDP", 5);
                    field.ID_SOIL = Utils.GetString(fieldHeader1, tmp, "ID_SOIL", 10);
                    field.FLNAME = Utils.GetString(fieldHeader1, tmp, "FLNAME", tmp.length() - fieldHeader1.indexOf("FLNAME"));

                    fieldList.AddNew(field);
                } else if (bField && bFieldHeader1 && bFieldHeader2 && !bFieldHeader3) {                    
                    if ("".equals(tmp.trim())) {
                        bField = false;
                        bFieldHeader1 = false;
                        bFieldHeader2 = false;
                        continue;
                    }
                    else if(tmp.trim().startsWith("!")){
                        int l = 1;
                        if(fieldList.GetSize() > 0){
                            l = fieldList.GetAtIndex(fieldList.GetSize() - 1).GetLevel();
                        }
                        comments.addComment(l, Section.Field2, tmp);
                    }
                    //@L ...........XCRD ...........YCRD .....ELEV .............AREA .SLEN .FLWR .SLAS FLHST FHDUR

                    try {
                        Integer level = Integer.valueOf(tmp.substring(0, 2).trim());
                        FieldDetail field = (FieldDetail)fieldList.GetAt(level);

                        field.XCRD = Utils.GetFloat(fieldHeader2, tmp, "XCRD", 15);
                        field.YCRD = Utils.GetFloat(fieldHeader2, tmp, "YCRD", 15);
                        field.ELEV = Utils.GetFloat(fieldHeader2, tmp, "ELEV", 9);
                        field.AREA = Utils.GetFloat(fieldHeader2, tmp, "AREA", 17);
                        field.SLEN = Utils.GetFloat(fieldHeader2, tmp, "SLEN", 5);
                        field.FLWR = Utils.GetFloat(fieldHeader2, tmp, "FLWR", 5);
                        field.SLAS = Utils.GetFloat(fieldHeader2, tmp, "SLAS", 5);
                        field.FLHST = Utils.GetString(fieldHeader2, tmp, "FLHST", 5);
                        field.FHDUR = Utils.GetFloat(fieldHeader2, tmp, "FHDUR", 5);
                    } catch (NumberFormatException numberFormatException) {
                    }
                } else if(bField && bFieldHeader1 && bFieldHeader2 && bFieldHeader3 ){                    
                    if ("".equals(tmp.trim())) {
                        bField = false;
                        bFieldHeader1 = false;
                        bFieldHeader2 = false;
                        bFieldHeader3 = false;
                        continue;
                    }
                    else if(tmp.trim().startsWith("!")){
                        int l = 1;
                        if(fieldList.GetSize() > 0){
                            l = fieldList.GetAtIndex(fieldList.GetSize() - 1).GetLevel();
                        }
                        comments.addComment(l, Section.Field2, tmp);
                    }
                    
                    try {
                        Integer level = Integer.valueOf(tmp.substring(0, 2).trim());
                        FieldDetail field = (FieldDetail)fieldList.GetAt(level);
                        
                        field.PMALB = Utils.GetFloat(fieldHeader3, tmp, "PMALB", 5);
                        field.BDWD = Utils.GetInteger(fieldHeader3, tmp, "BDWD", 5);
                        field.BDHT = Utils.GetInteger(fieldHeader3, tmp, "BDHT", 5);
                    }
                    catch (NumberFormatException numberFormatException) {
                    }
                }
            }
        } catch (Exception ex) {
            System.out.println(ex.getMessage());
        }
    }
    
    public static void Extract(PrintWriter pw){
        // <editor-fold defaultstate="collapsed" desc="Fields">
        if (fieldList.GetSize() > 0) {
            pw.println();
            pw.println("*FIELDS");
            pw.println("@L ID_FIELD WSTA....  FLSA  FLOB  FLDT  FLDD  FLDS  FLST SLTX  SLDP  ID_SOIL    FLNAME");
            for (int i = 0; i < fieldList.GetSize(); i++) {
                FieldDetail field = (FieldDetail)fieldList.GetAtIndex(i);
                Integer level = field.GetLevel();
                pw.print(Utils.PadLeft(level, 2, ' '));
                pw.print(" " + Utils.PadRight(field.ID_FIELD, 8, ' '));
                pw.print(" " + Utils.PadRight(field.WSTA, 8, ' '));
                pw.print(" " + Utils.PadLeft(field.FLSA, 5, ' '));
                pw.print(" " + Utils.PadLeft(field.FLOB, 5, ' '));
                pw.print(" " + Utils.PadLeft(field.FLDT, 5, ' '));
                pw.print(" " + Utils.PadLeft(field.FLDD, 5, ' '));
                pw.print(" " + Utils.PadLeft(field.FLDS, 5, ' '));
                pw.print(" " + Utils.PadLeft(field.FLST, 5, "0".equals(field.FLST) ? '0' : ' '));
                pw.print(" " + Utils.PadRight(field.SLTX, 5, ' '));
                pw.print(" " + Utils.PadLeft(field.SLDP, 4, ' '));
                pw.print("  " + Utils.PadRight(field.ID_SOIL, 10, ' '));
                if (field.FLNAME != null) {
                    pw.print(" " + field.FLNAME);
                } else {
                    pw.print(" -99");
                }
                
                pw.println();
                
                for (Comment comment : comments.getAll(i, Section.Field1)) {
                    pw.println(comment.description);
                }
            }


            pw.println("@L ...........XCRD ...........YCRD .....ELEV .............AREA .SLEN .FLWR .SLAS FLHST FHDUR");
            for (int i = 0; i < fieldList.GetSize(); i++) {
                Integer level = i + 1;
                FieldDetail field = (FieldDetail)fieldList.GetAtIndex(i);
                pw.print(Utils.PadLeft(level, 2, ' '));
                pw.print(" " + Utils.PadLeft(field.XCRD, 15, ' '));
                pw.print(" " + Utils.PadLeft(field.YCRD, 15, ' '));
                pw.print(" " + Utils.PadLeft(field.ELEV, 9, ' '));
                pw.print(" " + Utils.PadLeft(field.AREA, 17, ' '));
                pw.print(" " + Utils.PadLeft(field.SLEN, 5, ' '));
                pw.print(" " + Utils.PadLeft(field.FLWR, 5, ' '));
                pw.print(" " + Utils.PadLeft(field.SLAS, 5, ' '));
                pw.print(" " + Utils.PadLeft(field.FLHST, 5, ' '));
                pw.print(" " + Utils.PadLeft(field.FHDUR, 5, ' '));
                pw.println();
                
                for (Comment comment : comments.getAll(i, Section.Field2)) {
                    pw.println(comment.description);
                }
            }
            
            pw.println("@L PMALB  BDWD  BDHT");
            for (int i = 0; i < fieldList.GetSize(); i++) {
                Integer level = i + 1;
                FieldDetail field = (FieldDetail)fieldList.GetAtIndex(i);
                pw.print(Utils.PadLeft(level, 2, ' '));
                pw.print(" " + Utils.PadLeft(field.PMALB, 5, ' '));
                pw.print(" " + Utils.PadLeft(field.BDWD, 5, ' '));
                pw.print(" " + Utils.PadLeft(field.BDHT, 5, ' '));
                pw.println();
                
                for (Comment comment : comments.getAll(i, Section.Field3)) {
                    pw.println(comment.description);
                }
            }
        }
        // </editor-fold>
    }
}
