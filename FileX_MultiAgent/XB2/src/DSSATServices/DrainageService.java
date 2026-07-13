package DSSATServices;

import DSSATRepository.DrainageRepository;
import DSSATModel.Drainage;
import DSSATModel.DrainageList;
import java.util.ArrayList;

/**
 *
 * @author Jazzy
 */
public class DrainageService extends DSSATServiceBase {
    private final DrainageRepository drainageRepository;
    
    public DrainageService(String rootPath) {
        super(rootPath);
        
        this.drainageRepository = new DrainageRepository(rootPath);
    }
    
    public void Parse() throws Exception{
        try {
            ArrayList<String> drainList = this.drainageRepository.Parse();
            DrainageList.Clear();
            
            for (int i = 0; i < drainList.size(); i++) {
                Drainage drain = new Drainage();
                String tmp = drainList.get(i);

                drain.Code = tmp.substring(0, 5).trim();
                drain.Description = tmp.substring(9, 78).trim();
                DrainageList.AddNew(drain);
            }
        } catch (Exception ex) {
            throw new Exception("Drainage parse failed");
        }
    }
    
    @Override
    public String getName() {
        return "Drainage";
    }
}
