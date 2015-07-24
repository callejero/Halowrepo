# -*- coding: utf-8 -*-
from copy import deepcopy
from mocks import Xbmc, Xbmcplugin, Xbmcgui, Xbmcaddon
import navigation
import swefilmer
import unittest
from navigation import Navigation
import sys

class FirstTests(unittest.TestCase):
    def setUp(self):
        self.xbmc = Xbmc(Xbmc.LOGDEBUG)
        self.xbmcplugin = Xbmcplugin(self.xbmc)
        self.xbmcgui = Xbmcgui()
        self.addon = Xbmcaddon.Addon(id='plugin.video.swefilmer')

    def test_swefilmer(self):
        swe = swefilmer.Swefilmer(self.xbmc, self.xbmcplugin, self.xbmcgui,
                                  self.addon)
        swe.get_url(swefilmer.BASE_URL)

    def test_navigation(self):
        swe = swefilmer.Swefilmer(self.xbmc, self.xbmcplugin, self.xbmcgui,
                                  self.addon)
        nav = navigation.Navigation(self.xbmc, self.xbmcplugin, self.xbmcgui,
                                    self.addon, swe, 'plugin', '1', '')
        username, password = nav.get_credentials()
        swe.login(username, password)

    def test_resolve_redirect(self):
        swe = swefilmer.Swefilmer(self.xbmc, self.xbmcplugin, self.xbmcgui,
                                  self.addon)
        swe.resolve_redirect('https://redirector.googlevideo.com/videoplayback?requiressl=yes&id=b70284b0b126c0ef&itag=18&source=picasa&cmo=secure_transport%3Dyes&ip=0.0.0.0&ipbits=0&expire=1438852351&sparams=requiressl,id,itag,source,ip,ipbits,expire&signature=59AFF52BE87462676F00016C3B7480816FD27770.6526DFDEB450A9D6A190A6739AF8988E5FB9FC6C&key=lh1')

    def test_quality_select(self):
        swe = swefilmer.Swefilmer(self.xbmc, self.xbmcplugin, self.xbmcgui,
                                  self.addon)
        nav = navigation.Navigation(self.xbmc, self.xbmcplugin, self.xbmcgui,
                                    self.addon, swe, 'plugin', '1', '')
        stream_urls = [('1080p', 'url1080p'), ('360p', 'url360p'), ('720p', 'url720p')]
        self.assertEqual(nav.quality_select(stream_urls), 'url360p')
        stream_urls = [('sd', 'urlsd'), ('hd', 'urlhd')]
        self.assertEqual(nav.quality_select(stream_urls), 'urlsd')

    def test_traverse_all(self):
        self.xbmc.level = Xbmc.LOGNOTICE
        dir_items = self.diritems()
        self.traverse_video = True
        goal = [int(x) for x in sys.argv[1:]]
        self.traverse(dir_items, [], goal)

    def diritems(self, params=None):
        self.xbmcplugin.reset()
        swe = swefilmer.Swefilmer(self.xbmc, self.xbmcplugin, self.xbmcgui,
                                  self.addon)
        nav = Navigation(self.xbmc, self.xbmcplugin, self.xbmcgui,
                         self.addon, swe, 'plugin', '1', params)
        nav.dispatch()
        return self.xbmcplugin.dir_items

    def traverse(self, dir_items, stack, goal=[]):
        print '***** stack: ' + str(stack)
        i = 0
        if len(goal) > 0:
            print '***** goal: ' + str(goal)
            i = goal.pop(0) - 1
        for (handle, url, listitem, isFolder) in dir_items[i:]:
            i += 1
            params = '?' + url.split('?')[1]
            if isFolder or (self.traverse_video and url.find('plugin') == 0):
                if listitem.caption == self.addon.getLocalizedString(30301):
                    continue
                stack.append(i)
                print '***** selecting %d: %s' % (i, listitem.caption)
                self.diritems(params)
                new_list = deepcopy(self.xbmcplugin.dir_items)
                self.traverse(new_list, stack, goal)
            else:
                continue
        if len(stack) > 0:
            stack.pop()
        return

if __name__ == '__main__':
    unittest.main()
