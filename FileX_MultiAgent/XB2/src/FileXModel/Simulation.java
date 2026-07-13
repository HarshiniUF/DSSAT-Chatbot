/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package FileXModel;

import java.util.Date;

/**
 *
 * @author Jazzy
 */
public class Simulation extends ModelXBase implements Cloneable {
    public String SNAME;

    public Simulation(String SNAME)
    {
        this.SNAME = SNAME;
    }

    public Simulation()
    {
    }

    // <editor-fold defaultstate="collapsed" desc="GENERAL">
    public Integer NYERS;
    public Integer NREPS;
    public String START;
    public Date SDATE;
    public Float RSEED;
    //public String SNAME;
    public String SMODEL;
    // </editor-fold>

    // <editor-fold defaultstate="collapsed" desc="OPTIONS">
    public String WATER;
    public String NITRO;
    public String SYMBI;
    public String PHOSP;
    public String POTAS;
    public String DISES;
    public String CHEM;
    public String TILL;
    public String CO2;// </editor-fold>

    // <editor-fold defaultstate="collapsed" desc="METHODS">
    public String WTHER;
    public String INCON;
    public String LIGHT;
    public String EVAPO;
    public String INFIL;
    public String PHOTO;
    public String HYDRO;
    public String NSWIT;
    public String MESOM;
    public String MESEV;
    public String MESOL;
    // </editor-fold>

    // <editor-fold defaultstate="collapsed" desc="MANAGEMENT">
    public String PLANT;
    public String IRRIG;
    public String FERTI;
    public String RESID;
    public String HARVS;

    // <editor-fold defaultstate="collapsed" desc="PLANTING">
    public Date PFRST;
    public Date PLAST;
    public Integer PFRST_Day;
    public Integer PLAST_Day;
    public Float PH2OL;
    public Float PH2OU;
    public Float PH2OD;
    public Float PSTMX;
    public Float PSTMN;
    // </editor-fold>

    // <editor-fold defaultstate="collapsed" desc="IRRIGATION">
    public Float IMDEP;
    public Float ITHRL;
    public Float ITHRU;
    public String IROFF;
    public String IMETH;
    public Float IRAMT;
    public Float IREFF;
    // </editor-fold>

    // <editor-fold defaultstate="collapsed" desc="NITROGEN">
    public Float NMDEP;
    public Float NMTHR;
    public Float NAMNT;
    public String NCODE;
    public String NAOFF;
    // </editor-fold>

    // <editor-fold defaultstate="collapsed" desc="RESIDUES">
    public Float RIPCN = 100F;
    public Float RTIME = 1F;
    public Float RIDEP = 20F;
    // </editor-fold>

    // <editor-fold defaultstate="collapsed" desc="HARVEST">
    public Date HFRST;
    public Integer HFRST_Init;
    public Date HLAST;
    public Integer HLAST_Day;
    public Float HPCNP;
    public Float HPCNR;
    public Integer HMFRQ;
    public Integer HMGDD;
    public Float HMCUT;
    public Integer HMMOW;
    public Integer HRSPL;
    public Integer HMVS;
    // </editor-fold>

    // </editor-fold>

    // <editor-fold defaultstate="collapsed" desc="OUTPUTS">
    public String FNAME;    
    public String OVVEW;
    public String SUMRY;
    public Integer FROPT;
    public String GROUT;
    public String CAOUT;
    public String WAOUT;
    public String NIOUT;
    public String MIOUT;
    public String DIOUT;
    public String VBOSE;
    public String CHOUT;
    public String OPOUT;
    public String FMOPT;
    // </editor-fold>
    
    // <editor-fold defaultstate=collapsed" desc"FORECAST">
    public Date ENDAT;  //End of simulation date
    public Integer SDUR;    //Maximum duration of one season
    public Date FODAT;  //Forecast date
    public Integer FSTRYR;  //Ensenble start year
    public Integer FENDYR;  //Ensemblelast year 
    public String FWFILE;//: Forecast weather file
    public String FONAME;//: Yield forecast name
    // </editor-fold>
    
    @Override
    public Simulation clone() throws CloneNotSupportedException {
        Simulation sim = (Simulation)super.clone();    // return shallow copy
        sim.SNAME = this.SNAME;
        return sim;
    }

    @Override
    public String GetName() {
        return SNAME == null ? "" : SNAME;
    }

    @Override
    public void SetName(String name) {
        SNAME = name;
    }
}
