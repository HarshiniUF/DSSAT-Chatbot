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
public class SimulationMethodWeather {

    private static ArrayList<String[]> sims = new ArrayList<>();

    public static void Clear() {
        sims.clear();
    }

    public static void AddNew(String Code, String Description){
        sims.add(new String[] {Code, Description});
    }

    public static int GetSize()
    {
        return sims.size();
    }

    public static String[] GetAt(String Code) {

        for (String[] s : sims) {
            if (s[0].equalsIgnoreCase(Code)) {
                return s;
            }
        }
        return null;
    }

    public static String[] GetAt(int n)
    {
        return sims.get(n);
    }

    public static ArrayList<String[]> GetAll(WstaType wstaType)
    {
        ArrayList<String[]> simList = new ArrayList<>();
        switch(wstaType){
            case WTH:
                simList.add(GetAt("M"));
                break;
            case WTG:
                simList.add(GetAt("G"));
                break;
            case CLI:
                simList.add(GetAt("W"));
                simList.add(GetAt("S"));
                break;
        }
        
        return simList;
    }
}
