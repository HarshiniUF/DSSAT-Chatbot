/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package xbuild;

import java.io.File;
import java.io.FileFilter;

/**
 *
 * @author Jazzy
 */
public class ExtendFilter implements FileFilter {

    private String extend;
    private String filename;
    public ExtendFilter(String extend) {
        this.extend = extend;
    }

    public ExtendFilter(String filename, String extend) {
        this.extend = extend;
        this.filename = filename;
    }

    public boolean accept(File pathname) {
        //boolean bAccept = false;
        boolean bAccept = pathname.getName().toLowerCase().endsWith(extend.toLowerCase());

        if(bAccept && filename != null) {
            if (pathname.getName().toLowerCase().startsWith(filename.toLowerCase()))
                bAccept = true;
            else
                bAccept = false;
        }

        return bAccept;
    }
    
}
