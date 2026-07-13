/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package DSSATModel;

import java.util.Hashtable;

/**
 *
 * @author Jazzy
 */
public class DssatProfile {

    private static Hashtable dssatPro = new Hashtable();

    public static void AddNew(String Code, String Description)
    {
        dssatPro.put(Code, Description);
    }

    public static String GetAt(String Code)
    {
        String Description = null;
        try {
            Description = (String) dssatPro.get(Code);
        } catch (Exception e) {
        }

        return Description;
    }
}
