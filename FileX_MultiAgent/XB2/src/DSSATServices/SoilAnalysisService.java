package DSSATServices;

import DSSATRepository.SoilAnalysisRepository;
import DSSATModel.SoilAnalysisMethodPh;
import DSSATModel.SoilAnalysisMethodPhList;
import DSSATModel.SoilAnalysisMethodPhosphorus;
import DSSATModel.SoilAnalysisMethodPhosphorusList;
import DSSATModel.SoilAnalysisMethodPotassium;
import DSSATModel.SoilAnalysisMethodPotassiumList;
import java.util.ArrayList;

/**
 *
 * @author Jazzy
 */
public class SoilAnalysisService extends DSSATServiceBase {
    private final SoilAnalysisRepository soilAnalysisRepository;
    
    public SoilAnalysisService(String rootPath) {
        super(rootPath);
        
        this.soilAnalysisRepository = new SoilAnalysisRepository(rootPath);
    }
    
    @Override
    public void Parse() throws Exception{
        boolean isValid = true;
        
        try {
            ArrayList<String> soilAnalysis = this.soilAnalysisRepository.Parse();
            SoilAnalysisMethodPhosphorusList.Clear();
            SoilAnalysisMethodPhList.Clear();
            SoilAnalysisMethodPotassiumList.Clear();
            
            for(int i = 0;i < soilAnalysis.size();i++)
            {
                if(i >= 0 && i < 10)
                {
                    SoilAnalysisMethodPhosphorus phos = new SoilAnalysisMethodPhosphorus();
                    String tmp = soilAnalysis.get(i);

                    phos.Code = tmp.substring(0, 5).trim();
                    phos.Description = tmp.substring(9, 78).trim();
                    //SoilAnalysisMethodPhosphorusList.methods[i] = phos;
                    SoilAnalysisMethodPhosphorusList.AddNew(phos);
                }
                if(i >= 10 && i < 12)
                {
                    SoilAnalysisMethodPh ph = new SoilAnalysisMethodPh();
                    String tmp = soilAnalysis.get(i);

                    ph.Code = tmp.substring(0, 5).trim();
                    ph.Description = tmp.substring(9, 78).trim();
                    //SoilAnalysisMethodPhList.methods[i - 10] = ph;
                    SoilAnalysisMethodPhList.AddNew(ph);
                }
                if(i >= 12)
                {
                    SoilAnalysisMethodPotassium potass = new SoilAnalysisMethodPotassium();
                    String tmp = soilAnalysis.get(i);

                    potass.Code = tmp.substring(0, 5).trim();
                    potass.Description = tmp.substring(9, 78).trim();
                    SoilAnalysisMethodPotassiumList.AddNew(potass);
                }
            }
        } catch (Exception ex) {
            isValid = false;
        }
        
        if(!isValid){
            throw new Exception("Soil Analysis parse failed");
        }
    }
    
    @Override
    public String getName() {
        return "Soil Analysis";
    }
}
