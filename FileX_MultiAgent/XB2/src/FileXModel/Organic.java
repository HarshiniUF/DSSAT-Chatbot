/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package FileXModel;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;

/**
 *
 * @author Jazzy
 */
public class Organic extends ModelXBase implements Cloneable {

    protected ArrayList<OrganicApplication>  organicApps = new ArrayList<>();
    public Float EFIR;

    public String RENAME;

    public Organic(String RENAME)
    {
        this.RENAME = RENAME;
    }

    public Organic()
    {
    }

    public void AddApp(OrganicApplication organic)
    {
        organicApps.add(organic);
        
        Collections.sort(organicApps, organic.RDATE != null ? Comparator.comparing(OrganicApplication::getOrder) : Comparator.comparing(OrganicApplication::getOrderDay));
    }

    public void RemoveAt(int level)
    {
        organicApps.remove(level);
    }

    public void SetAt(int level, OrganicApplication organic)
    {
        organicApps.set(level, organic);
    }

    public ArrayList<OrganicApplication> GetApps()
    {
        return organicApps;
    }

    public OrganicApplication GetApp(int level)
    {
        return (OrganicApplication)organicApps.get(level);
    }

    public int GetSize()
    {
        return organicApps.size();
    }
    
    @Override
    public Organic clone() throws CloneNotSupportedException
    {
        return (Organic) super.clone();
    }

    @Override
    public String GetName() {
        return this.RENAME == null ? "" : this.RENAME;
    }
    
    @Override
    public void SetName(String name) {
        RENAME = name;
    }
}
