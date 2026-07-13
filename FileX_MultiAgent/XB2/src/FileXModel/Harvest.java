/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package FileXModel;

import DSSATModel.GrowthStage;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;

/**
 *
 * @author Jazzy
 */
public class Harvest extends ModelXBase implements Cloneable {

    protected ArrayList<HarvestApplication>  harvestApps = new ArrayList<>();
    public String HNAME;

    public Harvest(String HNAME)
    {
        this.HNAME = HNAME;
    }

    public Harvest()
    {
    }

    public void AddApp(HarvestApplication harvestApp)
    {
        harvestApps.add(harvestApp);
        Collections.sort(harvestApps, harvestApp.HDATE != null ? Comparator.comparing(HarvestApplication::getOrder) : Comparator.comparing(HarvestApplication::getOrder));
    }

    public void RemoveAt(int level)
    {
        harvestApps.remove(level);
    }

    public void SetAt(int level, HarvestApplication harvestApp)
    {
        harvestApps.set(level, harvestApp);
    }

    public ArrayList<HarvestApplication> GetApps()
    {
        return harvestApps;
    }
    
    public List<HarvestApplication> GetAll(){
        List<HarvestApplication> list = new ArrayList<>();

        harvestApps.forEach(obj -> {
            list.add((HarvestApplication) obj);
        });

        Collections.sort(list, new Comparator<HarvestApplication>() {
            public int compare(GrowthStage c1, GrowthStage c2) {
                return c1.Code.compareTo(c2.Code);
            }

            @Override
            public int compare(HarvestApplication o1, HarvestApplication o2) {
                throw new UnsupportedOperationException("Not supported yet."); //To change body of generated methods, choose Tools | Templates.
            }
        });
        
        return list;
    }

    public HarvestApplication GetApp(int level)
    {
        return (HarvestApplication)harvestApps.get(level);
    }

    public int GetSize()
    {
        return harvestApps.size();
    }
    
    @Override
    public Harvest clone() throws CloneNotSupportedException
    {
        return (Harvest) super.clone();
    }

    @Override
    public String GetName() {
        return this.HNAME == null ? "" : this.HNAME;
    }
    
    @Override
    public void SetName(String name) {
        HNAME = name;
    }
}
