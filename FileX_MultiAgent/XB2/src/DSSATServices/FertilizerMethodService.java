package DSSATServices;

import DSSATRepository.FertilizerMethodRepository;
import DSSATModel.FertilizerMethod;
import DSSATModel.FertilizerMethodList;
import java.util.ArrayList;

/**
 *
 * @author Jazzy
 */
public class FertilizerMethodService extends DSSATServiceBase {
    private final FertilizerMethodRepository fertilizerMethodRepository;
    public FertilizerMethodService(String rootPath) {
        super(rootPath);
        
        this.fertilizerMethodRepository = new FertilizerMethodRepository(rootPath);
    }
    
    @Override
    public void Parse() throws Exception{
        boolean isValid = true;
        
        try {
            ArrayList<String> fertilizerMethodList = this.fertilizerMethodRepository.Parse();
            FertilizerMethodList.Clear();
            
            for(int i = 0;i < fertilizerMethodList.size();i++)
            {
                FertilizerMethod fertil = new FertilizerMethod();
                String tmp = fertilizerMethodList.get(i);

                fertil.Code = tmp.substring(0, 5).trim();
                fertil.Description = tmp.substring(9, 78).trim();
                FertilizerMethodList.AddNew(fertil);
            }
        } catch (Exception ex) {
            isValid = false;
        }
        
        if(!isValid){
            throw new Exception("Fertilizer Method parse failed");
        }
    }
    
    @Override
    public String getName() {
        return "Fertilizer Method";
    }
}
