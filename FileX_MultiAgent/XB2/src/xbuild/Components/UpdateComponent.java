/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package xbuild.Components;

import DSSATModel.ExperimentType;
import Extensions.Utils;
import java.lang.reflect.Field;
import java.util.ArrayList;
import java.util.Date;
import java.util.logging.Level;
import java.util.logging.Logger;
import xbuild.Events.FieldUpdateEvent;
import xbuild.Events.XEventListener;

/**
 *
 * @author Jazz
 */
public class UpdateComponent {
    private static ArrayList<XEventListener> eventListeners;
    
    public static void setEventListener(XEventListener eventListener){
        if (UpdateComponent.eventListeners == null) {
            UpdateComponent.eventListeners = new ArrayList<>();
        }
        for(int i = UpdateComponent.eventListeners.size(); i > 1;i--){
            UpdateComponent.eventListeners.remove(i - 1);
        }
        
        UpdateComponent.eventListeners.add(eventListener);
    }
    
    public static void updateModel(Object component,Object model, String fieldName, Object value){
        Field field = null;
        try {
            field = model.getClass().getDeclaredField(fieldName);
        } catch (NoSuchFieldException | SecurityException ex) {
            Logger.getLogger(UpdateComponent.class.getName()).log(Level.SEVERE, null, ex);
        }

        if(field != null){
            field.setAccessible(true);
            try {
                if(field.getType() == Float.class && (field.get(model) != null || value != null)){
                    if(field.get(model) != Utils.ParseFloat(value)){
                        field.set(model, Utils.ParseFloat(value));
                        //eventListener.myAction(new FieldUpdateEvent(component));
                        publishEvents(component);
                    }
                }
                else if(field.getType() == Integer.class && (field.get(model) != null || value != null)){
                    if(field.get(model) != Utils.ParseInteger(value)){
                        field.set(model, Utils.ParseInteger(value));
                        //eventListener.myAction(new FieldUpdateEvent(component));
                        publishEvents(component);
                    }
                }
                else if(field.getType() == ExperimentType.class && (field.get(model) != null || value != null)){
                    if(field.get(model) != ExperimentType.valueOf(value.toString())){
                        field.set(model, ExperimentType.valueOf(value.toString()));
                        //eventListener.myAction(new FieldUpdateEvent(component));
                        publishEvents(component);
                    }
                }
                else if(field.getType() == Date.class && (field.get(model) != null || value != null)){
                    if(field.get(model) != value)
                    {
                        field.set(model, value);
                        publishEvents(component);
                    }
                }
                else{ 
                    if((field.get(model) != null && !field.get(model).equals(value) || (field.get(model) == null && value != null && !"".equals(value)))){
                        field.set(model, value);
                        //eventListener.myAction(new FieldUpdateEvent(component));
                        publishEvents(component);
                    }
                }
            } catch (IllegalArgumentException | IllegalAccessException ex) {
                Logger.getLogger(UpdateComponent.class.getName()).log(Level.SEVERE, null, ex);
            }
        }
    }
    
    private static void publishEvents(Object component){
        
        for(int i = 0;i < UpdateComponent.eventListeners.size(); i++){
            UpdateComponent.eventListeners.get(i).myAction(new FieldUpdateEvent(component));
        }
    }
}
