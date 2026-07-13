/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package DSSATModel;

import java.util.ArrayList;

/**
 *
 * @author Jazzy
 */
public class SimulationOptionCO2List {

    private static final ArrayList<SimulationOptionCO2> sim = new ArrayList<>();

    public static void Clear() {
        sim.clear();
    }

    public static void AddNew(String Code, String Description) {
        sim.add(new SimulationOptionCO2(Code, Description) );
    }

    public static int GetSize() {
        return sim.size();
    }

    public static SimulationOptionCO2 GetAt(String Code) {
        for (SimulationOptionCO2 s : sim) {
            if (s.Code.equalsIgnoreCase(Code)) {
                return s;
            }
        }
        return null;
    }

    public static SimulationOptionCO2 GetAt(int n) {
        return sim.get(n);
    }

    public static ArrayList<SimulationOptionCO2> GetAll() {
        return sim;
    }
}
