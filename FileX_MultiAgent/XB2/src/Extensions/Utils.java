package Extensions;

import java.text.DecimalFormat;
import java.text.SimpleDateFormat;
import java.time.LocalDate;
import java.time.ZoneId;
import java.util.Calendar;
import java.util.Date;
import java.util.Locale;

/**
 *
 * @author Jazzy
 */
public class Utils {

    public static void setTimeout(Runnable runnable, int delay) {
        new Thread(() -> {
            try {
                Thread.sleep(delay);
                runnable.run();
            } catch (Exception e) {
                System.err.println(e);
            }
        }).start();
    }

    public static Float GetFloat(String Header, String value, String field, int fieldLength) {
        int start = Header.indexOf(field) + field.length() - fieldLength - 1;
        Float val = null;
        if (start >= 0 && start < Header.indexOf(field)) {
            int stop = Math.min(start + fieldLength + 1, value.length());

            if(stop > start){
                String tmp = value.substring(start, stop).trim();

                if (tmp != null && !"".equals(tmp)) {
                    try {
                        val = Float.valueOf(tmp);
                    } catch (NumberFormatException ex) {
                        
                    }
                }
            }
        }
        return val;
    }
    
    public static Double GetDouble(String Header, String value, String field, int fieldLength) {
        int start = Header.indexOf(field) + field.length() - fieldLength - 1;
        Double val = null;

        if (start >= 0) {
            int stop = Math.min(start + fieldLength + 1, value.length());

            String tmp = value.substring(start, stop).trim();

            if (tmp != null && !"".equals(tmp)) {
                val = Double.valueOf(tmp);
            }
        }
        return val;
    }

    public static Date GetDate(String Header, String value, String field, int fieldLength) {
        int start = Header.indexOf(field) + field.length() - fieldLength - 1;
        Date val = null;

        if (start >= 0) {
            int stop = start + fieldLength + 1;

            String tmp = value.substring(start, stop).trim();

             if (!tmp.equals("-99") && !"".equals(tmp)) {
                try {
                    int yearDigits = tmp.length() == 7 ? 2 : 0;
                    Integer year = Integer.valueOf(tmp.substring(0, 2 + yearDigits));
                    
                    if(tmp.length() == 5){
                        if (year >= 60) {
                            year += 1900;
                        } else {
                            year += 2000;
                        }
                    }
                    
                    int day = Integer.parseInt(tmp.substring(2 + yearDigits, 5 + yearDigits));

                    int month[] = {31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31};
                    month[1] += ((year % 4) == 0) ? 1 : 0;

                    int dayCount = 0;
                    int nDay = 0;
                    int nMonth = 0;
                    for (int i = 0; i < 12; i++) {
                        if (day <= (dayCount + month[i])) {
                            nDay = day - dayCount;
                            nMonth = i;
                            break;
                        }
                        dayCount += month[i];
                    }

                    //val = new Date(year, nMonth, nDay);
                    Calendar ca = Calendar.getInstance(Locale.US);
                    ca.set(year, nMonth, nDay);
                    val = ca.getTime();
                } 
                catch (NumberFormatException numberFormatException) {
                    throw numberFormatException;
                }
                catch(Exception ex){
                    //LocalDate localDate = LocalDate.of(1900, 1, 1);
                    //return Date.from(localDate.atStartOfDay(ZoneId.systemDefault()).toInstant());
                    throw ex;
                }
            }
        }
        return val;
    }

    public static Integer GetInteger(String Header, String value, String field, int fieldLength) {        
        String tmp = GetString(Header, value, field, fieldLength);
        
        Integer val = null;
        if (tmp != null && !"".equals(tmp) && !tmp.equals("-99")) {
            val = Integer.valueOf(tmp);
        }

        return val;
    }

    public static Integer ParseInteger(Object value) {
        Integer val;
        if (value == null) {
            return 0;
        }
        val = Integer.valueOf(value.toString());

        return val;
    }
    
    public static Integer TryParseInteger(Object value) {
        Integer val;
        if (value == null) {
            return 0;
        }
        
        try{
            val = Integer.valueOf(value.toString());
        }
        catch(NumberFormatException e){
            val = 0;
        }
        return val;
    }

    public static Float ParseFloat(Object value) {
        Float val = null;

        try {
            if (value == null) {
                return 0.0f;
            }
            val = Float.valueOf(value.toString());
        } catch (NumberFormatException numberFormatException) {

        }
        return val;
    }
    
    public static Double ParseDouble(Object value) {
        Double val = null;

        try {
            if (value == null) {
                return 0.00d;
            }
            val = Double.valueOf(value.toString());
        } catch (NumberFormatException numberFormatException) {

        }
        return val;
    }

    public static String GetString(String Header, String value, String field, int fieldLength) {
        int start = Header.indexOf(field);
        String val = null;

        if (start >= 0 && start <= value.length()) {
            int stop = start + fieldLength;
            if (stop > value.length()) {
                stop = value.length();
            }

            String tmp = value.substring(start, stop).trim();
            if (tmp == null || "".equals(tmp.trim())) {
                val = "-99";
            } else {
                val = tmp;
            }

            //if(!tmp.equals("-99")) val = tmp;
        }
        return val;
    }

    public static String FloatToString(Float value) {
        DecimalFormat df = new DecimalFormat("##.##");
        String val = df.format(value);

        if (val.length() > 3) {
            if (val.substring(val.length() - 2).equals("00")) {
                val = val.substring(0, val.length() - 2);
            }
        }
        return val;
    }
    
    public static String DoubleToString(Double value) {
        DecimalFormat df = new DecimalFormat("##.##");
        String val = df.format(value);

        if (val.length() > 3) {
            if (val.substring(val.length() - 2).equals("00")) {
                val = val.substring(0, val.length() - 2);
            }
        }
        return val;
    }

    public static String PadLeft(String value, int count, char character) {
        if (value == null || "".equals(value.trim()) || "-99.0".equals(value) || "-99.00".equals(value) || "-99.000".equals(value)) {
            value = "-99";
        }

        for (int i = value.length(); i < count; i++) {
            value = character + value;
        }

        return value;
    }
    
    public static String PadLeft(String value, int count, char character, boolean ignoreRemoveDigit) {
        if (value == null) {
            value = "-99";
        }
        if ("".equals(value.trim())) {
            value = "-99";
        }

        if(!ignoreRemoveDigit){
            if (value.endsWith(".0")) {
                value = value.replace(".0", "");
            }
            if (value.endsWith(".00")) {
                value = value.replace(".00", "");
            }
            if (value.endsWith(".000")) {
                value = value.replace(".000", "");
            }
        }

        for (int i = value.length(); i < count; i++) {
            value = character + value;
        }

        return value;
    }

    public static String PadLeft(Integer value, int count, char character) {
        if (value == null) {
            value = -99;
        }
        return PadLeft(value.toString(), count, character);
    }

    public static String PadLeft(Float value, int count, char character) {
        if (value == null) {
            value = -99F;
        }
        return PadLeft(value.toString(), count, character, false);
    }
    
    public static String PadLeft(Double value, int count, char character) {
        if (value == null) {
            value = -99d;
        }
        return PadLeft(value.toString(), count, character);
    }

    public static String PadRight(Integer value, int count, char character) {
        if (value == null) {
            value = -99;
        }
        return PadLeft(value.toString(), count, character);
    }

    public static String PadRight(Float value, int count, char character) {
        if (value == null) {
            value = -99F;
        }
        return PadLeft(value.toString(), count, character);
    }

    public static String PadRight(String value, int count, char character) {
        if (value == null || "".equals(value.trim()) || "-99.0".equals(value) || "-99.00".equals(value) || "-99.000".equals(value)) {
            value = "-99";
        }

        for (int i = value.length(); i < count; i++) {
            value += character;
        }
        
        if(value.length() > count)
            value = value.substring(0, count);

        return value;
    }

    public static String JulianDate(Date date) {
        return JulianDate(date, "yy");
    }
    
    public static String JulianDate(Date date, String yearFormat) {
        String d;

        try {
            Calendar ca = Calendar.getInstance();
            ca.setTime(date);

            Locale l = new Locale("en", "US");
            SimpleDateFormat df = new SimpleDateFormat(yearFormat, l);

            d = df.format(date) + PadLeft(((Integer) ca.get(Calendar.DAY_OF_YEAR)).toString(), 3, '0');
        } catch (Exception e) {
            d = "-99";
        }

        return d;
    }

    public static boolean IsEmpty(String text) {
        return text == null || "".equals(text.trim());
    }
}
