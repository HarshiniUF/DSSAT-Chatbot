package Extensions;

import java.awt.Image;
import java.net.URL;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import javax.swing.Icon;
import javax.swing.ImageIcon;

/**
 *
 * @author PCMIWS16
 */
public class Icons {

    private static HashMap<String, Icon> icons = new HashMap<>();
    private static final ArrayList<String> menus = new ArrayList<>( Arrays.asList("General Information", "Notes", "Environment", "Fields", "Initial Conditions", "Soil Analysis", "Environmental Modifications",
        "Management", "Cultivars", "Planting", "Irrigation", "Fertilizer", "Organic Amendments", "Tillage", "Harvest", "Chemical Applications", "Simulation Controls", "Treatment"));   

    public static void Init(Class<?> c) {
        for (String menu : menus) {
            URL resource = c.getResource("/icons/Left Menu/" + menu + ".png");
            if (resource != null) {
                ImageIcon icon = new ImageIcon(resource);
                icons.put(menu, scale(icon, 24, 24));
            }
        }
    }
    
    public static boolean hasIcon(String menu){
        return menus.contains(menu) && icons.get(menu) != null;
    }
    
    public static Icon getIcon(String menu){
        return icons.get(menu);
    }
    
    static Icon scale(ImageIcon icon, int iconWidth, int iconHeight) {
        
        Image img = icon.getImage();
        Image newimg = img.getScaledInstance(iconWidth, iconHeight, java.awt.Image.SCALE_SMOOTH);
        return new ImageIcon(newimg);
}
}
