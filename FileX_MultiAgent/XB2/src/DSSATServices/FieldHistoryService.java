package DSSATServices;

import DSSATRepository.FieldHistoryRepository;
import DSSATModel.FieldHistory;
import DSSATModel.FieldHistoryList;
import DSSATModel.Residues;
import DSSATModel.ResiduesList;
import java.util.ArrayList;

/**
 *
 * @author Jazz
 */
public class FieldHistoryService extends DSSATServiceBase {
    private final FieldHistoryRepository fieldHistoryRepository; 
    public FieldHistoryService(String rootPath) {
        super(rootPath);
        
        this.fieldHistoryRepository = new FieldHistoryRepository(rootPath);
    }
    
    @Override
    public void Parse() throws Exception{
        boolean isValid = true;
        
        try {
            ArrayList<String> fieldHistoryList = this.fieldHistoryRepository.Parse();
            FieldHistoryList.Clear();
            
            for(int i = 0;i < fieldHistoryList.size();i++)
            {
                FieldHistory field = new FieldHistory();
                String tmp = fieldHistoryList.get(i);

                try
                {
                    field.Code = tmp.substring(0, 5).trim();
                    field.Description = tmp.substring(9, tmp.length()-2).trim();
                    FieldHistoryList.AddNew(field);
                }
                catch(Exception ex) {
                    isValid = false;
                }
            }
        } catch (Exception ex) {
            throw ex;
        }
        
        if(!isValid){
            throw new Exception("Field History parse failed");
        }
    }
    
    @Override
    public String getName() {
        return "Field History";
    }
}
