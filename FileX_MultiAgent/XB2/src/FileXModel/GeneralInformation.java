/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package FileXModel;

import DSSATModel.Crop;
import DSSATModel.ExperimentType;

/**
 *
 * @author Jazzy
 */
public class GeneralInformation extends ModelXBase {
    public GeneralInformation (){
        FileType = ExperimentType.Experimental;
    }
    
    public ExperimentType FileType;
    public String ExperimentName;
    public String InstituteCode;
    public String SiteCode;
    public String Year;
    public String ExperimentNumber;
    public Crop crop;
    public String People;
    public String Adress;
    public String Site;
    public String Notes;


    public Float PAREA;     /* Gross plot area per rep, m-2 */
    public Integer PRNO;        /* Rows per plot */
    public Float PLEN;      /* Plot length, m */
    public Integer PLDR;        /* Plots relative to drains, degrees */
    public Float PLSP;      /* Plot spacing, cm */
    public String PLAY;     /* Plot layout */
    public Float HAREA;     /* Harvest area, m-2 */
    public Integer HRNO;        /* Harvest row number */
    public Float HLEN;      /* Harvest row length, m */
    public String HARM;     /* Harvest method */

    @Override
    public String GetName() {
        return "";
    }

    @Override
    public void SetName(String name) {

    }
}
