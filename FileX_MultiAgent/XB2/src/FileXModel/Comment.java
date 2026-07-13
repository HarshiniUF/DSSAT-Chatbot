package FileXModel;

public class Comment {
    public int level;
    public Section section;
    public String description;
    
    public Comment(int level, Section section, String description){
        this.level = level;
        this.section = section;
        this.description = description;
    }
}
