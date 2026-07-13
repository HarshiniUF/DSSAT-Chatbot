package xbuild.Components;

import java.awt.Color;
import javax.swing.InputVerifier;
import javax.swing.JComponent;
import javax.swing.JTextField;

/**
 *
 * @author JAZZJAIKLA
 */
public class InputNumberVerifier extends InputVerifier {

    @Override
    public boolean verify(JComponent input) {
        JTextField field = (JTextField) input;
        String text = field.getText();
        boolean result = true;
        
        if (!"".equals(text)) {
            try {
                Float value = Float.valueOf(text);
                result = value >= 0 || value == -99;
            } catch (NumberFormatException e) {
                result = false;
            }
        }
        
        if(result){
            field.setForeground(Color.BLACK);
        }
        else{
            field.setForeground(Color.RED);
        }
        
        return result;
    }
    
}
