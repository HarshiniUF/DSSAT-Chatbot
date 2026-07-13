package DSSATRepository;

import DSSATModel.*;
import java.io.BufferedReader;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 *
 * @author Jazzy
 */
public class SimulationRepository extends DSSATRepositoryBase {
    
    public SimulationRepository(String rootPath) {
        super(rootPath);
    }
    
    @Override
    public ArrayList<String> Parse() {
        ArrayList<String> cropModel = new ArrayList<>();

        try {
            FileReader file = new FileReader(rootPath + "\\Simulation.cde");

            BufferedReader br = new BufferedReader(file);
            Boolean bSimStart = false;
            Boolean bSimOptionWater = false;
            Boolean bSimOptionSymbiosis = false;
            Boolean bSimOptionCO2 = false;
            Boolean bSimMethodWeather = false;
            Boolean bSimMethodEvap = false;
            Boolean bSimMethodInitial = false;
            Boolean bSimMethodInfil = false;
            Boolean bSimMethodPhoto = false;
            Boolean bSimMethodHydrology = false;
            Boolean bSimMethodSOM = false;
            Boolean bSimMethodSoilEvap = false;
            Boolean bSimMethodSoilLayer = false;
            Boolean bSimManagePlanting = false;
            Boolean bSimManageIrrigation = false;
            Boolean bSimManageFertilizer = false;
            Boolean bSimManageResidue = false;
            Boolean bSimManageHarvest = false;
            Boolean bSimOutput = false;
            Boolean bSimOutputOption = false;
            Boolean bSimOutputVerbose = false;
            Boolean bSimOutputFormat = false;
            Boolean bCropModel = false;
            
            SimulationStart.Clear();
            SimulationOptionWater.Clear();
            SimulationOptionSymbiosis.Clear();
            SimulationOptionCO2List.Clear();
            SimulationMethodWeather.Clear();
            SimulationMethodInitial.Clear();
            SimulationMethodEvap.Clear();
            SimulationMethodInfil.Clear();
            SimulationMethodPhoto.Clear();
            SimulationMethodHydrology.Clear();
            SimulationMethodSOM.Clear();
            SimulationMethodSoilEvap.Clear();
            SimulationMethodSoilLayer.Clear();
            SimulationManagePlanting.Clear();
            SimulationManagerIrrigation.Clear();
            SimulationManageFertilzation.Clear();
            SimulationManageResidue.Clear();
            SimulationManageHarvest.Clear();
            SimulationOutput.Clear();
            SimulationOutputOption.Clear();
            SimulationOutputVerbose.Clear();
            SimulationOutputFormat.Clear();
            

            String strRead = null;
            while ((strRead = br.readLine()) != null) {
                // <editor-fold defaultstate="collapsed" desc="Simulation Start">
                if (strRead.trim().startsWith("*Start Simulation")) {
                    bSimStart = true;
                } else if (bSimStart) {
                    if (!"".equals(strRead.trim())) {
                        if (!strRead.trim().startsWith("@") && !strRead.trim().startsWith("!")) {
                            String tmp = strRead.trim();
                            String Code = tmp.substring(0, 8).trim();
                            String Description = tmp.substring(9, tmp.length() - 2).trim();
                            SimulationStart.AddNew(Code, Description);
                        }
                    } else {
                        bSimStart = false;

                    }
                } // </editor-fold>
                // <editor-fold defaultstate="collapsed" desc="Simulation/Options/Water">
                /*
                    else if (strRead.trim().startsWith("*Simulation/Options/Water")) {
                        bSimOptionWater = true;
                    } else if (bSimOptionWater) {
                        if (!"".equals(strRead.trim())) {
                            if (!strRead.trim().startsWith("@") && !strRead.trim().startsWith("!")) {
                                String tmp = strRead.trim();
                                String Code = tmp.substring(0, 8).trim();
                                String Description = tmp.substring(9, tmp.length() - 2).trim();
                                SimulationOptionWater.AddNew(Code, Description);
                            }
                        } else {
                            bSimOptionWater = false;
                            
                        }
                    }*/ // </editor-fold>
                // <editor-fold defaultstate="collapsed" desc="Simulation/Options/Symbiosis">
                else if (strRead.trim().startsWith("*Simulation/Options/Symbiosis")) {
                    bSimOptionSymbiosis = true;
                } else if (bSimOptionSymbiosis) {
                    if (!"".equals(strRead.trim())) {
                        if (!strRead.trim().startsWith("@") && !strRead.trim().startsWith("!")) {
                            String tmp = strRead.trim();
                            String Code = tmp.substring(0, 8).trim();
                            String Description = tmp.substring(9, tmp.length() - 2).trim();
                            SimulationOptionSymbiosis.AddNew(Code, Description);
                        }
                    } else {
                        bSimOptionSymbiosis = false;

                    }
                } // </editor-fold>
                // <editor-fold defaultstate="collapsed" desc="Simulation/Options/CO2">
                /*
                    else if (strRead.trim().startsWith("*Simulation/Options/CO2")) {
                        bSimOptionCO2 = true;
                    } else if (bSimOptionCO2) {
                        if (!"".equals(strRead.trim())) {
                            if (!strRead.trim().startsWith("@") && !strRead.trim().startsWith("!")) {
                                String tmp = strRead.trim();
                                String Code = tmp.substring(0, 8).trim();
                                String Description = tmp.substring(9, tmp.length() - 2).trim();
                                SimulationOptionCO2.AddNew(Code, Description);
                            }
                        } else {
                            bSimOptionCO2 = false;
                            
                        }
                    }*/ // </editor-fold>
                // <editor-fold defaultstate="collapsed" desc="Simulation/Methods/Weather">
                else if (strRead.trim().startsWith("*Simulation/Methods/Weather")) {
                    bSimMethodWeather = true;
                } else if (bSimMethodWeather) {
                    if (!"".equals(strRead.trim())) {
                        if (!strRead.trim().startsWith("@") && !strRead.trim().startsWith("!")) {
                            String tmp = strRead.trim();
                            String Code = tmp.substring(0, 8).trim();
                            String Description = tmp.substring(9, tmp.length() - 2).trim();
                            SimulationMethodWeather.AddNew(Code, Description);
                        }
                    } else {
                        bSimMethodWeather = false;

                    }
                } // </editor-fold>
                // <editor-fold defaultstate="collapsed" desc="Simulation/Methods/Initial Soil Conditions">
                else if (strRead.trim().startsWith("*Simulation/Methods/Initial Soil Conditions")) {
                    bSimMethodInitial = true;
                } else if (bSimMethodInitial) {
                    if (!"".equals(strRead.trim())) {
                        if (!strRead.trim().startsWith("@") && !strRead.trim().startsWith("!")) {
                            String tmp = strRead.trim();
                            String Code = tmp.substring(0, 8).trim();
                            String Description = tmp.substring(9, tmp.length() - 2).trim();
                            SimulationMethodInitial.AddNew(Code, Description);
                        }
                    } else {
                        bSimMethodInitial = false;

                    }
                } // </editor-fold>
                // <editor-fold defaultstate="collapsed" desc="Simulation/Methods/Evapotransportation">
                else if (strRead.trim().startsWith("*Simulation/Methods/Evapotransportation")) {
                    bSimMethodEvap = true;
                } else if (bSimMethodEvap) {
                    if (!"".equals(strRead.trim())) {
                        if (!strRead.trim().startsWith("@") && !strRead.trim().startsWith("!")) {
                            String tmp = strRead.trim();
                            String Code = tmp.substring(0, 8).trim();
                            String Description = tmp.substring(9, tmp.length() - 2).trim();
                            SimulationMethodEvap.AddNew(Code, Description);
                        }
                    } else {
                        bSimMethodEvap = false;

                    }
                } // </editor-fold>
                // <editor-fold defaultstate="collapsed" desc="Simulation/Methods/Infiltration">
                else if (strRead.trim().startsWith("*Simulation/Methods/Infiltration")) {
                    bSimMethodInfil = true;
                } else if (bSimMethodInfil) {
                    if (!"".equals(strRead.trim())) {
                        if (!strRead.trim().startsWith("@") && !strRead.trim().startsWith("!")) {
                            String tmp = strRead.trim();
                            String Code = tmp.substring(0, 8).trim();
                            String Description = tmp.substring(9, tmp.length() - 2).trim();
                            SimulationMethodInfil.AddNew(Code, Description);
                        }
                    } else {
                        bSimMethodInfil = false;

                    }
                } // </editor-fold>
                // <editor-fold defaultstate="collapsed" desc="Simulation/Methods/Photosynthesis">
                else if (strRead.trim().startsWith("*Simulation/Methods/Photosynthesis")) {
                    bSimMethodPhoto = true;
                } else if (bSimMethodPhoto) {
                    if (!"".equals(strRead.trim())) {
                        if (!strRead.trim().startsWith("@") && !strRead.trim().startsWith("!")) {
                            String tmp = strRead.trim();
                            String Code = tmp.substring(0, 8).trim();
                            String Description = tmp.substring(9, tmp.length() - 2).trim();
                            SimulationMethodPhoto.AddNew(Code, Description);
                        }
                    } else {
                        bSimMethodPhoto = false;

                    }
                } // </editor-fold>
                // <editor-fold defaultstate="collapsed" desc="Simulation/Methods/Hydrology">
                else if (strRead.trim().startsWith("*Simulation/Methods/Hydrology")) {
                    bSimMethodHydrology = true;
                } else if (bSimMethodHydrology) {
                    if (!"".equals(strRead.trim())) {
                        if (!strRead.trim().startsWith("@") && !strRead.trim().startsWith("!")) {
                            String tmp = strRead.trim();
                            String Code = tmp.substring(0, 8).trim();
                            String Description = tmp.substring(9, tmp.length() - 2).trim();
                            SimulationMethodHydrology.AddNew(Code, Description);
                        }
                    } else {
                        bSimMethodHydrology = false;

                    }
                } // </editor-fold>
                // <editor-fold defaultstate="collapsed" desc="Simulation/Methods/SOM">
                else if (strRead.trim().startsWith("*Simulation/Methods/SOM")) {
                    bSimMethodSOM = true;
                } else if (bSimMethodSOM) {
                    if (!"".equals(strRead.trim())) {
                        if (!strRead.trim().startsWith("@") && !strRead.trim().startsWith("!")) {
                            String tmp = strRead.trim();
                            String Code = tmp.substring(0, 8).trim();
                            String Description = tmp.substring(9, tmp.length() - 2).trim();
                            SimulationMethodSOM.AddNew(Code, Description);
                        }
                    } else {
                        bSimMethodSOM = false;

                    }
                } // </editor-fold>
                // <editor-fold defaultstate="collapsed" desc="Simulation/Methods/Soil Evaporation">
                else if (strRead.trim().startsWith("*Simulation/Methods/Soil Evaporation")) {
                    bSimMethodSoilEvap = true;
                } else if (bSimMethodSoilEvap) {
                    if (!"".equals(strRead.trim())) {
                        if (!strRead.trim().startsWith("@") && !strRead.trim().startsWith("!")) {
                            String tmp = strRead.trim();
                            String Code = tmp.substring(0, 8).trim();
                            String Description = tmp.substring(9, tmp.length() - 2).trim();
                            SimulationMethodSoilEvap.AddNew(Code, Description);
                        }
                    } else {
                        bSimMethodSoilEvap = false;

                    }
                } // </editor-fold>
                // <editor-fold defaultstate="collapsed" desc="Simulation/Methods/Soil Layer Distribution">
                else if (strRead.trim().startsWith("*Simulation/Methods/Soil Layer Distribution")) {
                    bSimMethodSoilLayer = true;
                } else if (bSimMethodSoilLayer) {
                    if (!"".equals(strRead.trim())) {
                        if (!strRead.trim().startsWith("@") && !strRead.trim().startsWith("!")) {
                            String tmp = strRead.trim();
                            String Code = tmp.substring(0, 8).trim();
                            String Description = tmp.substring(9, tmp.length() - 2).trim();
                            SimulationMethodSoilLayer.AddNew(Code, Description);
                        }
                    } else {
                        bSimMethodSoilLayer = false;

                    }
                } // </editor-fold>
                // <editor-fold defaultstate="collapsed" desc="Simulation/Management/Planting">
                else if (strRead.trim().startsWith("*Simulation/Management/Planting")) {
                    bSimManagePlanting = true;
                } else if (bSimManagePlanting) {
                    if (!"".equals(strRead.trim())) {
                        if (!strRead.trim().startsWith("@") && !strRead.trim().startsWith("!")) {
                            String tmp = strRead.trim();
                            String Code = tmp.substring(0, 8).trim();
                            String Description = tmp.substring(9, tmp.length() - 2).trim();
                            SimulationManagePlanting.AddNew(Code, Description);
                        }
                    } else {
                        bSimManagePlanting = false;

                    }
                } // </editor-fold>
                // <editor-fold defaultstate="collapsed" desc="Simulation/Management/Irrigation">
                else if (strRead.trim().startsWith("*Simulation/Management/Irrigation")) {
                    bSimManageIrrigation = true;
                } else if (bSimManageIrrigation) {
                    if (!"".equals(strRead.trim())) {
                        if (!strRead.trim().startsWith("@") && !strRead.trim().startsWith("!")) {
                            String tmp = strRead.trim();
                            String Code = tmp.substring(0, 8).trim();
                            String Description = tmp.substring(9, tmp.length() - 2).trim();
                            SimulationManagerIrrigation.AddNew(Code, Description);
                        }
                    } else {
                        bSimManageIrrigation = false;

                    }
                } // </editor-fold>
                // <editor-fold defaultstate="collapsed" desc="Simulation/Management/Fertilization">
                else if (strRead.trim().startsWith("*Simulation/Management/Fertilization")) {
                    bSimManageFertilizer = true;
                } else if (bSimManageFertilizer) {
                    if (!"".equals(strRead.trim())) {
                        if (!strRead.trim().startsWith("@") && !strRead.trim().startsWith("!")) {
                            String tmp = strRead.trim();
                            String Code = tmp.substring(0, 8).trim();
                            String Description = tmp.substring(9, tmp.length() - 2).trim();
                            SimulationManageFertilzation.AddNew(Code, Description);
                        }
                    } else {
                        bSimManageFertilizer = false;

                    }
                } // </editor-fold>
                // <editor-fold defaultstate="collapsed" desc="Simulation/Management/Residue">
                else if (strRead.trim().startsWith("*Simulation/Management/Residue")) {
                    bSimManageResidue = true;
                } else if (bSimManageResidue) {
                    if (!"".equals(strRead.trim())) {
                        if (!strRead.trim().startsWith("@") && !strRead.trim().startsWith("!")) {
                            String tmp = strRead.trim();
                            String Code = tmp.substring(0, 8).trim();
                            String Description = tmp.substring(9, tmp.length() - 2).trim();
                            SimulationManageResidue.AddNew(Code, Description);
                        }
                    } else {
                        bSimManageResidue = false;

                    }
                } // </editor-fold>
                // <editor-fold defaultstate="collapsed" desc="Simulation/Management/Harvest">
                else if (strRead.trim().startsWith("*Simulation/Management/Harvest")) {
                    bSimManageHarvest = true;
                } else if (bSimManageHarvest) {
                    if (!"".equals(strRead.trim())) {
                        if (!strRead.trim().startsWith("@") && !strRead.trim().startsWith("!")) {
                            String tmp = strRead.trim();
                            String Code = tmp.substring(0, 8).trim();
                            String Description = tmp.substring(9, tmp.length() - 2).trim();
                            SimulationManageHarvest.AddNew(Code, Description);
                        }
                    } else {
                        bSimManageHarvest = false;

                    }
                } // </editor-fold>
                // <editor-fold defaultstate="collapsed" desc="Simulation/Outputs">
                else if (strRead.trim().equalsIgnoreCase("*Simulation/Outputs")) {
                    bSimOutput = true;
                } else if (bSimOutput) {
                    if (!"".equals(strRead.trim())) {
                        if (!strRead.trim().startsWith("@") && !strRead.trim().startsWith("!")) {
                            String tmp = strRead.trim();
                            String Code = tmp.substring(0, 8).trim();
                            String Description = tmp.substring(9, tmp.length() - 2).trim();
                            SimulationOutput.AddNew(Code, Description);
                        }
                    } else {
                        bSimOutput = false;

                    }
                } // </editor-fold>
                // <editor-fold defaultstate="collapsed" desc="Simulation/Outputs/Options">
                else if (strRead.trim().startsWith("*Simulation/Outputs/Options")) {
                    bSimOutputOption = true;
                } else if (bSimOutputOption) {
                    if (!"".equals(strRead.trim())) {
                        if (!strRead.trim().startsWith("@") && !strRead.trim().startsWith("!")) {
                            String tmp = strRead.trim();
                            String Code = tmp.substring(0, 8).trim();
                            String Description = tmp.substring(9, tmp.length() - 2).trim();
                            SimulationOutputOption.AddNew(Code, Description);
                        }
                    } else {
                        bSimOutputOption = false;

                    }
                } // </editor-fold>
                // <editor-fold defaultstate="collapsed" desc="Simulation/Outputs/Verbose">
                else if (strRead.trim().startsWith("*Simulation/Outputs/Verbose")) {
                    bSimOutputVerbose = true;
                } else if (bSimOutputVerbose) {
                    if (!"".equals(strRead.trim())) {
                        if (!strRead.trim().startsWith("@") && !strRead.trim().startsWith("!")) {
                            String tmp = strRead.trim();
                            String Code = tmp.substring(0, 8).trim();
                            String Description = tmp.substring(9, tmp.length() - 2).trim();
                            SimulationOutputVerbose.AddNew(Code, Description);
                        }
                    } else {
                        bSimOutputVerbose = false;

                    }
                } // </editor-fold>
                // <editor-fold defaultstate="collapsed" desc="Simulation/Outputs/Format">
                else if (strRead.trim().startsWith("*Simulation/Outputs/Format")) {
                    bSimOutputFormat = true;
                } else if (bSimOutputFormat) {
                    if (!"".equals(strRead.trim())) {
                        if (!strRead.trim().startsWith("@") && !strRead.trim().startsWith("!")) {
                            String tmp = strRead.trim();
                            String Code = tmp.substring(0, 8).trim();
                            String Description = tmp.substring(9, tmp.length() - 2).trim();
                            SimulationOutputFormat.AddNew(Code, Description);
                        }
                    } else {
                        bSimOutputFormat = false;

                    }
                } // </editor-fold>
                // <editor-fold defaultstate="collapsed" desc="Crop Models">
                else if (strRead.trim().startsWith("*Simulation/Crop Models")) {
                    bCropModel = true;
                } else if (bCropModel) {
                    if (!"".equals(strRead.trim())) {
                        if (!strRead.trim().startsWith("@") && !strRead.trim().startsWith("!")) {
                            String s = strRead;
                            cropModel.add(s);
                        }
                    } else {
                        bCropModel = false;
                    }
                }
                // </editor-fold>
            }
            SimulationOptionWater.AddNew("Y", "Yes");
            SimulationOptionWater.AddNew("N", "No");

            SimulationOptionCO2List.AddNew("D", "Use default value (380 vpm)");
            SimulationOptionCO2List.AddNew("M", "Actual CO2; Mauna Loa, Hawaii (Keeling curve)");
            SimulationOptionCO2List.AddNew("W", "Read from weather file");
            
            br.close();
            file.close();

        } catch (FileNotFoundException ex) {
            System.out.println(ex);
        } catch (IOException ex) {
            Logger.getLogger(CropRepository.class.getName()).log(Level.SEVERE, null, ex);
        }
        
        return cropModel;
    }
}
