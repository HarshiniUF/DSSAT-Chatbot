/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package FileXModel;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.Date;

/**
 *
 * @author Jazzy
 */
public class InitialCondition extends ModelXBase implements Cloneable {
    public String PCR;
    public Date ICDAT;
    public Float ICRT;
    public Float ICND;
    public Float ICRN;
    public Float ICRE;
    public Float ICWD;
    public Float ICRES;
    public Float ICREN;
    public Float ICREP;
    public Float ICRIP;
    public Float ICRID;
    public String ICNAME;
    protected ArrayList<InitialConditionApplication>  InitApps = new ArrayList<>();

    public InitialCondition(String ICNAME)
    {
        this.ICNAME = ICNAME;
    }

    public InitialCondition()
    {
        
    }
    
    public String GetName(){
        return this.ICNAME == null ? "" : this.ICNAME;
    }
    
    @Override
    public void SetName(String name) {
        ICNAME = name;
    }

    public void AddApp(InitialConditionApplication initApp)
    {
        InitApps.add(initApp);
        
        Collections.sort(InitApps, Comparator.comparing(InitialConditionApplication::getOrder));
    }

    public void RemoveAt(int level)
    {
        InitApps.remove(level);
    }

    public void SetAt(int level, InitialConditionApplication initApp)
    {
        InitApps.set(level, initApp);
    }

    public ArrayList<InitialConditionApplication> GetApps()
    {
        return InitApps;
    }

    public InitialConditionApplication GetApp(int level)
    {
        return (InitialConditionApplication)InitApps.get(level);
    }

    public int GetSize()
    {
        return InitApps.size();
    }
    
    @Override
    public InitialCondition clone() throws CloneNotSupportedException {
        return (InitialCondition)super.clone();
    } 
}
