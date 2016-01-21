from kivy.config import Config
Config.set('graphics', 'width', '250')
Config.set('graphics', 'height', '450')

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

from kivy.utils import get_color_from_hex

from functools import partial

from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.floatlayout import FloatLayout
#Window.clearcolor = (.8, .8, .8, 1)

import nexusAPI as api

__version__ = "0.0.3"

#Builder.load_file('C:\\Users\\ckswi\\Google Drive\\Nexus\\nexusApp\\nexus.kv') #LAPTOP
#Builder.load_file('C:\Users\CWPC\Google Drive\Nexus\nexusApp\nexus.kv') #PC

def find_in(string,lists):
    for list in lists:
        if string == list[0]:
            return list

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
        
        
        

    
    inv_args_converter = lambda row_index, item: \
        {'text': item['text'],
         'size_hint_y': None,
         'height': 25,
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














class Holder(BoxLayout):
    #IDs for Stat bar
    name = ObjectProperty(None)
    ap = ObjectProperty(None)
    hp = ObjectProperty(None)
    mp = ObjectProperty(None)
    mo = ObjectProperty(None)
    level = ObjectProperty(None)
    log = ObjectProperty(None)
    status = ObjectProperty(None)
    
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
    skill_pane = ObjectProperty(None)
    
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
        #self.inv_cont.bind(minimum_height=self.inv_cont.setter('height'))
        #self.target_pane.bind(minimum_height=self.target_pane.setter('height'))
        
        self.weapon = ''
        self.target = ''
        self.item = ''
        self.charge = ''
        api.page_load()
        self.refresh_quick()
            
    #Force a complete data update
    def refresh_data(self):
        api.ref_force()
        self.update_gui()
        pass
    
    #This should just update the not currently open screen out of map and inventory
    def refresh_quick(self):
        print('doing quick refresh')
        api.ref_both()
        self.update_gui()
        print('quick refresh complete')
        
    def update_gui(self):
        self.c_dat = api.get_c_dat()
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
                self.log.text = self.c_dat['log'][0]
            self.status.text = self.c_dat['status']
            
            
            if self.c_dat['hp'] != '0':
            
                inv_dict_adapter = inv_to_dict_adapter(self.c_dat['inv_trim'])
                inv_dict_adapter.bind(on_selection_change = self.set_item)
                self.inv_cont.adapter = inv_dict_adapter
                

                
                
                
                #restock the skills
                self.skill_pane.clear_widgets()
                
                self.skill_pane.add_widget(ClipLabel(text='Skill',size_hint_x=.7))
                self.skill_pane.add_widget(ClipLabel(text='mp',size_hint_x=.15,halign='center'))
                
                print('working on skills')
                for s in self.c_dat['skills']:
                    btn = ClipButton(text=s,size_hint_x=.7)
                    btn.bind(on_press=partial(self.use_skill, s))
                    self.skill_pane.add_widget(btn)
                    self.skill_pane.add_widget(ClipLabel(text='??',size_hint_x=.3))
                
                print('working on spells')
                if self.c_dat['spells']:
                    if self.c_dat['spells']['cast']:
                        self.skill_pane.add_widget(ClipLabel(text='Spell (memory)',size_hint_x=.7))
                        self.skill_pane.add_widget(ClipLabel(text='mp',size_hint_x=.3,halign='center'))
                        
                        for s in self.c_dat['spells']['cast']:
                            btn = ClipButton(text=s[0],size_hint_x=.7)
                            btn.bind(on_press=partial(self.cast_spell, s))
                            self.skill_pane.add_widget(btn)
                            self.skill_pane.add_widget(ClipLabel(text=s[1],size_hint_x=.3))

                    if self.c_dat['spells']['trigger']:
                        self.skill_pane.add_widget(ClipLabel(text='Spell (trigger)',size_hint_x=.7))
                        self.skill_pane.add_widget(ClipLabel(text='mp',size_hint_x=.3,halign='center'))                
                        
                        for s in self.c_dat['spells']['trigger']:
                            btn = ClipButton(text=s[1],size_hint_x=.7)
                            btn.bind(on_press=partial(self.trigger_spell, s))
                            self.skill_pane.add_widget(btn)
                            
                            self.skill_pane.add_widget(ClipLabel(text='??',size_hint_x=.3))            
                
                print('working on targets')
                #Stock the target list
                self.target_pane.clear_widgets()
                for key, l in self.c_dat['objects'].iteritems():
                    if l:
                        btn = Button(text=key,size_hint_x = .7,on_press=(partial(self.set_target_object,key)))
                        self.target_pane.add_widget(btn)
                        self.target_pane.add_widget(Label(size_hint_x = .1))
                        self.target_pane.add_widget(Label(size_hint_x = .1))
                        self.target_pane.add_widget(Label(size_hint_x = .1))
                        

                for key, l in self.c_dat['targets'].iteritems():
                    if l:
                        self.target_pane.add_widget(Label(text=key,size_hint_x = .7))
                        self.target_pane.add_widget(Label(text = 'lvl',size_hint_x = .1))
                        self.target_pane.add_widget(Label(text = 'hp',size_hint_x = .1))
                        self.target_pane.add_widget(Label(text = 'mp',size_hint_x = .1))
                        for t in l:
                            btn = Button(text=t[0],on_press=(partial(self.set_target,t)),size_hint_x = .67)
                            lvllab = Label(text=t[2],size_hint_x = .11)
                            hplab = Label(text=t[3],size_hint_x = .11,color = (1,0,0,1))
                            mplab = Label(text=t[4],size_hint_x = .11, color = (.4,.5,.95,1))
                            
                            self.target_pane.add_widget(btn)
                            self.target_pane.add_widget(lvllab)
                            self.target_pane.add_widget(hplab)
                            self.target_pane.add_widget(mplab)
                            
                print('working on map')        
                #Make the map
                self.map_pane.clear_widgets()
                i=0
                for t in self.c_dat['map']:
                    i=i+1
                    #Temporary tile info will just be text
                    tiletext = [t['type']]
                    for key, value in t.iteritems():
                        if value == True:
                            tiletext.append(key)
                    tiletext = ','.join(tiletext)
                    btn = MapButton(text=(tiletext),background_color = get_color_from_hex(t['color']))
                    self.c_dat['leap']=False
                    if self.c_dat['leap']:
                        do='nothing'
                    else:
                        if i in [7,8,9]:
                            btn.bind(on_press=partial(self.move,i-6))
                        if i in [12,14]:
                            btn.bind(on_press=partial(self.move,i-8))
                        if i in [17,18,19]:
                            btn.bind(on_press=partial(self.move,i-10))
                        
                        
                    self.map_pane.add_widget(btn)
                    
                #Add the current location
                self.current_location.text = self.c_dat['location']
                
                #Print some basic tile contents on the map page
                t = self.c_dat['targets']
                f = len(t['faction'])
                a = len(t['ally']) + len(t['friendly'])
                h = len(t['neutral']) + len(t['hostile']) + len(t['enemy'])
                self.tile_contents.text = ('Factionmates: %s, friendlies: %s, precious violence recipients: %s' % (f,a,h))
                
                print('working on dropdowns')
                #Populate the weapon dropdown
                if self.c_dat['weapons']:
                    vals = []
                    for w in self.c_dat['weapons']:
                        vals.append(w[0])
                    self.weapon_dropdown.values=vals
                    
                #Populate the charge attack dropdown    
                if self.c_dat['charges']:
                    vals = ['None']
                    for w in self.c_dat['charges']:
                        vals.append(w[0])            
                    self.charge_dropdown.values=vals
                
                print('working on messages')
                #Populate the message panel
                self.message_pane.clear_widgets()
                for m in self.c_dat['log']:
                    self.message_pane.add_widget(MessageLabel(text=m))
                    
                print('working on actions')
                #Put stuff in the action pane, if necessary
                self.ids['action_pane'].clear_widgets()
                #Put in the portals
                for portal in self.c_dat['portals']:
                    btn = FillButton(text=portal[0],on_press=partial(self.portal,portal))
                    self.action_pane.add_widget(btn)
                
            else:
                self.ids['action_pane'].clear_widgets()
                self.ids['action_pane'].add_widget(FillButton(text = 'Respawn',on_press=self.respawn))

        #If not connected to a character, make the character list on the functions page
        elif self.c_dat['screen'] == 'char_page':
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
            self.name.test = "login @ func tab"
            self.function_pane.clear_widgets()
            self.function_pane.cols = 2
            self.function_pane.add_widget(Label(text='username'))
            self.un_input = TextInput(multiline=False)
            self.function_pane.add_widget(self.un_input)
            self.function_pane.add_widget(Label(text='password'))
            self.pw_input = TextInput(multiline=False)
            self.function_pane.add_widget(self.pw_input)
            btn = Button(text='Login')
            btn.bind(on_press=self.login)
            self.function_pane.add_widget(btn)
            
        print('done refreshing gui')
        
###Callbacks that must interface with the api
    def login(self, button):
        print('trying to log in')
        print(self.un_input.text)
        api.login(self.un_input.text,self.pw_input.text)
        self.refresh_quick()
        
    def connect_character(self,cID,button):
        api.char_con(cID)
        self.update_gui()
        
    def disconnect_character(self):
        print('attempting to disconnect')
        api.char_dis()
        self.update_gui()
        
    def respawn(self,button):
        api.respawn()
        self.update_gui()
    
    def move(self,dir,button):
        print('moving begins')
        api.move(dir)
        print('moving ends, refreshing gui')
        self.update_gui()
        
    def portal(self, pID, button):
        api.portal(pID)
        self.update_gui()
    
    ###Combat stuff###
    def set_target(self,t,button):
        self.target = t[1]
        self.target_label.text = 't:'+t[0]
        
    def set_target_object(self,t,button):
        self.target = t
        print "attacking " + t
        self.target_label.text = 't:'+t
        
    def set_charge(self,c):
        if c == "None" or c == "Charges":
            self.charge = ''
        else:
            self.charge = c

    def attack(self):
        if self.weapon and self.target:
            if self.charge:
                api.attack(self.target,self.weapon,self.charge)
            else:
                api.attack(self.target,self.weapon)
        self.update_gui()

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
                api.reload(self.weapon)

        if reload_context == "Rocks":
            iID = 'rock'
            print('trying to rocks')
            api.pickup(iID)
        if reload_context == "Weapon":
            iID = self.weapon
            api.pickup(iID)
        if reload_context == "All":    
            iID = 'all'
            api.pickup(iID)
        #Other contextually useful buttons?
        
        self.update_gui()        
        
    def reload_weapon(self,w,button):
        api.use(w[1])
        self.update_gui()
    
    #Item stuff
    def set_item(self,i,button):    
        self.item = i[4]
        self.item_label.text = 'i:'+i[0]
        
    def set_item(self,adapter):
        #self.item = i[4]
        #self.item_label.text = 'i:'+i[0]
        
        if adapter.selection:
            item_data = find_in(adapter.selection[0].text, self.c_dat['inv_trim'])
            self.item = item_data[4]
            self.item_label.text = 'i:'+item_data[0]


        
    
    def use(self):
        self.c_dat = api.use(self.item)
        self.update_gui()
        
    def item_context_go(self):
        item_context = self.item_context.text
        if item_context == "Give":
            api.give(self.target,self.item)

        if item_context == "Drop":    
            api.drop(self.item)

        if item_context == "Safe":
            api.safe_place(self.item)
        
        if item_context == "Locker":
            api.locker_place(self.item)
        
        if item_context == "Reload":
            api.reload(self.item)
            
        if item_context == "Set Up":
            api.placeitem(self.item)
        


        self.update_gui()
        
    #Skills stuff
    def use_skill(self,s,button):
        api.useSkill(s)
        self.update_gui()

    def cast_spell(self,s,button):
        api.castSpell(s[0])
        self.update_gui()

    def trigger_spell(self,s,button):
        api.castSpell(s[0])
        self.update_gui()

    #ACTIONS stuff
    def door(self,action):
        api.door(action)
        self.update_gui()
    
    def search(self):
        api.search()
        self.update_gui()
    
    def hide(self):
        api.hide()
        self.update_gui()
    
    def say(self,text,mode=0):
        if mode:
            api.say(text,self.target)
        else:
            api.say(text)
        self.message_input.text = ''
        self.update_gui()
    
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
    
    

