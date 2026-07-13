package FileXService;

import DSSATModel.ExperimentType;
import Extensions.Utils;
import FileXModel.Comment;
import FileXModel.FileX;
import static FileXModel.FileX.comments;
import FileXModel.Section;
import FileXModel.Simulation;
import FileXModel.SimulationList;
import java.io.BufferedReader;
import java.io.FileReader;
import java.io.PrintWriter;
/**
 *
 * @author Jazzy
 */
public class SimulationControlService {
    public static SimulationList Read(String fileName) {
        SimulationList simulationList = new SimulationList();
        
        try {
            FileReader fReader = new FileReader(fileName);
            BufferedReader br = new BufferedReader(fReader);
            String strRead = null;
            
            String simGeneralHeader = "";
            String simOptionHeader = "";
            String simMethodHeader = "";
            String simManagementHeader = "";
            String simOutputHeader = "";
            String simPlantingHeader = "";
            String simIrrigationHeader = "";
            String simNitrogenHeader = "";
            String simResidueHeader = "";
            String simHarvestHeader = "";
            String simForecastHeader = "";
            
            boolean bSimulation = false;
            int nSimulation = 0;
            
            while ((strRead = br.readLine()) != null) {
                String tmp = strRead;
                
                if (tmp.trim().startsWith("*SIMULATION CONTROLS")) {
                    bSimulation = true;
                } else if (bSimulation && tmp.trim().startsWith("@N GENERAL")) {
                    simGeneralHeader = tmp.trim();
                    nSimulation = 1;
                } else if (bSimulation && tmp.trim().startsWith("@N OPTIONS")) {
                    simOptionHeader = tmp.trim();
                    nSimulation = 2;
                } else if (bSimulation && tmp.trim().startsWith("@N METHODS")) {
                    simMethodHeader = tmp.trim();
                    nSimulation = 3;
                } else if (bSimulation && tmp.trim().startsWith("@N MANAGEMENT")) {
                    simManagementHeader = tmp.trim();
                    nSimulation = 4;
                } else if (bSimulation && tmp.trim().startsWith("@N OUTPUTS")) {
                    simOutputHeader = tmp.trim();
                    nSimulation = 5;
                } else if (bSimulation && tmp.trim().startsWith("@N PLANTING")) {
                    simPlantingHeader = tmp.trim();
                    nSimulation = 6;
                } else if (bSimulation && tmp.trim().startsWith("@N IRRIGATION")) {
                    simIrrigationHeader = tmp.trim();
                    nSimulation = 7;
                } else if (bSimulation && tmp.trim().startsWith("@N NITROGEN")) {
                    simNitrogenHeader = tmp.trim();
                    nSimulation = 8;
                } else if (bSimulation && tmp.trim().startsWith("@N RESIDUES")) {
                    simResidueHeader = tmp.trim();
                    nSimulation = 9;
                } else if (bSimulation && tmp.trim().startsWith("@N HARVEST")) {
                    simHarvestHeader = tmp.trim();
                    nSimulation = 10;
                } else if (bSimulation && tmp.trim().startsWith("@N SIMDATES")) {
                    simForecastHeader = tmp.trim();
                    nSimulation = 11;
                }

                else if (bSimulation && nSimulation == 1 && !"".equals(tmp.trim()) && !tmp.trim().startsWith("@  AUTOMATIC MANAGEMENT")) {
                    if(strRead.trim().startsWith("!")){
                        int l = 1;
                        if(simulationList.GetSize() > 0){
                            l = simulationList.GetAtIndex(simulationList.GetSize() - 1).GetLevel();
                        }
                        comments.addComment(l, Section.Simulation1, strRead);
                        continue;
                    }
                    
                    Simulation sim;
                    Integer level = Integer.valueOf(tmp.substring(0, 2).trim());

                    //NYERS NREPS START SDATE RSEED SNAME.................... SMODEL
                    boolean isAdd = false;
                    if(!simulationList.IsLevelExists(level)) {
                        sim = new Simulation();
                        sim.SetLevel(level);
                        isAdd = true;
                    } else {
                        sim = (Simulation)simulationList.GetAt(level);
                    }

                    tmp = Utils.PadRight(tmp, Math.max(simGeneralHeader.length(), tmp.length()), ' ');

                    sim.NYERS = Utils.GetInteger(simGeneralHeader, tmp, "NYERS", 5);
                    sim.NREPS = Utils.GetInteger(simGeneralHeader, tmp, "NREPS", 5);
                    sim.START = Utils.GetString(simGeneralHeader, tmp, "START", 5);
                    sim.SDATE = Utils.GetDate(simGeneralHeader, tmp, "SDATE", 5);
                    sim.RSEED = Utils.GetFloat(simGeneralHeader, tmp, "RSEED", 5);
                    sim.SNAME = Utils.GetString(simGeneralHeader, tmp, "SNAME", simGeneralHeader.contains("SMODEL") ? 25 : 99);
                    
                    if(simGeneralHeader.contains("SMODEL"))
                        sim.SMODEL = Utils.GetString(simGeneralHeader, tmp, "SMODEL", 5);

                    if(isAdd) {
                        simulationList.AddNew(sim);
                    }
                    nSimulation = -1;
                }
                else if (bSimulation && nSimulation == 2 && !"".equals(tmp.trim()) && !tmp.trim().startsWith("@  AUTOMATIC MANAGEMENT")) {
                    if(strRead.trim().startsWith("!")){
                        int l = 1;
                        if(simulationList.GetSize() > 0){
                            l = simulationList.GetAtIndex(simulationList.GetSize() - 1).GetLevel();
                        }
                        comments.addComment(l, Section.Simulation2, strRead);
                        continue;
                    }
                    
                    Simulation sim;
                    Integer level = Integer.valueOf(tmp.substring(0, 2).trim());

                    //WATER NITRO SYMBI PHOSP POTAS DISES  CHEM  TILL   CO2
                    boolean isAdd = false;
                    if(!simulationList.IsLevelExists(level)) {
                        sim = new Simulation();
                    } else {
                        sim = (Simulation)simulationList.GetAt(level);
                    }

                    sim.WATER = Utils.GetString(simOptionHeader, tmp, "WATER", 5);
                    sim.NITRO = Utils.GetString(simOptionHeader, tmp, "NITRO", 5);
                    sim.SYMBI = Utils.GetString(simOptionHeader, tmp, "SYMBI", 5);
                    sim.PHOSP = Utils.GetString(simOptionHeader, tmp, "PHOSP", 5);
                    sim.POTAS = Utils.GetString(simOptionHeader, tmp, "POTAS", 5);
                    sim.DISES = Utils.GetString(simOptionHeader, tmp, "DISES", 5);
                    sim.CHEM = Utils.GetString(simOptionHeader, tmp, " CHEM", 5);
                    sim.TILL = Utils.GetString(simOptionHeader, tmp, " TILL", 5);
                    sim.CO2 = Utils.GetString(simOptionHeader, tmp, "  CO2", 5);

                    if(isAdd) {
                        simulationList.AddNew(sim);
                    }
                    nSimulation = -1;
                }
                else if (bSimulation && nSimulation == 3 && !"".equals(tmp.trim()) && !tmp.trim().startsWith("@  AUTOMATIC MANAGEMENT")) {
                    if(strRead.trim().startsWith("!")){
                        int l = 1;
                        if(simulationList.GetSize() > 0){
                            l = simulationList.GetAtIndex(simulationList.GetSize() - 1).GetLevel();
                        }
                        comments.addComment(l, Section.Simulation3, strRead);
                        continue;
                    }
                    
                    Simulation sim;
                    Integer level = Integer.valueOf(tmp.substring(0, 2).trim());

                    //WTHER INCON LIGHT EVAPO INFIL PHOTO HYDRO NSWIT MESOM MESEV MESOL
                    boolean isAdd = false;
                    if(!simulationList.IsLevelExists(level)) {
                        sim = new Simulation();
                        sim.SetLevel(level);
                        isAdd = true;
                    } else {
                        sim = (Simulation)simulationList.GetAt(level);
                    }

                    sim.WTHER = Utils.GetString(simMethodHeader, tmp, "WTHER", 5);
                    sim.INCON = Utils.GetString(simMethodHeader, tmp, "INCON", 5);
                    sim.LIGHT = Utils.GetString(simMethodHeader, tmp, "LIGHT", 5);
                    sim.EVAPO = Utils.GetString(simMethodHeader, tmp, "EVAPO", 5);
                    sim.INFIL = Utils.GetString(simMethodHeader, tmp, "INFIL", 5);
                    sim.PHOTO = Utils.GetString(simMethodHeader, tmp, "PHOTO", 5);
                    sim.HYDRO = Utils.GetString(simMethodHeader, tmp, "HYDRO", 5);
                    sim.NSWIT = Utils.GetString(simMethodHeader, tmp, "NSWIT", 5);
                    sim.MESOM = Utils.GetString(simMethodHeader, tmp, "MESOM", 5);
                    sim.MESEV = Utils.GetString(simMethodHeader, tmp, "MESEV", 5);
                    sim.MESOL = Utils.GetString(simMethodHeader, tmp, "MESOL", 5);

                    if(isAdd) {
                        simulationList.AddNew(sim);
                    }
                    nSimulation = -1;
                }
                else if (bSimulation && nSimulation == 4 && !"".equals(tmp.trim()) && !tmp.trim().startsWith("@  AUTOMATIC MANAGEMENT")) {
                    if(strRead.trim().startsWith("!")){
                        int l = 1;
                        if(simulationList.GetSize() > 0){
                            l = simulationList.GetAtIndex(simulationList.GetSize() - 1).GetLevel();
                        }
                        comments.addComment(l, Section.Simulation4, strRead);
                        continue;
                    }
                    
                    Simulation sim;
                    Integer level = Integer.valueOf(tmp.substring(0, 2).trim());

                    //PLANT IRRIG FERTI RESID HARVS
                    boolean isAdd = false;
                    if(!simulationList.IsLevelExists(level)) {
                        sim = new Simulation();
                        sim.SetLevel(level);
                        isAdd = true;
                    } else {
                        sim = (Simulation)simulationList.GetAt(level);
                    }

                    sim.PLANT = Utils.GetString(simManagementHeader, tmp, "PLANT", 5);
                    sim.IRRIG = Utils.GetString(simManagementHeader, tmp, "IRRIG", 5);
                    sim.FERTI = Utils.GetString(simManagementHeader, tmp, "FERTI", 5);
                    sim.RESID = Utils.GetString(simManagementHeader, tmp, "RESID", 5);
                    sim.HARVS = Utils.GetString(simManagementHeader, tmp, "HARVS", 5);

                    if(isAdd) {
                        simulationList.AddNew(sim);
                    }
                    nSimulation = -1;
                }
                else if (bSimulation && nSimulation == 5 && !"".equals(tmp.trim()) && !tmp.trim().startsWith("@  AUTOMATIC MANAGEMENT")) {
                    if(strRead.trim().startsWith("!")){
                        int l = 1;
                        if(simulationList.GetSize() > 0){
                            l = simulationList.GetAtIndex(simulationList.GetSize() - 1).GetLevel();
                        }
                        comments.addComment(l, Section.Simulation5, strRead);
                        continue;
                    }
                    
                    Simulation sim;
                    Integer level = Integer.valueOf(tmp.substring(0, 2).trim());

                    //FNAME OVVEW SUMRY FROPT GROUT CAOUT WAOUT NIOUT MIOUT DIOUT VBOSE CHOUT OPOUT
                    boolean isAdd = false;
                    if(!simulationList.IsLevelExists(level)) {
                        sim = new Simulation();
                        sim.SetLevel(level);
                        isAdd = true;
                    } else {
                        sim = (Simulation)simulationList.GetAt(level);
                    }

                    sim.FNAME = Utils.GetString(simOutputHeader, tmp, "FNAME", 5);
                    sim.OVVEW = Utils.GetString(simOutputHeader, tmp, "OVVEW", 5);
                    sim.SUMRY = Utils.GetString(simOutputHeader, tmp, "SUMRY", 5);
                    sim.FROPT = Utils.GetInteger(simOutputHeader, tmp, "FROPT", 5);
                    sim.GROUT = Utils.GetString(simOutputHeader, tmp, "GROUT", 5);
                    sim.CAOUT = Utils.GetString(simOutputHeader, tmp, "CAOUT", 5);
                    sim.WAOUT = Utils.GetString(simOutputHeader, tmp, "WAOUT", 5);
                    sim.NIOUT = Utils.GetString(simOutputHeader, tmp, "NIOUT", 5);
                    sim.MIOUT = Utils.GetString(simOutputHeader, tmp, "MIOUT", 5);
                    sim.DIOUT = Utils.GetString(simOutputHeader, tmp, "DIOUT", 5);
                    sim.VBOSE = Utils.GetString(simOutputHeader, tmp, "VBOSE", 5);
                    sim.CHOUT = Utils.GetString(simOutputHeader, tmp, "CHOUT", 5);
                    sim.OPOUT = Utils.GetString(simOutputHeader, tmp, "OPOUT", 5);
                    sim.FMOPT = Utils.GetString(simOutputHeader, tmp, "FMOPT", 5);

                    if("".equals(sim.FMOPT) || sim.FMOPT == null)
                        sim.FMOPT = "A";

                    if(isAdd) {
                        simulationList.AddNew(sim);
                    }
                    nSimulation = -1;
                }
                else if (bSimulation && nSimulation == 6 && !"".equals(tmp.trim()) && !tmp.trim().startsWith("@  AUTOMATIC MANAGEMENT")) {
                    if(strRead.trim().startsWith("!")){
                        int l = 1;
                        if(simulationList.GetSize() > 0){
                            l = simulationList.GetAtIndex(simulationList.GetSize() - 1).GetLevel();
                        }
                        comments.addComment(l, Section.Simulation6, strRead);
                        continue;
                    }
                    
                    Simulation sim;
                    Integer level = Integer.valueOf(tmp.substring(0, 2).trim());

                    //PFRST PLAST PH2OL PH2OU PH2OD PSTMX PSTMN
                    boolean isAdd = false;
                    if(!simulationList.IsLevelExists(level)) {
                        sim = new Simulation();
                        sim.SetLevel(level);
                        isAdd = true;
                    } else {
                        sim = (Simulation)simulationList.GetAt(level);
                    }

                    try{
                        sim.PFRST = Utils.GetDate(simPlantingHeader, tmp, "PFRST", 5);
                    }
                    catch(Exception ex) {
                        sim.PFRST_Day = Utils.GetInteger(simPlantingHeader, tmp, "PFRST", 2);
                    }
                    try{
                        sim.PLAST = Utils.GetDate(simPlantingHeader, tmp, "PLAST", 5);
                    }
                    catch(Exception ex) {
                        sim.PLAST_Day = Utils.GetInteger(simPlantingHeader, tmp, "PLAST", 2);
                    }
                    sim.PH2OL = Utils.GetFloat(simPlantingHeader, tmp, "PH2OL", 5);
                    sim.PH2OU = Utils.GetFloat(simPlantingHeader, tmp, "PH2OU", 5);
                    sim.PH2OD = Utils.GetFloat(simPlantingHeader, tmp, "PH2OD", 5);
                    sim.PSTMX = Utils.GetFloat(simPlantingHeader, tmp, "PSTMX", 5);
                    sim.PSTMN = Utils.GetFloat(simPlantingHeader, tmp, "PSTMN", 5);

                    if(isAdd) {
                        simulationList.AddNew(sim);
                    }
                    nSimulation = -1;
                }
                else if (bSimulation && nSimulation == 7 && !"".equals(tmp.trim()) && !tmp.trim().startsWith("@  AUTOMATIC MANAGEMENT")) {
                    if(strRead.trim().startsWith("!")){
                        int l = 1;
                        if(simulationList.GetSize() > 0){
                            l = simulationList.GetAtIndex(simulationList.GetSize() - 1).GetLevel();
                        }
                        comments.addComment(l, Section.Simulation7, strRead);
                        continue;
                    }
                    
                    Simulation sim;
                    Integer level = Integer.valueOf(tmp.substring(0, 2).trim());

                    //IMDEP ITHRL ITHRU IROFF IMETH IRAMT IREFF
                    boolean isAdd = false;
                    if(!simulationList.IsLevelExists(level)) {
                        sim = new Simulation();
                        sim.SetLevel(level);
                        isAdd = true;
                    } else {
                        sim = (Simulation)simulationList.GetAt(level);
                    }

                    sim.IMDEP = Utils.GetFloat(simIrrigationHeader, tmp, "IMDEP", 5);
                    sim.ITHRL = Utils.GetFloat(simIrrigationHeader, tmp, "ITHRL", 5);
                    sim.ITHRU = Utils.GetFloat(simIrrigationHeader, tmp, "ITHRU", 5);
                    sim.IROFF = Utils.GetString(simIrrigationHeader, tmp, "IROFF", 5);
                    sim.IMETH = Utils.GetString(simIrrigationHeader, tmp, "IMETH", 5);
                    sim.IRAMT = Utils.GetFloat(simIrrigationHeader, tmp, "IRAMT", 5);
                    sim.IREFF = Utils.GetFloat(simIrrigationHeader, tmp, "IREFF", 5);

                    if(isAdd) {
                        simulationList.AddNew(sim);
                    }
                    nSimulation = -1;
                }
                else if (bSimulation && nSimulation == 8 && !"".equals(tmp.trim()) && !tmp.trim().startsWith("@  AUTOMATIC MANAGEMENT")) {
                    if(strRead.trim().startsWith("!")){
                        int l = 1;
                        if(simulationList.GetSize() > 0){
                            l = simulationList.GetAtIndex(simulationList.GetSize() - 1).GetLevel();
                        }
                        comments.addComment(l, Section.Simulation8, strRead);
                        continue;
                    }
                    
                    Simulation sim;
                    Integer level = Integer.valueOf(tmp.substring(0, 2).trim());

                    //NMDEP NMTHR NAMNT NCODE NAOFF
                    boolean isAdd = false;
                    if(!simulationList.IsLevelExists(level)) {
                        sim = new Simulation();
                        sim.SetLevel(level);
                        isAdd = true;
                    } else {
                        sim = (Simulation)simulationList.GetAt(level);
                    }

                    sim.NMDEP = Utils.GetFloat(simNitrogenHeader, tmp, "NMDEP", 5);
                    sim.NMTHR = Utils.GetFloat(simNitrogenHeader, tmp, "NMTHR", 5);
                    sim.NAMNT = Utils.GetFloat(simNitrogenHeader, tmp, "NAMNT", 5);
                    sim.NCODE = Utils.GetString(simNitrogenHeader, tmp, "NCODE", 5);
                    sim.NAOFF = Utils.GetString(simNitrogenHeader, tmp, "NAOFF", 5);

                    if(isAdd) {
                        simulationList.AddNew(sim);
                    }
                }
                else if (bSimulation && nSimulation == 9 && !"".equals(tmp.trim()) && !tmp.trim().startsWith("@  AUTOMATIC MANAGEMENT")) {
                    if(strRead.trim().startsWith("!")){
                        int l = 1;
                        if(simulationList.GetSize() > 0){
                            l = simulationList.GetAtIndex(simulationList.GetSize() - 1).GetLevel();
                        }
                        comments.addComment(l, Section.Simulation9, strRead);
                        continue;
                    }
                    
                    Simulation sim;
                    Integer level = Integer.valueOf(tmp.substring(0, 2).trim());

                    // RIPCN RTIME RIDEP
                    boolean isAdd = false;
                    if(!simulationList.IsLevelExists(level)) {
                        sim = new Simulation();
                        sim.SetLevel(level);
                        isAdd = true;
                    } else {
                        sim = (Simulation)simulationList.GetAt(level);
                    }

                    sim.RIPCN = Utils.GetFloat(simResidueHeader, tmp, "RIPCN", 5);
                    sim.RTIME = Utils.GetFloat(simResidueHeader, tmp, "RTIME", 5);
                    sim.RIDEP = Utils.GetFloat(simResidueHeader, tmp, "RIDEP", 5);

                    if(isAdd) {
                        simulationList.AddNew(sim);
                    }
                    nSimulation = -1;
                }
                else if (bSimulation && nSimulation == 10 && !"".equals(tmp.trim()) && !tmp.trim().startsWith("@  AUTOMATIC MANAGEMENT")) {
                    if(strRead.trim().startsWith("!")){
                        int l = 1;
                        if(simulationList.GetSize() > 0){
                            l = simulationList.GetAtIndex(simulationList.GetSize() - 1).GetLevel();
                        }
                        comments.addComment(l, Section.Simulation10, strRead);
                        continue;
                    }
                    
                    Simulation sim;
                    Integer level = Integer.valueOf(tmp.substring(0, 2).trim());

                    //HFRST HLAST HPCNP HPCNR
                    boolean isAdd = false;
                    if(!simulationList.IsLevelExists(level)) {
                        sim = new Simulation();
                        sim.SetLevel(level);
                        isAdd = true;
                    } else {
                        sim = (Simulation)simulationList.GetAt(level);
                    }

                    try{
                        sim.HFRST = Utils.GetDate(simHarvestHeader, tmp, "HFRST", 5);
                    }
                    catch(Exception ex){
                        sim.HFRST_Init = Utils.GetInteger(simHarvestHeader, tmp, "HFRST", 5);
//                        if(sim.HFRST == null && sim.HFRST_Init != null){
//                            LocalDate localDate = LocalDate.of(1900, 1, 1);
//                            sim.HFRST = Date.from(localDate.atStartOfDay(ZoneId.systemDefault()).toInstant());
//                        }
                    }
                    try{
                        sim.HLAST = Utils.GetDate(simHarvestHeader, tmp, "HLAST", 5);
                    }
                    catch(Exception ex) {
                        sim.HLAST_Day = Utils.GetInteger(simHarvestHeader, tmp, "HLAST", 5);
                    }
                    sim.HPCNP = Utils.GetFloat(simHarvestHeader, tmp, "HPCNP", 5);
                    sim.HPCNR = Utils.GetFloat(simHarvestHeader, tmp, "HPCNR", 5);
                    sim.HMFRQ = Utils.GetInteger(simHarvestHeader, tmp, "HMFRQ", 5);
                    sim.HMGDD = Utils.GetInteger(simHarvestHeader, tmp, "HMGDD", 5);
                    sim.HMCUT = Utils.GetFloat(simHarvestHeader, tmp, "HMCUT", 5);
                    sim.HMMOW = Utils.GetInteger(simHarvestHeader, tmp, "HMMOW", 5);
                    sim.HRSPL = Utils.GetInteger(simHarvestHeader, tmp, "HRSPL", 5);
                    sim.HMVS = Utils.GetInteger(simHarvestHeader, tmp, "HMVS", 5);

                    if(isAdd) {
                        simulationList.AddNew(sim);
                    }
                    nSimulation = -1;
                }
                else if (bSimulation && nSimulation == 11 && !"".equals(tmp.trim()) && !tmp.trim().startsWith("@  AUTOMATIC MANAGEMENT")) {
                    if(strRead.trim().startsWith("!")){
                        int l = 1;
                        if(simulationList.GetSize() > 0){
                            l = simulationList.GetAtIndex(simulationList.GetSize() - 1).GetLevel();
                        }
                        comments.addComment(l, Section.Simulation11, strRead);
                        continue;
                    }
                    
                    Simulation sim;
                    Integer level = Integer.valueOf(tmp.substring(0, 2).trim());

                    //@N SIMDATES    ENDAT    SDUR   FODAT  FSTRYR  FENDYR FWFILE           FONAME
                    boolean isAdd = false;
                    if(!simulationList.IsLevelExists(level)) {
                        sim = new Simulation();
                        sim.SetLevel(level);
                        isAdd = true;
                    } else {
                        sim = (Simulation)simulationList.GetAt(level);
                    }
                    
                    sim.ENDAT = Utils.GetDate(simForecastHeader, tmp, "ENDAT", 8);
                    sim.SDUR = Utils.GetInteger(simForecastHeader, tmp, "   SDUR", 7);
                    sim.FODAT = Utils.GetDate(simForecastHeader, tmp, "FODAT", 7);
                    sim.FSTRYR = Utils.GetInteger(simForecastHeader, tmp, "FSTRYR", 7);
                    sim.FENDYR = Utils.GetInteger(simForecastHeader, tmp, "FENDYR", 7);
                    sim.FWFILE = Utils.GetString(simForecastHeader, tmp, "FWFILE", 16);
                    sim.FONAME = Utils.GetString(simForecastHeader, tmp, "FONAME", tmp.length() - simForecastHeader.indexOf("FONAME"));

                    if(isAdd) {
                        simulationList.AddNew(sim);
                    }
                    nSimulation = -1;
                }
            }
        } catch (Exception ex) {
            System.out.println(ex.getMessage());
        }
        
        return simulationList;
    }
    
    public static void Extract(PrintWriter pw) {
        // <editor-fold defaultstate="collapsed" desc="Simulation Options">
        if (FileX.simulationList.GetSize() > 0) {
            pw.println();
            pw.println("*SIMULATION CONTROLS");
            for (int i = 0; i < FileX.simulationList.GetSize(); i++) {
                Simulation sim = (Simulation)FileX.simulationList.GetAtIndex(i);
                Integer level = sim.GetLevel();

                pw.println("@N GENERAL     NYERS NREPS START SDATE RSEED SNAME.................... SMODEL");
                pw.print(Utils.PadLeft(level, 2, ' '));
                pw.print(" GE         ");
                pw.print(" " + Utils.PadLeft(sim.NYERS, 5, ' '));
                pw.print(" " + Utils.PadLeft(sim.NREPS, 5, ' '));
                pw.print(" " + Utils.PadLeft(sim.START, 5, ' '));
                pw.print(" " + Utils.PadRight(Utils.JulianDate(sim.SDATE), 5, ' '));
                pw.print(" " + Utils.PadLeft(sim.RSEED, 5, ' '));
                pw.print(" " + Utils.PadRight(sim.SNAME, 25, ' '));
                if (sim.SMODEL != null) {
                    pw.print(" " + sim.SMODEL);
                } else {
                    pw.print(" -99");
                }
                pw.println();
                
                for (Comment comment : comments.getAll(level, Section.Simulation1)) {
                    pw.println(comment.description);
                }

                pw.println("@N OPTIONS     WATER NITRO SYMBI PHOSP POTAS DISES  CHEM  TILL   CO2");
                pw.print(Utils.PadLeft(level, 2, ' '));
                pw.print(" OP         ");
                pw.print(" " + Utils.PadLeft(sim.WATER, 5, ' '));
                pw.print(" " + Utils.PadLeft(sim.NITRO, 5, ' '));
                pw.print(" " + Utils.PadLeft(sim.SYMBI, 5, ' '));
                pw.print(" " + Utils.PadLeft(sim.PHOSP, 5, ' '));
                pw.print(" " + Utils.PadLeft(sim.POTAS, 5, ' '));
                pw.print(" " + Utils.PadLeft(sim.DISES, 5, ' '));
                pw.print(" " + Utils.PadLeft(sim.CHEM, 5, ' '));
                pw.print(" " + Utils.PadLeft(sim.TILL, 5, ' '));
                pw.print(" " + Utils.PadLeft(sim.CO2, 5, ' '));
                pw.println();
                for (Comment comment : comments.getAll(level, Section.Simulation2)) {
                    pw.println(comment.description);
                }

                pw.println("@N METHODS     WTHER INCON LIGHT EVAPO INFIL PHOTO HYDRO NSWIT MESOM MESEV MESOL");
                pw.print(Utils.PadLeft(level, 2, ' '));
                pw.print(" ME         ");
                pw.print(" " + Utils.PadLeft(sim.WTHER, 5, ' '));
                pw.print(" " + Utils.PadLeft(sim.INCON, 5, ' '));
                pw.print(" " + Utils.PadLeft(sim.LIGHT, 5, ' '));
                pw.print(" " + Utils.PadLeft(sim.EVAPO, 5, ' '));
                pw.print(" " + Utils.PadLeft(sim.INFIL, 5, ' '));
                pw.print(" " + Utils.PadLeft(sim.PHOTO, 5, ' '));
                pw.print(" " + Utils.PadLeft(sim.HYDRO, 5, ' '));
                pw.print(" " + Utils.PadLeft(sim.NSWIT, 5, ' '));
                pw.print(" " + Utils.PadLeft(sim.MESOM, 5, ' '));
                pw.print(" " + Utils.PadLeft(sim.MESEV, 5, ' '));
                pw.print(" " + Utils.PadLeft(sim.MESOL, 5, ' '));
                pw.println();
                for (Comment comment : comments.getAll(level, Section.Simulation3)) {
                    pw.println(comment.description);
                }

                pw.println("@N MANAGEMENT  PLANT IRRIG FERTI RESID HARVS");
                pw.print(Utils.PadLeft(level, 2, ' '));
                pw.print(" MA         ");
                pw.print(" " + Utils.PadLeft(sim.PLANT, 5, ' '));
                pw.print(" " + Utils.PadLeft(sim.IRRIG, 5, ' '));
                pw.print(" " + Utils.PadLeft(sim.FERTI, 5, ' '));
                pw.print(" " + Utils.PadLeft(sim.RESID, 5, ' '));
                pw.print(" " + Utils.PadLeft(sim.HARVS, 5, ' '));
                pw.println();
                for (Comment comment : comments.getAll(level, Section.Simulation4)) {
                    pw.println(comment.description);
                }

                pw.println("@N OUTPUTS     FNAME OVVEW SUMRY FROPT GROUT CAOUT WAOUT NIOUT MIOUT DIOUT VBOSE CHOUT OPOUT FMOPT");
                pw.print(Utils.PadLeft(level, 2, ' '));
                pw.print(" OU         ");
                pw.print(" " + Utils.PadLeft(sim.FNAME, 5, ' '));
                pw.print(" " + Utils.PadLeft(sim.OVVEW, 5, ' '));
                pw.print(" " + Utils.PadLeft(sim.SUMRY, 5, ' '));
                pw.print(" " + Utils.PadLeft(sim.FROPT, 5, ' '));
                pw.print(" " + Utils.PadLeft(sim.GROUT, 5, ' '));
                pw.print(" " + Utils.PadLeft(sim.CAOUT, 5, ' '));
                pw.print(" " + Utils.PadLeft(sim.WAOUT, 5, ' '));
                pw.print(" " + Utils.PadLeft(sim.NIOUT, 5, ' '));
                pw.print(" " + Utils.PadLeft(sim.MIOUT, 5, ' '));
                pw.print(" " + Utils.PadLeft(sim.DIOUT, 5, ' '));
                pw.print(" " + Utils.PadLeft(sim.VBOSE, 5, ' '));
                pw.print(" " + Utils.PadLeft(sim.CHOUT, 5, ' '));
                pw.print(" " + Utils.PadLeft(sim.OPOUT, 5, ' '));
                pw.print(" " + Utils.PadLeft(sim.FMOPT, 5, ' '));
                pw.println();
                for (Comment comment : comments.getAll(level, Section.Simulation5)) {
                    pw.println(comment.description);
                }

                pw.println();
                pw.println("@  AUTOMATIC MANAGEMENT");

                pw.println("@N PLANTING    PFRST PLAST PH2OL PH2OU PH2OD PSTMX PSTMN");
                pw.print(Utils.PadLeft(level, 2, ' '));
                pw.print(" PL         ");
                if(sim.PFRST != null)
                    pw.print(" " + Utils.PadRight(Utils.JulianDate(sim.PFRST), 5, ' '));
                else
                    pw.print(" " + Utils.PadLeft(sim.PFRST_Day, 5, ' '));
                if(sim.PLAST != null)
                    pw.print(" " + Utils.PadRight(Utils.JulianDate(sim.PLAST), 5, ' '));
                else
                    pw.print(" " + Utils.PadLeft(sim.PLAST_Day, 5, ' '));
                pw.print(" " + Utils.PadLeft(sim.PH2OL, 5, ' '));
                pw.print(" " + Utils.PadLeft(sim.PH2OU, 5, ' '));
                pw.print(" " + Utils.PadLeft(sim.PH2OD, 5, ' '));
                pw.print(" " + Utils.PadLeft(sim.PSTMX, 5, ' '));
                pw.print(" " + Utils.PadLeft(sim.PSTMN, 5, ' '));
                pw.println();
                for (Comment comment : comments.getAll(level, Section.Simulation6)) {
                    pw.println(comment.description);
                }

                pw.println("@N IRRIGATION  IMDEP ITHRL ITHRU IROFF IMETH IRAMT IREFF");
                pw.print(Utils.PadLeft(level, 2, ' '));
                pw.print(" IR         ");
                pw.print(" " + Utils.PadLeft(sim.IMDEP, 5, ' '));
                pw.print(" " + Utils.PadLeft(sim.ITHRL, 5, ' '));
                pw.print(" " + Utils.PadLeft(sim.ITHRU, 5, ' '));
                pw.print(" " + Utils.PadRight(sim.IROFF, 5, ' '));
                pw.print(" " + Utils.PadRight(sim.IMETH, 5, ' '));
                pw.print(" " + Utils.PadLeft(sim.IRAMT, 5, ' '));
                pw.print(" " + Utils.PadLeft(sim.IREFF, 5, ' '));
                pw.println();
                for (Comment comment : comments.getAll(level, Section.Simulation7)) {
                    pw.println(comment.description);
                }

                pw.println("@N NITROGEN    NMDEP NMTHR NAMNT NCODE NAOFF");
                pw.print(Utils.PadLeft(level, 2, ' '));
                pw.print(" NI         ");
                pw.print(" " + Utils.PadLeft(sim.NMDEP, 5, ' '));
                pw.print(" " + Utils.PadLeft(sim.NMTHR, 5, ' '));
                pw.print(" " + Utils.PadLeft(sim.NAMNT, 5, ' '));
                pw.print(" " + Utils.PadRight(sim.NCODE, 5, ' '));
                pw.print(" " + Utils.PadRight(sim.NAOFF, 5, ' '));
                pw.println();
                for (Comment comment : comments.getAll(level, Section.Simulation8)) {
                    pw.println(comment.description);
                }

                pw.println("@N RESIDUES    RIPCN RTIME RIDEP");
                pw.print(Utils.PadLeft(level, 2, ' '));
                pw.print(" RE         ");
                pw.print(" " + Utils.PadLeft(sim.RIPCN, 5, ' '));
                pw.print(" " + Utils.PadLeft(sim.RTIME, 5, ' '));
                pw.print(" " + Utils.PadLeft(sim.RIDEP, 5, ' '));
                pw.println();
                for (Comment comment : comments.getAll(level, Section.Simulation9)) {
                    pw.println(comment.description);
                }

                pw.println("@N HARVEST     HFRST HLAST HPCNP HPCNR HMFRQ HMGDD HMCUT HMMOW HRSPL HMVS");
                pw.print(Utils.PadLeft(level, 2, ' '));
                pw.print(" HA         ");
                pw.print(" " + Utils.PadLeft(sim.HFRST_Init == null ? Utils.JulianDate(sim.HFRST) : sim.HFRST_Init.toString(), 5, ' '));
                pw.print(" " + Utils.PadLeft(Utils.JulianDate(sim.HLAST), 5, ' '));
                pw.print(" " + Utils.PadLeft(sim.HPCNP, 5, ' '));
                pw.print(" " + Utils.PadLeft(sim.HPCNR, 5, ' '));
                pw.print(" " + Utils.PadLeft(sim.HMFRQ, 5, ' '));
                pw.print(" " + Utils.PadLeft(sim.HMGDD, 5, ' '));
                pw.print(" " + Utils.PadLeft(sim.HMCUT, 5, ' '));
                pw.print(" " + Utils.PadLeft(sim.HMMOW, 5, ' '));
                pw.print(" " + Utils.PadLeft(sim.HRSPL, 5, ' '));
                pw.print(" " + Utils.PadLeft(sim.HMVS, 4, ' '));
                pw.println();
                for (Comment comment : comments.getAll(level, Section.Simulation10)) {
                    pw.println(comment.description);
                }
                
                if(FileX.general.FileType == ExperimentType.Forecast){
                    pw.println("@N SIMDATES    ENDAT    SDUR   FODAT  FSTRYR  FENDYR FWFILE           FONAME");
                    pw.print(Utils.PadLeft(level, 2, ' '));
                    pw.print(" SI       ");
                    pw.print(" " + Utils.PadLeft(Utils.JulianDate(sim.ENDAT, "yyyy"), 7, ' '));
                    pw.print(" " + Utils.PadLeft(sim.SDUR, 7, ' '));
                    pw.print(" " + Utils.PadLeft(Utils.JulianDate(sim.FODAT, "yyyy"), 7, ' '));
                    pw.print(" " + Utils.PadLeft(sim.FSTRYR, 7, ' '));
                    pw.print(" " + Utils.PadLeft(sim.FENDYR, 7, ' '));
                    pw.print(" " + Utils.PadRight(sim.FWFILE, 16, ' '));
                    pw.print(" " + sim.FONAME);
                    pw.println();
                    
                    for (Comment comment : comments.getAll(level, Section.Simulation11)) {
                        pw.println(comment.description);
                    }
                }
                
                pw.println();
            }
        }
        // </editor-fold>
    }
}
