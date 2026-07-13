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
public class Soil {

    public String Code;
    public String Unknow1;
    public String Unknow2;
    public String Description;

    private ArrayList<SoilProfile> soilProfiles;
    
    public Soil(){
        soilProfiles = new ArrayList<>();
    }
    

    public void AddProfile(Float SLB, String SLMH, Float SLLL, Float SDUL, Float SSAT, Float SRGF, Float SSKS, Float SBDM, Float SLOC, Float SLCL, Float SLSI, Float SLCF, Float SLNI, Float SLHW, Float SLHB, Float SCEC, Float SADC) {
        SoilProfile profile = new SoilProfile();
        profile.SLB = SLB;
        profile.SLMH = SLMH;
        profile.SLLL = SLLL;
        profile.SDUL = SDUL;
        profile.SSAT = SSAT;
        profile.SRGF = SRGF;
        profile.SSKS = SSKS;
        profile.SBDM = SBDM;
        profile.SLOC = SLOC;
        profile.SLCL = SLCL;
        profile.SLSI = SLSI;
        profile.SLCF = SLCF;
        profile.SLNI = SLNI;
        profile.SLHW = SLHW;
        profile.SLHB = SLHB;
        profile.SCEC = SCEC;
        profile.SADC = SADC;

        soilProfiles.add(profile);
    }
    
    public ArrayList<SoilProfile> GetSoilProfiles(){
        return soilProfiles;
    }

    @Override
    public String toString() {
        return Description;
    }
}
