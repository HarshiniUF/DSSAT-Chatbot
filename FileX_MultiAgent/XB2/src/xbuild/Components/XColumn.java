package xbuild.Components;

/**
 *
 * @author Jazz
 */
public class XColumn {
    private final String fieldName;
    private final String caption;
    private final int width;
    
    public XColumn(String fieldName, String caption, int width){
        this.fieldName = fieldName;
        this.caption = caption;
        this.width = width;
    }
    
    public String getFieldName(){
        return fieldName;
    }
    
    public String getCaption(){
        return caption;
    }
    
    public int getWidth(){
        return width;
    }
}
