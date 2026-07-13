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
public class Chemical extends ModelXBase implements Cloneable {

    protected ArrayList<ChemicalApplication>  chems = new ArrayList<>();
    public String CHNAME;

    public Chemical(String CHNAME)
    {
        this.CHNAME = CHNAME;
    }

    public Chemical()
    {
    }

    public void AddApp(ChemicalApplication chem)
    {
        chems.add(chem);
        Collections.sort(chems, chem.CDATE != null ? Comparator.comparing(ChemicalApplication::getOrder) : Comparator.comparing(ChemicalApplication::getOrderDay));
    }

    public void RemoveAt(int level)
    {
        chems.remove(level);
    }

    public void SetAt(int level, ChemicalApplication chem)
    {
        chems.set(level, chem);
    }

    public ArrayList<ChemicalApplication> GetApps()
    {
        return chems;
    }

    public ChemicalApplication GetApp(int level)
    {
        return (ChemicalApplication)chems.get(level);
    }

    public int GetSize()
    {
        return chems.size();
    }
    
    @Override
    public Chemical clone() throws CloneNotSupportedException
    {
        return (Chemical) super.clone();
    }

    @Override
    public String GetName() {
        return this.CHNAME == null ? "" : this.CHNAME;
    }

    @Override
    public void SetName(String name) {
        this.CHNAME = name;
    }
}
