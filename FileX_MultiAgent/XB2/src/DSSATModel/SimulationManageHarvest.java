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
public class SimulationManageHarvest {

    private static final ArrayList<String[]> sim = new ArrayList<>();

    public static void Clear() {
        sim.clear();
    }

    public static void AddNew(String Code, String Description) {
        sim.add(new String[]{Code, Description});
    }

    public static int GetSize() {
        return sim.size();
    }

    public static String[] GetAt(String Code) {
        for (String[] s : sim) {
            if (s[0].equalsIgnoreCase(Code)) {
                return s;
            }
        }
        return null;
    }

    public static String[] GetAt(int n) {
        return sim.get(n);
    }

    public static ArrayList<String[]> GetAll() {
        return sim;
    }
}
