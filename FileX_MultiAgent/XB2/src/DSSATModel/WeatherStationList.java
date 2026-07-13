/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package DSSATModel;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

/**
 *
 * @author Jazzy
 */
public class WeatherStationList {
    //protected static Hashtable wStation = new Hashtable();
    protected static ArrayList<WeatherStation> wStation = new ArrayList<>();

    public static void AddNew(WeatherStation weather)
    {
        wStation.add(weather);
    }

    public static WeatherStation GetAt(String Code)
    {
        WeatherStation weather = null;
        for(WeatherStation w : wStation) {
           if(w.Code.equalsIgnoreCase(Code)){
               weather = w;
               break;
           } 
        }
        return weather;
    }
    
    public static WeatherStation GetAt(String Code, WstaType type)
    {
        WeatherStation weather = null;
        for(WeatherStation w : wStation) {
           if(w.Code.equalsIgnoreCase(Code) && w.Type == type){
               weather = w;
               break;
           } 
        }
        return weather;
    }
    
    public static void Clear(){
        wStation.clear();
    }

    public static WeatherStation GetAt(int n)
    {
        WeatherStation weather = null;
        try{
            //Object[] object = wStation.values().toArray();
            weather = (WeatherStation) wStation.get(n);
        }
        catch(Exception ex) {}

        return weather;
    }
    
    public static List<WeatherStation> GetAll(WstaType type)
    {
        List<WeatherStation> weatherList = new ArrayList<>();
        
        for(Object object : wStation.toArray()){
            WeatherStation wsta = (WeatherStation) object;
            if(wsta.Type == type)
                weatherList.add(wsta);
        }
        
        Collections.sort(weatherList, (WeatherStation w1, WeatherStation w2) -> w1.StationName.compareTo(w2.StationName));

        return weatherList;
    }
    
    public static boolean Exists(WeatherStation weather){
        for(Object o : wStation.toArray()){
            WeatherStation w = (WeatherStation)o;
            if(w.Code.equalsIgnoreCase(weather.Code) && w.StationName.equalsIgnoreCase(weather.StationName))
                return true;
        }
        
        return false;
    }

    public static int size()
    {
        return wStation.size();
    }
}
