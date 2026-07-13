package DSSATServices;

import DSSATRepository.IrrigationMethodRepository;
import DSSATModel.IrrigationMethod;
import DSSATModel.IrrigationMethodList;
import java.util.ArrayList;

/**
 *
 * @author PCMIWS16
 */
public class IrrigationMethodService extends DSSATServiceBase {
    private final IrrigationMethodRepository irrigationMethodRepository;
    public IrrigationMethodService(String rootPath) {
        super(rootPath);
        
        this.irrigationMethodRepository = new IrrigationMethodRepository(rootPath);
    }
    
    @Override
    public void Parse() throws Exception{
        boolean isValid = true;
        
        try {
            ArrayList<String> irrigationMethod = this.irrigationMethodRepository.Parse();
            IrrigationMethodList.Clear();
            
            for(int i = 0;i < irrigationMethod.size();i++)
            {
                IrrigationMethod irrig = new IrrigationMethod();
                String tmp = irrigationMethod.get(i);

                irrig.Code = tmp.substring(0, 5).trim();
                irrig.Description = tmp.substring(9, 78).trim();
                IrrigationMethodList.AddNew(irrig);
            }
        }
        catch (Exception ex) {
            isValid = false;
        }
        
        if(!isValid){
            throw new Exception("Irrigation Method parse failed");
        }
    }
    
    @Override
    public String getName() {
        return "Irrigation Method";
    }
}
