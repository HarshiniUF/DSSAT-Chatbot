package FileXModel;

import java.util.ArrayList;
import java.util.stream.Collectors;
import java.util.stream.Stream;


public class FileXCommentList {
    private ArrayList<Comment> comments = new ArrayList();
    
    public void addComment(int level, Section section, String description) {
        comments.add(new Comment(level, section, description));
    }
    
    public ArrayList<Comment> getAll(int level, Section section){
        Stream<Comment> s = comments.stream().filter(comment -> comment.level == level && comment.section == section);
        
        return (ArrayList<Comment>) s.collect(Collectors.toList());
    }
}
