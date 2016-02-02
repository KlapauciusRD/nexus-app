A mobile interface for Nexus Clash, an online browser based MMO

To install on android: Download and install the latest apk file in the bin directory onto your device. 
If you haven't already, you must 'enable installation of files from untrusted sources' in your android options -> security settings
We've had some issues with screen dimmers during installation, so if you can't click the install button just panic



How to use:
The func. tab contains the login and character connect info. If nothing seems to be popping up, go here.
The weapon, target and item are all saved when selected. Any item, target or attacking actions will use these.
The reload context menu reloads the selected weapon. Unlike the game system, a default target and weapon will never be selected.
This precludes the possibility of accidentally attacking with the wrong weapon or the wrong target.
Portals and door actions, such as opening, closing, entering and exiting are in the act tab. 
Respawn is in the act tab.

Notable unimplemented features:
There are no pet interactions, either summoning or killing. 
Alchemy and enchanting are not possible
Some charge attacks do not work, particularly the ones I don't have to test.
Skills with dropdowns do not work (i.e. portal cleaving)
Portals cannot be bent



###Instructions for install Python + Kivy for development###
Instructions for Windows 10 64 bit:

Git instructions:
download git for windows at
https://git-scm.com/download/win

open git GUI
clone existing repository from https://github.com/KlapauciusRD/nexus-app
to a directory of your choice

Install python 2.7 (preferably in default directory c:/python27)
download the lxml windows 64 bit install file located at
https://pypi.python.org/packages/2.7/l/lxml/lxml-3.3.5.win-amd64-py2.7.exe#md5=eab16170c28173b66019eace6352a0c1

run the following python commands (might need to be run from python directory):
python -m pip install --upgrade pip setuptools
python -m easy_install "(LOCATION OF THE lxml PACKAGE DOWNLOADED ABOVE)"
python -m pip install docutils pygments pypiwin32 kivy.deps.sdl2 kivy.deps.glew
python -m pip install cython requests
python -m pip install kivy

it should now be possible to run main.py by double clicking it. Alternatively, using the following command in 
batch file will create a window and keep it open so that any error messages are visible
c:/python27/python.exe -i main.py

Install on ubuntu 64 bit:
tbd

