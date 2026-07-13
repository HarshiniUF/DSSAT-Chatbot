package xbuild.Components;

import java.lang.reflect.Constructor;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 *
 * @author Jazzy
 */
public class XInternalFrame {

    public static IXInternalFrame newInstance(String frameName) {
        try {
            Class<?> clazz = Class.forName("xbuild." + frameName);
            Constructor<?> ctor = clazz.getConstructor();
            Object[] object = null;
            IXInternalFrame instance = (IXInternalFrame) ctor.newInstance(object);

            return instance;
        } catch (Exception ex) {
            Logger.getLogger(XInternalFrame.class.getName()).log(Level.SEVERE, null, ex);
        }
        return null;
    }
    
    public static IXInternalFrame newInstance(String frameName, String nodeName) {

        try {
            Class<?> clazz = Class.forName("xbuild." + frameName);

            Constructor<?> ctor = clazz.getConstructor(String.class);
            Object[] object = new Object[]{nodeName};

            IXInternalFrame instance = (IXInternalFrame) ctor.newInstance(object);

            return instance;
        } catch (Exception ex) {
            Logger.getLogger(XInternalFrame.class.getName()).log(Level.SEVERE, null, ex);
        }

        try {
            Class<?> clazz = Class.forName("xbuild." + frameName);
            Constructor<?> ctor = clazz.getConstructor();
            Object[] object = null;
            IXInternalFrame instance = (IXInternalFrame) ctor.newInstance(object);

            return instance;
        } catch (Exception ex) {
            Logger.getLogger(XInternalFrame.class.getName()).log(Level.SEVERE, null, ex);
        }

        return null;
    }
}
