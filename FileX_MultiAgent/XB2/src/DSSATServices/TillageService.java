package DSSATServices;

import DSSATRepository.TillageRepository;
import DSSATModel.TillageImplement;
import DSSATModel.TillageImplementList;
import java.util.ArrayList;

/**
 *
 * @author Jazzy
 */
public class TillageService extends DSSATServiceBase {
    private final TillageRepository tillageRepository;
    public TillageService(String rootPath) {
        super(rootPath);
        
        this.tillageRepository = new TillageRepository(rootPath);
    }
    
    @Override
    public void Parse() throws Exception{
        boolean isValid = true;
        
        try {
            ArrayList<String> tillageList = this.tillageRepository.Parse();
            TillageImplementList.Clear();
            
            for(int i = 0;i < tillageList.size();i++)
            {
                TillageImplement tillage = new TillageImplement();
                String tmp = tillageList.get(i);

                try
                {
                    tillage.Code = tmp.substring(0, 5).trim();
                    tillage.Description = tmp.substring(9, tmp.length()-2).trim();
                    TillageImplementList.AddNew(tillage);
                }
                catch(Exception ex) {
                    isValid = false;
                }
            }
        } catch (Exception ex) {
            throw ex;
        }
        
        if(!isValid){
            throw new Exception("Tillage parse failed");
        }
    }
    
    @Override
    public String getName() {
        return "Tillage";
    }
}
