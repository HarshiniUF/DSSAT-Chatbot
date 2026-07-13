package DSSATServices;

import DSSATRepository.EnvironmentRepository;
import DSSATModel.EnvironmentFactor;
import DSSATModel.EnvironmentFactorList;
import java.util.ArrayList;

/**
 *
 * @author Jazzy
 */
public class EnvironmentService extends DSSATServiceBase {
    private final EnvironmentRepository environmentRepository;
    
    public EnvironmentService(String rootPath) {
        super(rootPath);
        
        this.environmentRepository = new EnvironmentRepository(rootPath);
    }
    
    @Override
    public void Parse() throws Exception{
        boolean isValid = true;
        
        try {
            ArrayList<String> environmentList = this.environmentRepository.Parse();
            EnvironmentFactorList.Clear();
            
            for(int i = 0;i < environmentList.size();i++)
            {
                EnvironmentFactor env = new EnvironmentFactor();
                String tmp = environmentList.get(i);

                env.Code = tmp.substring(0, 5).trim();
                env.Description = tmp.substring(9, 78).trim();
                //EnvironmentFactorList.factors[i] = env;
                EnvironmentFactorList.Add(env);
            }
        } catch (Exception ex) {
            isValid = false;
        }
        
        if(!isValid){
            throw new Exception("Environment parse failed");
        }
    }
    
    @Override
    public String getName() {
        return "Environment";
    }
}
