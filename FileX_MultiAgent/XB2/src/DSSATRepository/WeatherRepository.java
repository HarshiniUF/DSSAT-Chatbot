package DSSATRepository;

import DSSATModel.DssatProfile;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.util.ArrayList;
import xbuild.ExtendFilter;

/**
 *
 * @author Jazzy
 */
public class WeatherRepository extends DSSATRepositoryBase {

    public WeatherRepository(String rootPath) {
        super(rootPath);
    }

    @Override
    public ArrayList<String> Parse(String wstaType, String extension) throws Exception {
        ArrayList<String> weatherList = new ArrayList<>();
        String weatherDir = null;
        try {
            weatherDir = DssatProfile.GetAt(wstaType);
        } catch (Exception e) {
            throw e;
        }

        File w = new File(weatherDir);
        if (!w.exists()) {
            throw new Exception("Please check your weather folder: " + weatherDir + "!!");
        }
        File fList[] = w.listFiles(new ExtendFilter("." + extension));

        for (File file : fList) {

            String fullName = file.getName();
            String code = fullName.substring(0, 4);
            String number = "";
            String fullCode = "";
            if (fullName.length() > 4) {
                number = file.getName().substring(6, 8);
                fullCode = file.getName().substring(0, 8);
            }

            try (FileReader fileRead = new FileReader(file); BufferedReader wReader = new BufferedReader(fileRead)) {
                String strWRead;
                String wsta = "";
                String insi = "";

                boolean is2 = false;
                boolean is4 = false;
                boolean isCli = false;
                boolean isR = false;
                boolean isInsi = false;

                int line = 1;

                while ((strWRead = wReader.readLine()) != null) {
                    if("".equals(strWRead) || strWRead.startsWith("!")){
                        continue;
                    }
                    else if (strWRead.startsWith("*WEATHER") || strWRead.startsWith("**WEATHER") || strWRead.startsWith("$WEATHER") || strWRead.startsWith("*CLIMATE")) {
                        String WSTAName = strWRead.substring(strWRead.indexOf(":") + 1, strWRead.length()).trim();
                        wsta = code + ":" + (!"".equals(WSTAName) ? WSTAName : code);
                    } else if (strWRead.startsWith("@DATE")) {
                        is2 = true;
                    } else if (strWRead.startsWith("@  DATE")) {
                        is4 = true;
                    } else if (strWRead.startsWith("@START")) {
                        isCli = true;
                    } else if (strWRead.startsWith("@YRDAY")) {
                        isR = true;
                    } else if (strWRead.startsWith("@") && strWRead.contains("INSI")) {
                        isInsi = true;
                    } else if (is2) {
                        wsta += ":" + strWRead.substring(0, 2) + ":" + number + ":" + fullCode + ":" + insi + "^File: " + file.getName() + ", Line: " + line;
                        weatherList.add(wsta);
                        is2 = false;
                    } else if (is4) {
                        wsta += ":" + strWRead.substring(0, 4) + ":" + number + ":" + fullCode + ":" + insi + "^File: " + file.getName() + ", Line: " + line;
                        weatherList.add(wsta);
                        is4 = false;
                    } else if (isCli) {
                        number = strWRead.substring(8, 13).trim();
                        wsta += ":" + strWRead.substring(0, 6).trim() + ":" + number + ":" + fullCode + ":" + insi + "^File: " + file.getName() + ", Line: " + line;
                        weatherList.add(wsta);
                        isCli = false;
                    } else if (isR) {
                        number = fullName.substring(6, 8).trim();
                        wsta += ":" + fullName.substring(4, 6).trim() + ":" + number + ":" + fullCode + ":" + insi + "^File: " + file.getName() + ", Line: " + line;
                        weatherList.add(wsta);
                        isR = false;
                    } 
                    else if (isInsi) {
                        insi = strWRead.substring(0, Math.min(7, strWRead.length() - 1)).trim() + "^File: " + file.getName() + ", Line: " + line;
                        isInsi = false;
                    }

                    line++;
                }
            }
        }
        return weatherList;
    }
}
