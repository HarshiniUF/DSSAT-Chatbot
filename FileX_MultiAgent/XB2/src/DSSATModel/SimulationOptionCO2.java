package DSSATModel;

/**
 *
 * @author Jazz
 */
public class SimulationOptionCO2 {
    public String Code;
    public String Description;
    
    public SimulationOptionCO2(String code, String description){
        Code = code;
        Description = description;
    }
    
    @Override
    public String toString(){
        return Description;
    }
}
