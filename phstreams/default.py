# -*- coding: utf-8 -*-

'''
    Phoenix Add-on
    Copyright (C) 2015 Blazetamer
    Copyright (C) 2015 lambda

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import urlparse,sys
import xbmc,xbmcgui,xbmcaddon,xbmcplugin

params = dict(urlparse.parse_qsl(sys.argv[2].replace('?','')))

try: mode = params['mode']
except: mode = None
try: name = params['name']
except: name = '0'
try: url = params['url']
except: url = '0'
try: playable = params['playable']
except: playable = '0'
try: content = params['content']
except: content = '0'
try: audio = params['audio']
except: audio = '0'
try: image = params['image']
except: image = '0'
try: fanart = params['fanart']
except: fanart = '0'


def CATEGORIES():

    ROOT()
    addDir('NHL', 'mainnhl', 'hockey.jpg')
    addDir('Settings', 'settings', 'settings.png' ,isFolder=False)
    addDir('Manage Downloads', 'downloader', 'downloader.png')
    addDir('Search', 'search', 'search.png')

    if xbmc.getSkinDir() == 'skin.confluence':
        xbmc.executebuiltin('Container.SetViewMode(500)')

def addDir(name,mode,image,isFolder=True):

    u = sys.argv[0]+"?mode="+str(mode)
    image = xbmcaddon.Addon().getAddonInfo('path') + '/art/' + image
    item = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=image)
    item.addContextMenuItems([], replaceItems=False)
    item.setProperty('Fanart_Image', xbmcaddon.Addon().getAddonInfo('fanart'))
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=item,isFolder=isFolder)




if mode == None:
    from modules.phstreams import ROOT
    CATEGORIES()


elif mode == 'dmode' or mode == 'ndmode':
    from modules.phstreams import DIRECTORY
    DIRECTORY(name, url, audio, image, fanart, playable, content)

elif mode == 'sublinks':
    from modules.phstreams import SUBLINKS
    SUBLINKS(name, url, audio, image, fanart, playable, content)

elif mode == 'resolver':
    from modules.phstreams import RESOLVER
    RESOLVER(name, url, audio, image, fanart, playable, content)

elif mode == 'search':
    from modules.phstreams import SEARCH_ROOT
    SEARCH_ROOT()

elif mode == 'clearsearch':
    from modules.phstreams import SEARCH_CLEAR
    SEARCH_CLEAR()

elif mode == 'savedsearch':
    from modules.phstreams import SEARCH
    SEARCH(url)

elif mode == 'simsearch':
    from modules.phstreams import SEARCH
    SEARCH()

elif mode == 'settings':
    from modules.phstreams import SETTINGS
    SETTINGS()


elif mode == 'trailer':
    from modules.trailer import trailer
    trailer().play(name,None)


elif mode == 'vpop':
    from modules.dialogs import VPOP
    VPOP(url,audio)


elif mode == 'downloader':
    from modules.downloader import DOWNLOADER
    DOWNLOADER()

elif mode == 'downloader_add':
    from modules.downloader import DOWNLOADER_ADD
    DOWNLOADER_ADD(name,url,image)

elif mode == 'downloader_remove':
    from modules.downloader import DOWNLOADER_REMOVE
    DOWNLOADER_REMOVE(url)

elif mode == 'downloader_start':
    from modules.downloader import DOWNLOADER_START
    DOWNLOADER_START()

elif mode == 'downloader_status':
    from modules.downloader import DOWNLOADER_STATUS
    DOWNLOADER_STATUS()


elif mode == 'mainnhl':
    from modules.nhl import MAINNHL
    MAINNHL()

elif mode == 'nhlarchives':
    from modules.nhl import NHLARCHIVES
    NHLARCHIVES()

elif mode == 'nhlstreams':
    from modules.nhl import NHLSTREAMS
    NHLSTREAMS(name,url)

elif mode == 'nhlresolver':
    from modules.nhl import NHLRESOLVER
    NHLRESOLVER(url)


xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)
