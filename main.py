#!/usr/bin/env python
# -*- coding: utf-8 -*-


from kivy.config import Config
Config.set('graphics', 'width', '500')
Config.set('graphics', 'height', '900')
Config.set('kivy', 'log_level', 'debug')

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.layout import Layout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.properties import ObjectProperty
from kivy.uix.label import Label
from kivy.uix.button import Button 
from kivy.uix.dropdown import DropDown
from kivy.uix.textinput import TextInput


from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.core.text.markup import MarkupLabel

from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.recycleboxlayout import RecycleBoxLayout

from kivy.properties import ListProperty, BooleanProperty


from kivy.clock import Clock, _default_time as time

from kivy.utils import get_color_from_hex

from functools import partial
import threading
import unicodedata

from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.floatlayout import FloatLayout
#Window.clearcolor = (.8, .8, .8, 1)

from kivy.core.window import Window
Window.softinput_mode = 'below_target'

import nexusAPI as api
#import irc

__version__ = "0.1"

#Builder.load_file('C:\\Users\\ckswi\\Google Drive\\Nexus\\nexusApp\\nexus.kv') #LAPTOP
#Builder.load_file('C:\Users\CWPC\Google Drive\Nexus\nexusApp\nexus.kv') #PC


#Searches for a string in a list of lists as the first element of the sublists
def find_in(string,lists):
    for list in lists:
        if string == list[0]:
            return list

#Searches for a string in a dict of lists of lists as the first element of the sublists
def find_in_in(string,listss):
    for type, lists in listss.iteritems():
        for list in lists:
            if list:
                if string == list[0]:
                    return list,type
                    
#Stupid function that mimics find_in_in but due to lack of consistency in data structures is necessary
def find_in_in_stupid(string,listss):
    print('string')
    for type, lists in listss.iteritems():
        for list in lists:
            if list:
                if string == list['text']:
                    print(list,type)
                    return list,type
                    







class Holder(BoxLayout):
    #IDs for Stat bar
    refresh = ObjectProperty(None)
    name = ObjectProperty(None)
    ap = ObjectProperty(None)
    hp = ObjectProperty(None)
    mp = ObjectProperty(None)
    mo = ObjectProperty(None)
    level = ObjectProperty(None)
    log = ObjectProperty(None)
    status = ObjectProperty(None)
    
    tabs = ObjectProperty(None)
    
    #IDs for Inventory panel
    item_context = ObjectProperty(None)
    inv_cont = ObjectProperty(None)
    
    #IDs for Target panel
    target_pane = ObjectProperty(None)
    reload_context = ObjectProperty(None)
    weapon_dropdown = ObjectProperty(None)
    charge_dropdown = ObjectProperty(None)
    
    #IDs for actions page page
    action_pane = ObjectProperty(None)
    default_action_pane= ObjectProperty(None)
    
    #IDs for skill page
    ability_cont = ObjectProperty(None)
    
    #IDs for Map panel
    map_pane = ObjectProperty(None)
    tile_contents = ObjectProperty(None)
    current_location = ObjectProperty(None)
    
    #IDs for message panel
    message_input = ObjectProperty(None)
    message_pane = ObjectProperty(None)

    #IDs for bottom panel
    target_label = ObjectProperty(None)
    item_label = ObjectProperty(None)
    weapon_label = ObjectProperty(None)
    
    #Function panel
    function_pane = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super(Holder, self).__init__(**kwargs)
   
        self.weapon = ''
        self.target = ''
        self.item = ''
        self.charge = ''
        
        #Make the map, add the movement buttons. Should deal with jumping abilities eventually
        for i in range(25):
            btn = MapButton(text=(''),id=str(i))
            if i in [6,7,8]:
                btn.bind(on_press=partial(self.move,i-5))
            if i in [11,13]:
                btn.bind(on_press=partial(self.move,i-7))
            if i in [16,17,18]:
                btn.bind(on_press=partial(self.move,i-9))
            self.map_pane.add_widget(btn)
            if i == 12:
                btn.bind(on_press=partial(self.door,'alternate'))

        #Do an initial page load
        self.c_dat = api.ref_force()
        self.access_api(api.page_load)
        self.need_ref = True
        
        #Set the GUI to update from the data every .1 seconds
        Clock.schedule_interval(self.update_gui, .1)
        
        self.irc_log = [{'viewclass':'ContactItem',
                        'index':0,"height":30,
                        "message_time":'Time',
                        'message_text':'Message'}
                        ]
        # self.ids.irc_pane.data  = self.irc_log

    

   
            
    #Force a complete data update
    def refresh_data(self):
        self.access_api(partial(api.ref_force))
        self.need_ref = True

    
    #This should just update the not currently open screen out of map and inventory
    def refresh_quick(self):
        print('doing quick refresh')
        self.access_api(partial(api.ref_both))
        self.need_ref = True
        print('quick refresh complete')
        
    def update_gui(self,clock):
        if self.need_ref == True and not self.t.is_alive():
            self.refresh.color = (0,1,0,1)
            self.need_ref = False
            self.c_dat = api.get_c_dat()
            if not self.c_dat['connection']:
                self.refresh.color = (1,.75,0,1)
                self.log.text = "!!Internet failure!!"
                return
                
            print('updating gui')
            if self.c_dat['connected']:
                print('working on stats')
                #Refresh the stats
                self.name.text = self.c_dat['name']
                self.ap.text = self.c_dat['ap']
                self.hp.text = self.c_dat['hp']
                self.mp.text = self.c_dat['mp']
                self.mo.text = self.c_dat['mo']
                
                #refresh the upper message logs
                print('working on messages')
                if self.c_dat['error']:
                    self.log.text = self.c_dat['error']
                else:
                    self.log.text = self.c_dat['log'][0].split('- ')[1]
                self.status.text = self.c_dat['status']
                
                #Print some basic tile contents on the map page
                t = self.c_dat['targets']
                f = 1#len(t['faction'])
                a = 1#len(t['ally']) + len(t['friendly'])
                h = 1#len(t['neutral']) + len(t['hostile']) + len(t['enemy'])
                target_text = ('Factionmates: %s, friendlies: %s, precious violence recipients: %s' % (f,a,h))
                if self.c_dat['faction_tile']:
                    target_text = target_text +'\nFaction Stronghold of '+self.c_dat['faction_tile']
                self.tile_contents.text = target_text

                    
                
                print('working on map') 
                #Fill the map data
                for c in self.map_pane.children:
                    if len(self.c_dat['map']) == 0:
                        print('skipping map')
                        continue
                    i = c.id
                    tile_data = self.c_dat['map'][int(i)]
                    tiletext = [tile_data['type']]
                    for key,value in tile_data.items():
                        if value == True:
                            tiletext.append(key)
                    tiletext = '\n'.join(tiletext)
                    c.text = tiletext
                    c.background_color = background_color = get_color_from_hex(tile_data['color'])
                
                
                print('working on messages')
                #Populate the message panel
                self.message_pane.text = self.c_dat['log'][0]
                
                
                
                
                
                #This stuff only needs to happen if you're alive
                if self.c_dat['hp'] != '0':

                    #Run the Inventory adapter
                    print('Working on inventory')
                    if self.c_dat['inv_trim']:
                        self.inv_cont.set_data([{'label':i[0], 'quantity':i[2], 'weight':i[3], 'item_id':i[4]} for i in self.c_dat['inv_trim']])

                    
                    #restock the skills
                    print('working on skills')
                    self.ability_cont.set_data(self.c_dat['abilities'])

                    
                    print('working on targets')
                    #Stock the target list
                    self.target_pane.set_data(self.c_dat['targets']+self.c_dat['pets'])

                    #Add the current location
                    self.current_location.text = self.c_dat['location']
                    
                    
                    print('working on dropdowns')
                    #Populate the weapon dropdown
                    if self.c_dat['weapons']:
                        vals = []
                        for w in self.c_dat['weapons']:
                            vals.append(w[0])
                        self.weapon_dropdown.values=vals
                        
                    #Populate the charge attack dropdown    
                    vals = ['None']
                    for w in self.c_dat['charges']:
                        vals.append(w[0])            
                    self.charge_dropdown.values=vals
                    


                    print('working on actions')
                    #Put stuff in the action pane, if necessary. Not going to listify this, since it should be a very small performance toll
                    self.ids['action_pane'].clear_widgets()
                    #Put in the portals
                    for portal in self.c_dat['portals']:
                        btn = FillButton(text=portal[0],on_press=partial(self.portal,portal))
                        self.action_pane.add_widget(btn)
                    for flag_recap in self.c_dat['flag_recap']:
                        btn = FillButton(text=flag_recap[1],on_press=partial(self.flag_recap,flag_recap[0]))
                        self.action_pane.add_widget(btn)
                    if self.c_dat['flag_capture']:
                        btn = FillButton(text='Capture Standard',on_press=self.flag_cap)
                        self.action_pane.add_widget(btn)
                        
                else:
                    self.ids.action_pane.clear_widgets()
                    self.action_pane.add_widget(FillButton(text = 'Respawn',on_press=self.respawn))
                    self.tabs.switch_to(self.ids.act_tab)

                    
                    
                #Change the colour of tabs with interesting things in them
                #if self.c_dat['targets']['enemy'] or self.c_dat['targets']['hostile'] or self.c_dat['targets']['neutral']:
                #    self.ids.target_tab.background_color = (1,0,0,1)
                #else:
                #    self.ids.target_tab.background_color = (1,1,1,1)
                    
                    
                
                    
                    
            #If not connected to a character, make the character list on the functions page
            elif self.c_dat['screen'] == 'char_page':
                self.tabs.switch_to(self.ids.func_tab)
                self.name.text = "Pick char @ func tab"
                self.function_pane.clear_widgets()
                self.function_pane.cols = 1

                self.char_list = api.get_char_list()
                for c in self.char_list:
                    btn = ClipButton(text = c[0])
                    btn.bind(on_press=partial(self.connect_character,c[9]))
                    box = BoxLayout()
                    d_vals = {1:(1,1,1,1),2:(0,1,0,1),3:(1,0,0,1),4:(.4,.5,.95,1)}
                    for key, val in d_vals.items():
                        label = ClipLabel(text=c[key],color=val)
                        if key ==1:
                            label.size_hint_x = .5
                        else:
                            label.size_hint_x = .5/3
                        box.add_widget(label)
                    self.function_pane.add_widget(btn)
                    self.function_pane.add_widget(box)
            elif self.c_dat['screen'] == 'login':
                self.tabs.switch_to(self.ids.func_tab)
                self.name.test = "login @ func tab"
                self.function_pane.clear_widgets()
                self.function_pane.cols = 2
                self.function_pane.add_widget(Label(text='username'))
                self.un_input = MyTextInput(multiline=False)
                self.function_pane.add_widget(self.un_input)
                self.function_pane.add_widget(Label(text='password'))
                self.pw_input = MyTextInput(multiline=False,password=True)
                self.function_pane.add_widget(self.pw_input)
                btn = Button(text='Login')
                btn.bind(on_press=self.login)
                self.function_pane.add_widget(btn)
                
            print('done refreshing gui')
        
    
    

    
    def access_api(self,function):
        self.refresh.color = (1,0,0,1)
        try:
            if not self.t.is_alive():
                self.t = threading.Thread(target= function)
                self.t.start()
            else:
                Clock.schedule_once(self.access_api(function),.1) #This queues up to one action. Not ideal.
        except:
            self.t = threading.Thread(target= function)
            self.t.start()
        self.need_ref = True
        
###Callbacks that must interface with the api
    def login(self, button):
        print('trying to log in')
        print(self.un_input.text)
        self.access_api(partial(api.login,self.un_input.text,self.pw_input.text))
        self.need_ref = True
        
        
    def connect_character(self,cID,button):
        self.access_api(partial(api.char_con,cID))
        self.need_ref = True
       
        
    def disconnect_character(self):
        print('attempting to disconnect')
        self.access_api(partial(api.char_dis))
        self.need_ref = True
       
        
    def respawn(self,button):
        self.access_api(partial(api.respawn))
        self.need_ref = True
       
    
    def move(self,dir,button):
        print('moving begins')
        self.access_api(partial(api.move,dir))

        print('moving ends, refreshing gui')
        
    def portal(self, pID, button):
        self.access_api(partial(api.portal,pID))
        self.need_ref = True
    
    ###Combat stuff###
    def set_target(self,target_id, target_name):
        self.target = target_id
        self.target_label.text = 't:'+target_name 

        
    def set_charge(self,c):
        if c == "None" or c == "Charges":
            self.charge = ''
        else:
            self.charge = c

    def attack(self):
        if self.weapon and self.target:
            if self.charge:
                self.access_api(partial(api.attack,self.target,self.weapon,self.charge))
            else:
                self.access_api(partial(api.attack,self.target,self.weapon))
        self.need_ref = True

    #These are set via spinners. This requires checking against the dictionaries.
    def set_weapon(self,w):
        for x in self.c_dat['weapons']:
            if x[0]==w:
                self.weapon =  x[1]
                self.weapon_label.text = 'w-%s' % x[0]
                break
    
    def reload(self):
        reload_context = self.reload_context.text
        if reload_context == "Reload":
            if self.weapon:
                self.access_api(partial(api.reload,self.weapon))

        if reload_context == "Rocks":
            iID = 'rock'
            print('trying to rocks')
            self.access_api(partial(api.pickup,iID))
        if reload_context == "Weapon":
            iID = self.weapon
            self.access_api(partial(api.pickup,iID))
        if reload_context == "All":
            iID = 'all'
            self.access_api(partial(api.pickup,iID))
        #Other contextually useful buttons?
        self.need_ref = True
               
        
    def reload_weapon(self,w,button):
        self.access_api(partial(api.use,w[1]))
        self.need_ref = True
    
    #Item stuff
    def set_item(self, item_id, label):
        self.item = item_id
        self.item_label.text = 'i:' + label

        
    
    def use(self):
        self.access_api(partial(api.use,self.item))
        self.need_ref = True
        
        
    def item_context_go(self):
        item_context = self.item_context.text
        if item_context == "Give":
            self.access_api(partial(api.give,self.target,self.item))

        if item_context == "Drop":    
            self.access_api(partial(api.drop,self.item))

        if item_context == "Safe":
            self.access_api(partial(api.safe_place,self.item))
        
        if item_context == "Locker":
            self.access_api(partial(api.locker_place,self.item))
        
        if item_context == "Reload":
            self.access_api(partial(api.reload,self.item))
            
        if item_context == "Set Up":
            self.access_api(partial(api.placeitem,self.item))
        self.need_ref = True


       
        
    #Skills stuff
    def use_ability(self, ability_id, ability_type):
        if ability_type == 'skill':
            self.access_api(partial(api.useSkill, ability_id))
        if ability_type in ['cast', 'trigger']:
            self.access_api(partial(api.castSpell, ability_id))
    
    
    #ACTIONS stuff
    def door(self,action,button = 0):
        print(action)
        self.access_api(partial(api.door,action))
        self.need_ref = True
        
        
    
    def search(self):
        self.access_api(partial(api.search,))
        self.need_ref = True
    
    def hide(self):
        api.hide()
        self.need_ref = True
    
    def say(self,text,mode=0):
        if mode:
            self.access_api(partial(api.say,text,self.target))
        else:
            self.access_api(partial(api.say,text))
        self.message_input.text = ''
        self.need_ref = True
    
    
    def flag_recap(self,id,button):
        self.access_api(partial(api.flag_recap,id))
        self.need_ref = True
        
    def flag_cap(self,button):
        api.flag_cap()
    

#%% Inventory business

class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior,
                                 RecycleBoxLayout):
    ''' Adds selection and focus behaviour to the view. '''


class InvLabel(RecycleDataViewBehavior, GridLayout):
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)
    cols = 3

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        self.label_text = data['label']
        self.quantity_text = data['quantity']
        self.weight_text = data['weight']
        self.item_id = data['item_id']
        return super(InvLabel, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_up(self, touch):
        ''' Add selection on touch down '''
        if super(InvLabel, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected
        if is_selected:
            App.get_running_app().root.set_item(self.item_id, self.label_text)
        

class TargetLabel(RecycleDataViewBehavior, GridLayout):
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)
    relationship_color_map = {'faction':(0,0,0,1),
                              'ally': (),
                              'neutral': (),
                              'hostile': (),
                              'enemy':()}
    bcolor = ListProperty([0,0,0,1])
    cols = 4

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        self.name_text = data['name']
        self.level_text = data['level']
        self.hp_text = data['hp']
        self.mp_text = data['mp']
        self.character_id = data['char_id']
        self.relationship = data['relationship']
        
        return super(TargetLabel, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_up(self, touch):
        ''' Add selection on touch down '''
        if super(TargetLabel, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected
        if is_selected:
            App.get_running_app().root.set_target(self.character_id, self.name_text)

class AbilityLabel(RecycleDataViewBehavior, GridLayout):
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(False)
    bcolor = ListProperty([0,0,0,1])
    cols = 2

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        self.name_text = data['text']
        self.type_text = data['ability_type'].title()
        self.ability_id = data['id']
        
        return super(AbilityLabel, self).refresh_view_attrs(
            rv, index, data)
    
    def on_touch_up(self, touch):
        ''' Add selection on touch down '''
        if super(AbilityLabel, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos):
            App.get_running_app().root.use_ability(self.ability_id, self.ability_type)
            return self.parent.select_with_touch(self.index, touch)


class InvRV(RecycleView):
    def __init__(self, **kwargs):
        super(InvRV, self).__init__(**kwargs)
        self.data = []

    def set_data(self, data):
        self.data = self.data = data 


class TargetRV(RecycleView):
    def __init__(self, **kwargs):
        super(TargetRV, self).__init__(**kwargs)
        self.data = []

    def set_data(self, data):
        self.data = self.data = data 


class AbilityRV(RecycleView):
    def __init__(self, **kwargs):
        super(AbilityRV, self).__init__(**kwargs)
        self.data = []

    def set_data(self, data):
        self.data = self.data = data 
    
#These are custom kivy classes    
class Tabbable(TabbedPanel):
    pass
class ClipLabel(Label):
    pass
class ClipButton(Button):
    pass
class FillLabel(Label):
    pass
class FillButton(Button):
    pass
class MapButton(Button):
    pass
class MessageLabel(Label):
    pass
class LoginGridLayout(GridLayout):
    pass
class SpinnerOption(Button):
    pass
class MyTextInput(TextInput):
    pass
    
    
###Build the app###

class NexusApp(App):
    def on_pause(self):
        # Here you can save data if needed
        return True

    def on_resume(self):
        # Here you can check if any data needs replacing (usually nothing)
        pass
      
    def build(self):
        global holder
        holder = Holder()
        return holder
    
###Run The application###
if __name__ == '__main__':
    NexusApp().run()
    
    

