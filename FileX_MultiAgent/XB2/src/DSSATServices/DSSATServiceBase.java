package DSSATServices;

/**
 *
 * @author Jazz
 */
public abstract class DSSATServiceBase {
    protected String rootPath;
    
    public DSSATServiceBase(String rootPath){
        this.rootPath = rootPath;
    }
    public abstract void Parse() throws Exception;
    public abstract String getName();
}
