package DSSATServices;

import DSSATRepository.ResiduesRepository;
import DSSATModel.Residues;
import DSSATModel.ResiduesList;
import java.util.ArrayList;

/**
 *
 * @author Jazzy
 */
public class ResiduesService extends DSSATServiceBase {
    private final ResiduesRepository residuesRepository;
    
    public ResiduesService(String rootPath) {
        super(rootPath);
        
        this.residuesRepository = new ResiduesRepository(rootPath);
    }
    
    @Override
    public void Parse() throws Exception{
        boolean isValid = true;
        
        try {
            ArrayList<String> residuesList = this.residuesRepository.Parse();
            ResiduesList.Clear();
            
            for(int i = 0;i < residuesList.size();i++)
            {
                Residues res = new Residues();
                String tmp = residuesList.get(i);

                res.Code = tmp.substring(0, 5).trim();
                res.Description = tmp.substring(9, 78).trim();
                ResiduesList.AddNew(res);
            }
        } catch (Exception ex) {
            throw ex;
        }
        
        if(!isValid){
            throw new Exception("Residues parse failed");
        }
    }
    
    @Override
    public String getName() {
        return "Residues";
    }
}
