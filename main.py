#!/usr/bin/env python
# -*- coding: utf-8 -*-


from kivy.config import Config
Config.set('graphics', 'width', '500')
Config.set('graphics', 'height', '900')

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
from kivy.uix.listview import (ListView, ListItemButton, ListItemLabel,
                               CompositeListItem)
from kivy.adapters.dictadapter import DictAdapter

from kivy.core.text.markup import MarkupLabel

from kivy.garden.recycleview import RecycleView
from kivy.properties import ListProperty


from kivy.clock import Clock, _default_time as time

from kivy.utils import get_color_from_hex

from functools import partial
import threading
import unicodedata

from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.floatlayout import FloatLayout
#Window.clearcolor = (.8, .8, .8, 1)

import nexusAPI as api
import irc

__version__ = "0.0.4"

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
                    

def join_adapter_dict(dict1,dict2):
    #should only join in the case where there are actual things to join.
    if len(dict1)==1:
        dict1 = {}
    if len(dict2)==1:
        dict2 = {}
    sep = len(dict1)
    for i in range(len(dict2)):
        dict1[str(i+sep)] = dict2[str(i)]
    return dict1
    
def inv_to_dict_adapter(inv):
    inv_dict = {}
    inv_ints = range(len(inv))
    for i in inv_ints:
        item = inv[i]
        item_dict = {
                    'text':item[0],
                    'qty':item[2],
                    'wgt':item[3],
                    'id':item[4],
                    'is_selected':False
                    }
        inv_dict[str(i)] = item_dict
        

    inv_ints = ["{0}".format(index) for index in range(len(inv))]

    
    inv_args_converter = lambda row_index, item: \
        {'text': item['text'],
         'size_hint_y': None,
         'height': 35,
         'cls_dicts': [{'cls': InvListButton,
                        'kwargs': {'text': item['text'],'size_hint_x':.8}},
                       {'cls': InvListLabel,
                        'kwargs': {'text': item['qty'],'size_hint_x':.1}},
                       {'cls': InvListLabel,
                        'kwargs': {'text': item['wgt'],'size_hint_x':.1}}
                        ]}
                        
    inv_dict_adapter = DictAdapter(sorted_keys=inv_ints,
                               data=inv_dict,
                               args_converter=inv_args_converter,
                               selection_mode='single',
                               propagate_selection_to_data=True,
                               cls=CompositeListItem)
    
    return inv_dict_adapter

def targets_to_dict_adapter(objects,target_lists):
    targets_dict = {}
    

    head = {'text':'Objects','lvl':'','hp':'','mp':'','is_selected':False}
    targets_dict['0'] = head
    i=0
    for object,value in objects.iteritems():
        print (object,value)
        if value:
            i=i+1
            print(i)
            object_dict = {
                            'text':object,
                            'lvl':'',
                            'hp':'',
                            'mp':'',
                            'is_selected':False
                            }
            targets_dict[str(i)] = object_dict
        
    
    
    for rel,target_list in target_lists.iteritems():
        rel_dict = {}
        head = {'text':rel,'lvl':'','hp':'','mp':'','is_selected':False}
        rel_dict['0'] = head
        for i in range(len(target_list)):
            target = target_list[i]
            target_dict = {
                        'text':target[0],
                        'lvl':target[2],
                        'hp':target[3],
                        'mp':target[4],
                        'is_selected':False
                        }
            rel_dict[str(i+1)] = target_dict
        if not targets_dict:
            targets_dict = rel_dict
            
        else:
            targets_dict = join_adapter_dict(targets_dict,rel_dict)

    
    target_ints = ["{0}".format(index) for index in range(len(targets_dict))]
    

    
    target_args_converter = lambda row_index, target: \
        {'text': target['text'],
         'size_hint_y': None,
         'height': 35,
         'cls_dicts': [{'cls': InvListButton,
                        'kwargs': {'text': target['text'],'size_hint_x':.7}},
                       {'cls': InvListLabel,
                        'kwargs': {'text': target['lvl'],'size_hint_x':.1}},
                       {'cls': InvListLabel,
                        'kwargs': {'text': target['hp'],'color':(1,0,0,1),'size_hint_x':.1}},
                       {'cls': InvListLabel,
                        'kwargs': {'text': target['mp'],'color':(.4,.5,.95,1),'size_hint_x':.1}}
                        ]}
                        
    target_dict_adapter = DictAdapter(sorted_keys=target_ints,
                               data=targets_dict,
                               args_converter=target_args_converter,
                               selection_mode='single',
                               propagate_selection_to_data=True,
                               cls=CompositeListItem)

    return target_dict_adapter

def abilities_to_dict_adapter(ability_lists):
    ability_dict = {}

    for type,ability_list in ability_lists.iteritems():
        type_dict = {}
        head = {'text':type,'lvl':'','hp':'','mp':'','is_selected':False}
        type_dict['0'] = head
        for i in range(len(ability_list)):
            ability = ability_list[i]
            ability['is_selected'] = False
            type_dict[str(i+1)] = ability
            
        if not ability_dict:
            ability_dict = type_dict
        else:
            ability_dict = join_adapter_dict(ability_dict,type_dict)

    
    ability_ints = ["{0}".format(index) for index in range(len(ability_dict))]
    

    
    ability_args_converter = lambda row_index, ability: \
        {'text': ability['text'],
         'size_hint_y': None,
         'height': 45,
         'cls_dicts': [{'cls': InvListButton,
                        'kwargs': {'text': ability['text'],'size_hint_x':.85}},
                       {'cls': InvListLabel,
                        'kwargs': {'text': ability['mp'],'color':(.4,.5,.95,1),'size_hint_x':.15}}
                        ]}
                        
    ability_dict_adapter = DictAdapter(sorted_keys=ability_ints,
                               data=ability_dict,
                               args_converter=ability_args_converter,
                               selection_mode='single',
                               propagate_selection_to_data=True,
                               cls=CompositeListItem)

    return ability_dict_adapter




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
    ability_pane = ObjectProperty(None)
    
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

        #Do an initial page load
        self.access_api(api.ref_force)
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
                    self.log.text = self.c_dat['log'].split('- ')[1]
                self.status.text = self.c_dat['status']
                
                #Print some basic tile contents on the map page
                t = self.c_dat['targets']
                f = len(t['faction'])
                a = len(t['ally']) + len(t['friendly'])
                h = len(t['neutral']) + len(t['hostile']) + len(t['enemy'])
                self.tile_contents.text = ('Factionmates: %s, friendlies: %s, precious violence recipients: %s' % (f,a,h))

                    
                    
                print('working on map') 
                #Fill the map data
                for c in self.map_pane.children:
                    i = c.id
                    tile_data = self.c_dat['map'][int(i)]
                    tiletext = [tile_data['type']]
                    for key,value in tile_data.iteritems():
                        if value == True:
                            tiletext.append(key)
                    tiletext = '\n'.join(tiletext)
                    c.text = tiletext
                    c.background_color = background_color = get_color_from_hex(tile_data['color'])
                
                
                print('working on messages')
                #Populate the message panel
                self.message_pane.text = self.c_dat['log']
                
                
                
                
                
                #This stuff only needs to happen if you're alive
                if self.c_dat['hp'] != '0':

                    #Run the Inventory adapter
                    print('Working on inventory')
                    inv_dict_adapter = inv_to_dict_adapter(self.c_dat['inv_trim'])
                    inv_dict_adapter.bind(on_selection_change = self.set_item)
                    self.inv_cont.adapter = inv_dict_adapter

                    
                    #restock the skills
                    print('working on skills')
                    abilities_adapter = abilities_to_dict_adapter(self.c_dat['abilities'])
                    abilities_adapter.bind(on_selection_change = self.use_ability)
                    self.ability_pane.adapter = abilities_adapter
                    
                    print('working on targets')
                    #Stock the target list
                    targets_adapter = targets_to_dict_adapter(self.c_dat['objects'],self.c_dat['targets'])
                    targets_adapter.bind(on_selection_change = self.set_target)
                    self.target_pane.adapter = targets_adapter
                                

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
                else:
                    self.ids.action_pane.clear_widgets()
                    self.action_pane.add_widget(FillButton(text = 'Respawn',on_press=self.respawn))
                    self.tabs.switch_to(self.ids.act_tab)

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
                    dict = {1:(1,1,1,1),2:(0,1,0,1),3:(1,0,0,1),4:(.4,.5,.95,1)}
                    for key, val in dict.iteritems():
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
                self.un_input = TextInput(multiline=False)
                self.function_pane.add_widget(self.un_input)
                self.function_pane.add_widget(Label(text='password'))
                self.pw_input = TextInput(multiline=False,password=True)
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
                Clock.schedule_once(access_api(function),.1) #This queues up to one action. Not ideal.
        except:
            self.t = threading.Thread(target= function)
            self.t.start()
        self.need_ref = True
        
###Callbacks that must interface with the api
    def login(self, button):
        print('trying to log in')
        print(self.un_input.text)
        self.access_api(partial(api.login,self.un_input.text,self.pw_input.text))
        self.refresh_quick()
        
        
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
    def set_target(self,adapter):
        if adapter.selection:
        
            if adapter.selection[0].text in ['ward','fort','door']:
                self.target = adapter.selection[0].text
                print "attacking " + adapter.selection[0].text
                self.target_label.text = 't:'+adapter.selection[0].text
            elif adapter.selection[0].text not in self.c_dat['targets'].keys():
                target_data,rel = find_in_in(adapter.selection[0].text, self.c_dat['targets'])
                if target_data:
                    self.target = target_data[1]
                    self.target_label.text = 't:'+target_data[0]
    

        
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
    def set_item(self,adapter):
        if adapter.selection:
            item_data = find_in(adapter.selection[0].text, self.c_dat['inv_trim'])
            self.item = item_data[4]
            self.item_label.text = 'i:'+item_data[0]


        
    
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
    def use_ability(self,adapter):
        if adapter.selection:
            if adapter.selection[0].text not in self.c_dat['abilities'].keys():
                ability_data,type = find_in_in_stupid(adapter.selection[0].text, self.c_dat['abilities'])
                if ability_data:
                    print(type)
                    if type == 'skills':
                        self.access_api(partial(api.useSkill,ability_data['id']))
                    elif type in ['cast','trigger']:
                        self.access_api(partial(api.castSpell,ability_data['id']))
        self.need_ref = True
    
    #ACTIONS stuff
    def door(self,action):
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
    
    def irc_connect(self):
        self.irc_nickname = self.ids.irc_nickname_input.text.encode('utf-8')
        self.irc_channel = self.ids.irc_channel_input.text.encode('utf-8')
        Clock.schedule_interval(self.irc_update, .5)
        irc.initialise(self.irc_nickname,self.irc_channel)
        self.ids.irc_connect.clear_widgets()
        self.ids.irc_connect.parent.remove_widget(self.ids.irc_connect)
        
    def irc_update(self,clock):
        try:
            new_messages = irc.p.get_message_log()
        except:
            new_messages = []
        if new_messages:
            for m in new_messages:
                print(m)
                message_dict = {'viewclass':'ContactItem'}
                message_dict['message_time'] = m[0]
                message_dict['message_text'] = m[1]
                message_dict['index'] = self.irc_log[-1]['index']+1
                self.irc_log.append(message_dict)
            self.ids.irc_pane.data  = self.irc_log
        self.ids.irc_pane.scroll_y = 0
        
        
    def irc_say(self):

        msg = self.ids.irc_input.text
        irc.p.send_message(msg)
        
    
    
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
class InvGridLayout(GridLayout):
    pass
class InvListButton(ListItemButton):
    pass
class InvListLabel(ListItemLabel):
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
        return Holder()
    
###Run The application###
if __name__ == '__main__':
    NexusApp().run()
    
    

