package Extensions;

import java.awt.image.BufferedImage;
import java.io.IOException;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.Locale;
import javax.imageio.ImageIO;

/**
 *
 * @author Jazz
 */
public class Variables {
    
    private static SimpleDateFormat dateFormatWithTime;
    private static SimpleDateFormat dateFormat;
    private static String DATE_FORMAT;
    private static Locale locale;
    
    public static SimpleDateFormat getDateFormatWithTime()
    {
        if(dateFormatWithTime == null)
            dateFormatWithTime = new SimpleDateFormat(getDatePattern() + "hh:mm:ss", new Locale("en","US"));
        
        return dateFormatWithTime;
    }
    
    private static String getDatePattern(){
        if (DATE_FORMAT == null || "".equals(DATE_FORMAT.trim())) {
            DateFormat formatter = SimpleDateFormat.getDateInstance(SimpleDateFormat.SHORT, getLocale());            
            
            String pattern = ((SimpleDateFormat) formatter).toPattern();
            String localPattern = ((SimpleDateFormat) formatter).toLocalizedPattern();
            if(!localPattern.contains("MM"))
                localPattern = localPattern.replaceAll("M", "MM");
            if(!localPattern.contains("dd"))
                localPattern = localPattern.replaceAll("d", "dd");
            if(!localPattern.contains("yyyy"))
                localPattern = localPattern.replaceAll("yy", "yyyy");
            
            DATE_FORMAT = localPattern;
        }
        
        return DATE_FORMAT;
    }
    
    public static SimpleDateFormat getDateFormat()
    {
        if(dateFormat == null)
            dateFormat = new SimpleDateFormat(getDatePattern(), new Locale("en","US"));
        
        return dateFormat;
    }
    
    private static Locale getLocale() {
//        if (locale == null) {
//            locale = System.getProperty("user.language.format") == null
//                    ? Locale.getDefault()
//                    : new Locale(System.getProperty("user.language.format"), System.getProperty("user.country.format"));
//        }

        return locale;
    }
    
    public static void setLocale(Locale locale){
        Variables.locale = locale;
    }
    
    public static String getDateFormatString(){
        return getDatePattern();
    }
    
    public static BufferedImage getIconImage(Class<?> objectClass){
        BufferedImage image = null;
        try {
            image = ImageIO.read(objectClass.getResource("/icons/32/XB2Logo.png"));
        } catch (IOException ex) {
            System.out.println(ex.getMessage());
        }
        
        return image;
    }
    
    public static String getVersion(){
        return "v1.5.0.0";
    }
}
