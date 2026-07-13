package DSSATServices;

import DSSATRepository.CropRepository;
import DSSATModel.Crop;
import DSSATModel.CropList;
import DSSATModel.CultivarList;
import DSSATModel.DssatProfile;
import java.io.File;
import java.util.ArrayList;
import xbuild.*;

/**
 *
 * @author Jazzy
 */
public class CropService extends DSSATServiceBase {

    private final CropRepository cropRepository;

    public CropService(String rootPath) {
        super(rootPath);
        this.cropRepository = new CropRepository(rootPath);
    }

    @Override
    public void Parse() throws Exception {
        boolean isValid = true;

        try {
            ArrayList<String> cropList = this.cropRepository.Parse();

            CropList.Clear();
            CultivarList.Clear();

            for (int i = 0; i < cropList.size(); i++) {

                Crop crop = new Crop();
                String tmp = cropList.get(i);

                crop.CropCode = tmp.substring(0, 2);
                crop.CropName = tmp.substring(9, Math.min(tmp.length(), 78)).trim();
                CropList.AddNew(crop);

                String culFile = "";
                String genoTypeDir = DssatProfile.GetAt("CRD");

                File wc = new File(genoTypeDir);

                if (!wc.exists()) {
                    throw new Exception("Please check your Cultivar folder: " + genoTypeDir + "!!");
                }

                File culList[] = wc.listFiles(new ExtendFilter(crop.CropCode, ".cul"));

                for (File ci : culList) {
                    if (culFile.equals("")) {
                        culFile = genoTypeDir + "\\" + ci.getName();
                    }
                }
                if (culFile != null && !"".equals(culFile)) {
                    CultivarList.AddNew(crop, culFile);
                } else {
                    CultivarList.AddNew(crop, "");
                }
            }
        } catch (Exception ex) {
            throw ex;
        }

        if (!isValid) {
            throw new Exception("Crop parse failed");
        }
    }

    @Override
    public String getName() {
        return "Crop";
    }
}
