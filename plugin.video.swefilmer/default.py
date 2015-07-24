# -*- coding: utf-8 -*-
import swefilmer
import sys
import xbmcplugin
import xbmcgui
import xbmcaddon
import xbmc
from navigation import Navigation

addon = xbmcaddon.Addon(id='plugin.video.swefilmer')
swe = swefilmer.Swefilmer(xbmc, xbmcplugin, xbmcgui, addon)
navigation = Navigation(xbmc, xbmcplugin, xbmcgui, addon, swe, sys.argv[0],
                        sys.argv[1], sys.argv[2])
navigation.dispatch()
