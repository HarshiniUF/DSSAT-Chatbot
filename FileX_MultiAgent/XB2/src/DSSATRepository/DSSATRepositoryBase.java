package DSSATRepository;

import java.util.ArrayList;

/**
 *
 * @author Jazzy
 */
public abstract class DSSATRepositoryBase {
    protected String rootPath;
    
    public DSSATRepositoryBase(String rootPath){
        this.rootPath = rootPath;
    }
    public ArrayList<String> Parse() throws Exception {
        return new ArrayList<>();
    }
    
    /**
     *
     * @param subFolder
     * @param extension
     * @return
     * @throws Exception
     */
    public ArrayList<String> Parse(String subFolder, String extension) throws Exception {
        return new ArrayList<>();
    }
}
