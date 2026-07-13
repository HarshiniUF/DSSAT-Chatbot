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
public class WeatherStation {
    public String Code;
    public String StationName;
    public WstaType Type;
    public int Begin;
    public String Number;
    public ArrayList<String> FullCode;
    
    public WeatherStation(){
        FullCode = new ArrayList<>();
    }
    @Override
    public String toString(){
        return StationName;
    }
}
