package DSSATServices;

import DSSATRepository.SoilRepository;
import DSSATModel.Soil;
import DSSATModel.SoilList;
import Extensions.Utils;
import java.util.ArrayList;

/**
 *
 * @author Jazzy
 */
public class SoilService extends DSSATServiceBase {

    private final SoilRepository soilRepository;

    public SoilService(String rootPath) {
        super(rootPath);

        this.soilRepository = new SoilRepository(rootPath);
    }

    @Override
    public void Parse() throws Exception {
        boolean isValid = true;
        String invalidResult = "";

        ArrayList<String> soilList = this.soilRepository.Parse();
        SoilList.Clear();
        for (String soilTemp : soilList) {

            try {
                String[] tmp = soilTemp.split("\\|")[0].split(":");
                String soilCode = tmp[0];
                String soilDescription = tmp[1];

                Soil soil = new Soil();
                soil.Code = soilCode;
                soil.Description = soilDescription;

                String[] profileTmp = soilTemp.split("\\|");
                String header = "@  SLB  SLMH  SLLL  SDUL  SSAT  SRGF  SSKS  SBDM  SLOC  SLCL  SLSI  SLCF  SLNI  SLHW  SLHB  SCEC  SADC";
                if (profileTmp.length > 1) {
                    for (int i = 1; i < profileTmp.length; i++) {
                        try {
                            String pro = profileTmp[i].split("\\^")[0];
                            Float SLB = Utils.GetFloat(header, pro, "SLB", 3);
                            String SLMH = Utils.GetString(header, pro, "SLMH", 5);
                            Float SLLL = Utils.GetFloat(header, pro, "SLLL", 5);
                            Float SDUL = Utils.GetFloat(header, pro, "SDUL", 5);
                            Float SSAT = Utils.GetFloat(header, pro, "SSAT", 5);
                            Float SRGF = Utils.GetFloat(header, pro, "SRGF", 5);
                            Float SSKS = Utils.GetFloat(header, pro, "SSKS", 5);
                            Float SBDM = Utils.GetFloat(header, pro, "SBDM", 5);
                            Float SLOC = Utils.GetFloat(header, pro, "SLOC", 5);
                            Float SLCL = Utils.GetFloat(header, pro, "SLCL", 5);
                            Float SLSI = Utils.GetFloat(header, pro, "SLSI", 5);
                            Float SLCF = Utils.GetFloat(header, pro, "SLCF", 5);
                            Float SLNI = Utils.GetFloat(header, pro, "SLNI", 5);
                            Float SLHW = Utils.GetFloat(header, pro, "SLHW", 5);
                            Float SLHB = Utils.GetFloat(header, pro, "SLHB", 5);
                            Float SCEC = Utils.GetFloat(header, pro, "SCEC", 5);
                            Float SADC = Utils.GetFloat(header, pro, "SADC", 5);

                            soil.AddProfile(SLB, SLMH, SLLL, SDUL, SSAT, SRGF, SSKS, SBDM, SLOC, SLCL, SLSI, SLCF, SLNI, SLHW, SLHB, SCEC, SADC);
                        }
                        catch(Exception ex){
                            isValid = false;
                            invalidResult += "\n" + profileTmp[i].split("\\^")[1];
                        }
                    }
                }

                SoilList.AddNew(soil);
            } catch (Exception ex) {
                isValid = false;
            }
        }

        if (!isValid) {
            throw new Exception(invalidResult);
        }
    }

    @Override
    public String getName() {
        return "Soil";
    }
}
