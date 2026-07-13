package DSSATServices;

import DSSATRepository.ChemicalRepository;
import DSSATModel.ChemicalMaterial;
import DSSATModel.ChemicalMaterialList;
import java.util.ArrayList;

/**
 *
 * @author Jazzy
 */
public class ChemicalService extends DSSATServiceBase {
    private final ChemicalRepository chemicalRepository;
    
    public ChemicalService(String rootPath) {
        super(rootPath);
        
        this.chemicalRepository = new ChemicalRepository(rootPath);
    }
    
    @Override
    public void Parse() throws Exception {
        try {
            ArrayList<String> chemList = this.chemicalRepository.Parse();
            ChemicalMaterialList.Clear();

            for (int i = 0; i < chemList.size(); i++) {
                ChemicalMaterial chem = new ChemicalMaterial();
                String tmp = chemList.get(i);

                chem.Code = tmp.substring(0, 5);
                chem.Description = tmp.substring(9, 78).trim();
                ChemicalMaterialList.AddNew(chem);
            }
        } catch (Exception ex) {
            throw new Exception("Chemical parse failed");
        }
    }
    
    @Override
    public String getName() {
        return "Chemical";
    }
}
