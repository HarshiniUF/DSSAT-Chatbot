package DSSATServices;

import DSSATRepository.FertilizerRepository;
import DSSATModel.FertilizerMaterial;
import DSSATModel.FertilizerMaterialList;
import java.util.ArrayList;

/**
 *
 * @author Jazzy
 */
public class FertilizerService extends DSSATServiceBase {
    private final FertilizerRepository fertilizerRepository;
    public FertilizerService(String rootPath) {
        super(rootPath);
        
        this.fertilizerRepository = new FertilizerRepository(rootPath);
    }
    
    @Override
    public void Parse() throws Exception{
        boolean isValid = true;
        
        try {
            ArrayList<String> fertilizerList = this.fertilizerRepository.Parse();
            FertilizerMaterialList.Clear();
            
            for(int i = 0;i < fertilizerList.size();i++)
            {
                FertilizerMaterial fertil = new FertilizerMaterial();
                String tmp = fertilizerList.get(i);

                fertil.Code = tmp.substring(0, 5).trim();
                fertil.Description = tmp.substring(9, 78).trim();
                FertilizerMaterialList.AddNew(fertil);
            }
        }
        catch (Exception ex) {
            isValid = false;
        }
        
        if(!isValid){
            throw new Exception("Fertilizer parse failed");
        }
    }
    
    @Override
    public String getName() {
        return "Fertilizer";
    }
}
