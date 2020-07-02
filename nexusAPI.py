import requests
import pickle
from lxml import html


###Loading pages###
def page_load(postData={}, quick = False):
    print('page loading')
    if postData:
        try:
            p = s.post(url,data=postData)
            c_dat['connection'] = True
        except requests.ConnectionError as e:
            c_dat['connection'] = False
            return
        print(postData)
    else:
        try:
            p=s.get(url)
            c_dat['connection'] = True
        except requests.ConnectionError as e:
            c_dat['connection'] = False
            return
    print('page loaded')

    #Now skip processing the page if we want to just spam something
    if not quick:#Forgo scraping on quick page load
        #Do some processing. parse with lxml
        print('parsing page')
        tree=html.fromstring(p.content)
        
        #Scrape info from the soup
        
        ref_all(tree)
        print('finished parsing page')
    if not quick:
        return tree

###Code for logging in and out###
def login(un,pw):
    
    postdat = {'username':un,'user_password':pw,'op':'login'}
    
    #Send login request
    l = s.post("http://www.nexusclash.com/modules.php?name=Your_Account", data=postdat)
    print('attempted to log in')
    ses_save(s)
    page_load()

def logout():
    pass

#Storing and restoring the session to avoid logins
def ses_load(s):
	try:
		s = pickle.load(open("login.p","rb"))
		return s
	except:
		return s

def ses_save(s):
    pickle.dump( s, open("login.p","wb"))

###Connecting and disconnecting characters###
def char_con(cID=0):
    postData={'op':'connect'}
    print(cID)
    if not cID:#This is really just for testing with the command line
        if not 'char_list' in a_dat:
            char_ref()
        choice = input("Which character alphabeticaly? ")
        cID=str(a_dat['char_list'][int(choice)][9])
    postData['CID']=cID
    page_load(postData)
    #Load the other screen too
    ref_both()
    return

def char_dis():
    #disconnect
    print('disconnecting character')
    postData={'op':'disconnect'}
    p = page_load(postData)
    return

###Scraping the character page###
def char_ref(div):
    char_list = []
    for c in div[3][0]:
        if len(c) != 10: #Break if the number of html children isn't 10. Fixes released characters.
            print('breaking')
            break
        char_stats = []
        for s in c:
            #append the text, if any
            if s.text_content():
                char_stats.append(s.text_content())
            #Otherwise, there should be a connect button, scrape the char_id
            else:
                char_stats.append(s[0][0].attrib['value'])
        char_list.append(char_stats)
    a_dat['char_list'] = char_list[1:]

###Refs using divs with IDs###
def stat_ref(div):
    stats = div[0][0][0]
    c_dat['name'] = stats[0].text_content()
    c_dat['cID'] = stats[0][0][0].attrib['href'].split('=')[-1]
    c_dat['ap'] = stats[2].text_content()
    c_dat['hp'] = stats[3].text_content()
    c_dat['mp'] = stats[4].text_content()
    c_dat['mo'] = stats[5].text_content().split('.')[0]
    c_dat['level'] = stats[1].text_content()[6:7]
    c_dat['status'] = div[0][0][2].text_content()
 
def message_ref(div):
    c_dat['log'] = div.text_content()
    #c_dat['log'] = div.text_content().split(' \r\n')[1:-1]
    
    
def error_ref(div):
    c_dat['error'] = div.text_content()
    print(c_dat['error'])

###Refs using forms###
def spell_ref(f):

    if f.attrib['name'] == 'spellother': #Castable spells from memory
        c_dat['abilities']['cast'] = []
        for s in f[1]:
            value = s.attrib['value']
            text = s.text
            mp = ''
            c_dat['abilities']['cast'].append({'text':text,'id':value,'mp':mp})

    if f.attrib['name'] == 'spellattack': #Castable spells from gems
        c_dat['abilities']['trigger'] = []
        for s in f[1]:
            iID = s.attrib['value']
            text = s.text
            mp = ''
            c_dat['abilities']['trigger'].append({'text':text,'id':iID,'mp':mp})
       
def skill_ref(f):
	#This could really have mp and ap info separated
    skill_text = f[0].attrib['value']
    skill_mp = ''
    c_dat['abilities']['skills'].append({'text':skill_text,'id':skill_text,'mp':skill_mp})

    
def portal_ref(f):
    portal_stats = f.xpath('input')
    if len(portal_stats) == 3:  #This is the regular portal case      
        portal_id = portal_stats[1].attrib['value']
        portal_name = portal_stats[2].attrib['value']
        c_dat['portals'].append([portal_name,portal_id])
    if len(portal_stats) == 2: # This is the ferries
        ferries = f.xpath('.//option')
        for dest in ferries:
            c_dat['portals'].append([dest.text, dest.attrib['value']])

def combat_ref(f):
    #only do if not done this refresh yet
    if c_dat['weapons']:
        return
    weapons = f[2]
    for weapon in weapons:
        weaponText=weapon.text_content()
        weaponText=weaponText.split(' - ')
        weaponStats=weaponText[-1].split(', ')
        weaponName = weaponText[-2]
        if weaponStats[0]=='':
            weaponDam = '0'
        else:
            weaponDam = weaponStats[0][:-1]
        weaponAcc = weaponStats[1].split(' ')[0][:-1]
        weaponID = weapon.attrib['value']
        c_dat['weapons'].append([weaponName,weaponID,weaponDam,weaponAcc])

    #Also check charge attacks
    c_dat['charges'] = []
    if len(f) > 4:
        charges = f[3]
        for charge in charges:
            c_dat['charges'].append([charge.attrib['value'],charge.text_content()])
            
    return
    
def flag_ref(f):
    global test
    test = f
    print('test')
    flag_recap = []
    if f.attrib['name'] == 'flag_retrieval':
        flags_raw = f[2]
        
        for flag in flags_raw:
            id = flag.attrib['value']
            name = flag.text_content().split(' - ')[0]
            flag_recap.append([id,name])
        flag_recap = flag_recap[1:]
    c_dat['flag_recap'] = flag_recap
    
    if f.attrib['name'] == 'flag_capture':
        c_dat['flag_capture'] = True
            
    
    
def pickup_ref(f):
    for item in f[1]:
        c_dat['pickup'].append([item.text, item.attrib['value']])

###Unsorted refs###
def loc_ref(tag):
    c_dat['location'] = tag.text_content()

#Target ref should probably scrape current hp. Stretch goal.
def target_ref(characters, levels, stats):
    # Remove faction link if we are on a SH tile:
    if characters:    
        if characters[0].attrib['href'][:32] == 'modules.php?name=Game&op=faction':
            c_dat['faction_tile'] = characters[0].text_content()
            characters = characters[1:]
        

        #Go through all the characters. Currently completely ignores pets, despite them being passed in the characters variable.
        for i in range(len(levels)):
            name = characters[i].text
            relationship = characters[i].attrib['class']
            cID = characters[i].attrib['href'].split("'")[-2]
            level = levels[i].text_content()
            
            hp_test = stats[2*i].attrib['src'][-5]
            if hp_test == '1':
                hp = 'Max'
            elif hp_test == '2':
                hp = 'High'
            elif hp_test == '3':
                hp = 'Low'
            elif hp_test == '4':
                hp = 'Dire'
            mp_test = stats[2*i+1].attrib['src'][-5]
            if mp_test == '1':
                mp = 'Max'
            elif mp_test == '2':
                mp = 'High'
            elif mp_test == '3':
                mp = 'Low'
            elif mp_test == '4':
                mp = 'Out'
            c_dat['targets'][relationship].append([name,cID,level,hp,mp])
            
        
    
    #Check if it's a pet or a person.
    #Person case:
    # if not 'title' in a.attrib:
        # name = a.text
        # cID = a.attrib['href'].split("'")[-2]
        
    #Pet case:
    # else:
        # name = a.text
        # pID = a.attrib['href'].split('=')[-1]
        # c_dat['pets'][relationship].append([name,pID])
    return
###Refs from the side bar###
def inv_ref(sidebar):
    inv_content = []
    for item in sidebar[3:]:
        #Don't bother parsing the worn stuff just yet
        if item[0].text == 'Worn':
            break
        inv_item = []
        for item_field in item:
            if item_field.text_content() !='Drop':
                inv_item.append(item_field.text_content())
            else:
                iID = item_field[0].attrib['href'].split('=')[-1]
                inv_item.append(iID)

        inv_content.append(inv_item)
        
    #Now trim the inventory.
    inv_trim = []
    for i in inv_content:
        #Remove all zero weight objects
        if i[3] == '0':
            continue
        #Remove some other stuff?
        
        #Sort spellgems?
        
        #tidy weapons?
        
        #Add the tidied item to the trimmed list
        inv_trim.append(i)
    c_dat['inv_trim'] = inv_trim
        
def map_ref(sidebar):
    map_raw = sidebar.xpath('.//div[@id="Map"]')[0][0]
    map_contents = []
    c_dat['inside'] = False
    for row in map_raw:
        for tile in row:
            #Get all the pertinent info from the tile. The contents stuff needs a lot of work.
            tile_color = tile.attrib['bgcolor']
            tile_type = tile.attrib['title'].split(', ')[-1].split(' ',1)[-1]
            
            if tile_type == 'unknown':
                c_dat['inside'] = True

            #Look in all the td elements with the background attribute
            tile_contents = tile.xpath('.//*[@background]')
            #Assume all this stuff is false
            tile_sh = False
            tile_lights = False
            tile_pc = False
            tile_pets = False
            tile_portal = False
            for i in tile_contents:
                #Check for the stronghold image
                if i.attrib['background'] == "/images/g/inf/stronghold.gif":
                    tile_sh = True
                #check for the power image
                if i.attrib['background'] == "/images/g/inf/poweron.gif":
                    tile_lights = True
                #check for any pop image
                if i.attrib['background'][:-5] == "/images/g/pop/pop":
                    tile_pc = True
                #check for any pet image
                if i.attrib['background'][:-5] == "/images/g/pop/pet":
                    tile_pets = True
                if i.attrib['background'] == "/images/g/inf/portal.gif":
                    tile_portal = True

            map_contents.append({'color':tile_color, 'type':tile_type,'sh':tile_sh,'lights':tile_lights,'pc':tile_pc,'pets':tile_pets,'portal':tile_portal})
    c_dat['map'] = map_contents
    
    a_dat['test'] = map_raw
    

def clean_data():
    for key in ['portals','pickup','weapons','charges','error','flag_recap','flag_capture','faction_tile']:
        c_dat[key] = []

    c_dat['abilities'] = {'cast':[],'trigger':[],'skills':[]}
    c_dat['targets'] = {'faction':[],'ally':[],'friendly':[],'neutral':[],'hostile':[],'enemy':[],'objects':[]}
    c_dat['pets'] = {'faction':[],'ally':[],'friendly':[],'neutral':[],'hostile':[],'enemy':[]}
    c_dat['objects'] = {'ward':False,'door':False,'fort':False}
    
def ref_force():
    page_load({'sidebar':'Inventory'})
    page_load({'sidebar':'Map'})
    return c_dat

def ref_both():

    c_dat['screen']
    print(c_dat['screen'])
    if c_dat['screen'] == 'inventory':
        page_load({'sidebar':'Map'})
    elif c_dat['screen'] == 'map':
        page_load({'sidebar':'Inventory'})
    else:
        ref_force()

def ref_all(tree):
    #Check all the data without loading any pages
    #if there are 5, it might be the character or login screen, needs further testing
    #Now do a screencheck.

    elems = tree.xpath('.//td[@valign="top"]') #Retrieves all the tds with valign top
    #this allows the screen to be checked
    if len(elems) == 3: #3 elems found means it's the login scree
        c_dat['screen'] = 'login'
        c_dat['connected'] = False
        print('login page')
    
    if len(elems) == 5: #5 elems found means it's the character select screen
        c_dat['screen'] = 'char_page'
        c_dat['connected'] = False
        char_ref(elems)
        
    #If there are 6 tds, it is the game screen
    if len(elems)==6:
        c_dat['connected'] = True
        clean_data()
        
        #Scrape info from the main panel
        main_panel = elems[3]
        #Get info from the top parts of the main panel. This stuff should always be avaialable
        id_divs = main_panel.xpath('div[@id]')
        for i in id_divs:
            if i.attrib['id']== 'CharacterInfo':
                stat_ref(i)
            elif i.attrib['id'] == 'Errors':####NOT DONE
                error_ref(i)
                print(i.attrib)
            elif i.attrib['id'] == 'Messages':
                message_ref(i)
                print(i.attrib)

                
        #start parsing the body of the main panel
        if c_dat['hp'] != '0': #Don't check this stuff if you're dead
            #Parse all the available forms
            forms = main_panel.xpath('.//form')
            for f in forms:
                if f.attrib['action'] == 'modules.php?name=Game&op=skill':
                    skill_ref(f)
                elif f.attrib['action'] == 'modules.php?name=Game&op=castspell':
                    spell_ref(f)
                elif f.attrib['action'] == 'modules.php?name=Game&op=attack':
                    combat_ref(f)
                elif f.attrib['action'] == 'modules.php?name=Game&op=flag':
                    flag_ref(f)
                elif f.attrib['name'] == 'portal':
                    portal_ref(f)
                elif f.attrib['name'] == 'pickup':
                    pickup_ref(f)
                elif f.attrib['name'] == 'wardattack':
                    c_dat['objects']['ward']= True
                    combat_ref(f)
                elif f.attrib['name'] == 'doorattack':
                    c_dat['objects']['door']= True
                    combat_ref(f)
                elif f.attrib['name'] == 'fortificationattack':
                    c_dat['objects']['fort']= True      
                    combat_ref(f)

            loc_ref(main_panel.xpath('b')[0])
                    
            #Parse the characters and pets, which are 'a' elements
            character_names = main_panel.xpath('a[@class]')
            character_levels = main_panel.xpath("*[contains(@href,'modules.php?name=Game&op=character&id')]")
            # for i in character_levels:
                # print(i.text_content())
            character_stats = main_panel.xpath("img[@height='12']")
            target_ref(character_names,character_levels,character_stats)
            
      
            
       #Scrape info from the sidebar
        sidebar = elems[4]
        #If the inventory sidebar is open
        if len(sidebar[0]) == 3 and sidebar[0][-1].text_content()[:5] =='\r\nINV':
            print('inventory')
            c_dat['screen'] = 'inventory'
            inv_ref(sidebar[0][2][0][0])
        #If the map sidebar is open
        elif len(sidebar[0]) == 5:
            map_ref(sidebar)
            c_dat['screen'] = 'map'
        #If another sidebar is open
        else:
            c_dat['screen'] = 'other'
            print('other')

###Giving Data###
def get_c_dat():
    return c_dat

def get_char_list():
    return a_dat['char_list']

######ACTIONS########
def respawn():
    postData = {'op':'respawn','RID':c_dat['cID'],'sidebar':'Map'}
    p = page_load(postData)
#Map interactions
def move(direction, leap = 0):
    postData={'op':'move','direction':direction,'sidebar':'Map'}
    for s in c_dat['abilities']['skills']:
        if s['text'] == "Deactivate Cloak of Air":
            postData['Gust'] = 'Gust'
        print('gusting?')
        
    p = page_load(postData)
    #or if you are a HC with air p = s.post(url, data={'op':'move','direction':direction,'Gust':'Gust'})
    #maybe if skills contains deactive air cloak>

    #Need to work out wyrm master and wizard movement too
    return

#Door interactions
def door(action):
    postData={'op':'door','sidebar':'Map'}
    canseep = any(l=='Deactivate Cloak of Air' for l in c_dat['abilities']['skills'])
    print('called door')
    print(action)
    print(c_dat['inside'])
    if action=='alternate':
        if c_dat['inside']:
            action = 'out'
        else:
            action = 'in'
    if action=='in':
        postData['action']='enter'
        if canseep:
            postData['action']='seepin'
    elif action=='out':
        postData['action']='exit'
        if canseep:
            postData['action']='seepout'
    elif action == 'open':
        postData['action']='open'
    elif action == 'close':
        postData['action']='close'
    elif action=='pick':
        postData['action']='pick'
    elif action=='lock':
        postData['action']='lock'
    elif action=='unlock':
        postData['action']='unlock'    

    p = page_load(postData)

#Use a portal
def portal(pID, bend=0):
    postData = {'op':'door','action':'portal','portal':pID,'sidebar':'Map'}
    p = page_load(postData)

#Basic actions
def search():
    postData={'op':'search','sidebar':'Inventory'}
    p = page_load(postData)

def hide():
    postData={'op':'hide'}
    p = page_load(postData)

#Inventory actions
def drop(iID):
    postData={'op':'drop','item':iID,'sidebar':'Inventory'}
    p = page_load(postData)
   
def reload(iID):
    postData={'op':'reload','item':iID}
    p = page_load(postData)

def use(iID):
    postData={'op':'useitem','item':iID,'sidebar':'Inventory'}
    p = page_load(postData)

#Pickup an item, with some special cases like all rocks
def pickup(item):
    postData = {'op':'pickup','sidebar':'Inventory'}

    if item=='rock':
        #iterate through all rocks
        for i in c_dat['pickup']:
            if i[0] == 'Rock':
                postData['item'] = i[1]
                page_load(postData,True)
            
        pass
    elif item == 'hatchet':
        #iterate through hatchets
        pass
    else:
        #Case where an actual number is passed
        postData['item'] = item
        page_load(postData)

#Set up a target
def placeitem(iID):
    postData = {'op':'targetsetup','item':iID,'sidebar':'Inventory'}
    p = page_load(postData)

#Safe and footlocker actions
def safe_place(iID):
    postData = {'op':'safe','item':iID,'action':'deposit','sidebar':'Inventory'}
    page_load(postData)

def safe_withdraw(iID):
    postData = {'op':'safe','item':iID,'action':'retrieve','sidebar':'Inventory'}
    page_load(postData)
    
def locker_place(iID):
    postData = {'op':'footlocker','item':iID,'action':'deposit','sidebar':'Inventory'}
    page_load(postData)

def locker_withdraw(iID):
    postData = {'op':'footlocker','item':iID,'action':'retrieve','sidebar':'Inventory'}
    page_load(postData)

#Skill and spell actions
#Cast a buffing sort of spell.
def castSpell(sName=0,sID=0):
    postData = {'op':'castspell'}
    if sID:
        postData['item']=sID

    else:
        postData['spell']=sName

    p = page_load(postData)

#Use a skill
def useSkill(s):
    postData = {'op':'skill','skill':s}
    page_load(postData)

#PC interactions
#Give a certain character a certain item
def give(cID, iID):
    postData={'op':'give','target_id':cID,'give_item_id':iID,'sidebar':'Inventory'}
    p = page_load(postData)
#Heal a character
def heal(cID):
    postData={'op':'heal','target_id':cID}
    p = page_load(postData)
#Attack a character with a specfici weapon
def attack(tID, wID, charge=0,c2=0,clock=0):

    postData={'attacking_with_item_id':wID}
    #Ward Bash
    if tID=='ward':
        postData['action']='wardattack'
        postData['op']='door'

    #Door break
    elif tID=='door':
        postData['op']='door'
        postData['action']='attack'

    elif tID == 'fort':
        postData['op'] = 'door'
        postData['action'] = 'fortificationattack'
        
    #case for pc
    else:
        postData={'target_id':tID,'attacking_with_item_id':wID}
        postData['op']='attack'

    if charge:
        postData['powerup'] = charge
    p = page_load(postData)

def say(text,target=0):
    postData = {'op':'speak', 'blahblah':text, 'SID':c_dat['cID']}
    if target:
        postData['target_id'] = target
    page_load(postData)
    
    
#faction interactions
def flag_recap(id):
    postData = {'op':'flag','action':'retrieve', 'standard_id':id}
    page_load(postData)
    
def flag_cap():
    postData = {'op':'flag','action':'capture'}
    page_load(postData)
    
####On start
            
###Session Setup###
url='http://www.nexusclash.com/modules.php?name=Game'
my_referer=url

#Session Initialise
s = requests.session()
s.headers.update({'referer': my_referer})
s = ses_load(s)

#useful variables to keep track of because spaghetti code is the bestetti code, potentially avoiding page_loads
c_dat = {'inv':[],'map':[],'inv_trim':[]}  #dictionary containing all the stuff that needs to be passed every page load
clean_data()
c_dat['connection'] = True
a_dat = {}#Dict containing some account data, won't be passed every page load



###End session setup###



