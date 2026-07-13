/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package xbuild.Components;

/**
 *
 * @author PCMIWS04
 */
public class XComboBoxItem {
    public XComboBoxItem(String index, String item){
        this.index = index;        
        this.item = item;
    }
    public String index;
    public String item;
    
    @Override
    public String toString(){
        return item;
    }
}
