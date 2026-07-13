package DSSATServices;

import DSSATRepository.DSSATProfileRepository;
import DSSATModel.DssatProfile;
import java.util.ArrayList;

/**
 *
 * @author Jazzy
 */
public class DSSATProfileService {
    private final DSSATProfileRepository dssatProfileRepository;
    
    public DSSATProfileService(String rootPath){
        this.dssatProfileRepository = new DSSATProfileRepository(rootPath);
    }
    
    public void Parse() throws Exception {
        try{
            ArrayList<String> dssatList = this.dssatProfileRepository.Parse();
            
            for (int i = 0; i < dssatList.size(); i++) {
                String tmp = dssatList.get(i);
                String code = tmp.substring(0, 3).trim();
                String description = tmp.substring(3, tmp.length()).trim();
                description = description.replace(" ", "");
                DssatProfile.AddNew(code, description);
            }
        }
        catch(Exception ex){
            throw ex;
        }
    }
}
