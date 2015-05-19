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

import urllib,urllib2,re,os,sys,datetime,time
import xbmc,xbmcgui,xbmcaddon,xbmcplugin

try:
    import json
except:
    import simplejson as json

import subprocess
from jars import FuckNeulionClient


addonPath = xbmcaddon.Addon().getAddonInfo('path')
addonIcon = os.path.join(addonPath, 'art/hockey.jpg')
addonFanart = xbmcaddon.Addon().getAddonInfo('fanart')
jarfile = os.path.join(addonPath, 'jars/FuckNeulionV2.jar')


def GETURL(url):
    try:
        headers = {}
        headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; rv:34.0) Gecko/20100101 Firefox/34.0'
        request = urllib2.Request(url, headers=headers)
        response = urllib2.urlopen(request, timeout=60)
        result = response.read()
        response.close()
        return result
    except:
        return


def DATETIME_PROCESSOR(h, dt=0):

    dt1 = datetime.datetime.utcnow() - datetime.timedelta(hours = h)
    d = datetime.datetime(dt1.year, 4, 1)
    dston = d - datetime.timedelta(days=d.weekday() + 1)
    d = datetime.datetime(dt1.year, 11, 1)
    dstoff = d - datetime.timedelta(days=d.weekday() + 1)
    if dston <=  dt1 < dstoff: dt1 = dt1 + datetime.timedelta(hours = 1)
    dt1 = datetime.datetime(dt1.year, dt1.month, dt1.day, dt1.hour, dt1.minute)

    if dt == 0: return dt1

    dt2 = datetime.datetime.now()
    dt2 = datetime.datetime(dt2.year, dt2.month, dt2.day, dt2.hour, dt1.minute)

    dt3 = datetime.datetime.utcnow()
    dt3 = datetime.datetime(dt3.year, dt3.month, dt3.day, dt3.hour, dt1.minute)

    if dt2 >= dt1 :
        dtd = (dt2 - dt1).seconds/60/60
        dt = dt + datetime.timedelta(hours = int(dtd))
    else:
        dtd = (dt1 - dt2).seconds/60/60
        dt = dt - datetime.timedelta(hours = int(dtd))

    return dt


def MAINNHL():

    dt = DATETIME_PROCESSOR(5)
    datex = int(dt.strftime('%Y%m%d'))

    url = 'http://live.nhl.com/GameData/SeasonSchedule-20142015.json'
    result = GETURL(url)

    items = json.loads(result)
    items = sorted(items, key=lambda k: k['est'])

    addDir('[COLOR red]Archived Games Click Here[/COLOR]', 'Archived', 'nhlarchives', '0', '0', isFolder=True)
    addDir('[COLOR gold]Live Games , Requires some modifications to get working visit forum.[/COLOR]', '0', '0', '0', '0', isFolder=False)
    addDir('[COLOR gold]If list returns BLANK, Feed is not up yet.[/COLOR]', '0', '0', '0', '0', isFolder=False)

    for item in items:
        try:
            est = datetime.datetime.strptime(item['est'], '%Y%m%d %H:%M:%S')
            date = int(est.strftime('%Y%m%d'))
            if not date == datex: raise Exception()

            est = DATETIME_PROCESSOR(5, est)
            name = '%s at %s  [COLOR gold](%s)[/COLOR]  [COLOR red](%s)[/COLOR]' % (item['a'], item['h'], est.strftime('%H:%M'), est.strftime('%Y-%m-%d'))
            url = str(item['id'])

            addDir(name, url, 'nhlstreams', '0', '0', isFolder=True)
        except:
            pass


def NHLARCHIVES():

    dt = DATETIME_PROCESSOR(5)
    datex = int(dt.strftime('%Y%m%d'))

    url = 'http://live.nhl.com/GameData/SeasonSchedule-20142015.json'
    result = GETURL(url)

    items = json.loads(result)
    items = sorted(items, key=lambda k: k['est'])[::-1]

    for item in items:
        try:
            est = datetime.datetime.strptime(item['est'], '%Y%m%d %H:%M:%S')
            date = int(est.strftime('%Y%m%d'))
            if not date <= datex: raise Exception()

            est = DATETIME_PROCESSOR(5, est)
            name = '%s at %s  [COLOR gold](%s)[/COLOR]  [COLOR red](%s)[/COLOR]' % (item['a'], item['h'], est.strftime('%H:%M'), est.strftime('%Y-%m-%d'))
            url = str(item['id'])

            addDir(name, url, 'nhlstreams', '0', '0', isFolder=True)
        except:
            pass


def NHLSTREAMS(name,url):

    try:
        name = re.sub('\s\[COLOR.+?\].+?\[/COLOR\]', '', name).strip()
        n1 = name + ' [COLOR gold]%s[/COLOR]'; n2 = name + ' [COLOR red]%s[/COLOR]'

        SelectHomeGame = 'x0xe%sx0xehome' % str(url)
        SelectAwayGame = 'x0xe%sx0xeaway' % str(url)

        url = re.compile('(\d{4})(\d{2})(\d{4})').findall(url)[0]
        url = 'http://smb.cdnak.neulion.com/fs/nhl/mobile/feed_new/data/streams/%s/ipad/%s_%s.json' % (url[0], url[1], url[2])

        result = GETURL(url)
        result = json.loads(result)

        items = result['gameStreams']['ipad']
        h = items['home']; a = items['away']
    except:
        pass


    l1 = []; l2 = []

    try: finish = result['finish']
    except: finish = 'true'

    try: image = re.compile('"image" *: *"(.+?)"').findall(json.dumps(h))[-1]
    except: image = '0'

    try: l1.append({'name': n1 % 'Home LIVE', 'url': h['live']['bitrate0'] + SelectHomeGame, 'image': image})
    except: pass

    try: l2.append({'name': n2 % 'Home Whole', 'url': h['vod-whole']['bitrate0'], 'image': image})
    except: pass

    try: l2.append({'name': n2 % 'Home Continuous', 'url': h['vod-continuous']['bitrate0'], 'image': image})
    except: pass

    try: l2.append({'name': n2 % 'Home Condensed', 'url': h['vod-condensed']['bitrate0'], 'image': image})
    except: pass

    try: image = re.compile('"image" *: *"(.+?)"').findall(json.dumps(a))[-1]
    except: image = '0'

    try: l1.append({'name': n1 % 'Away LIVE', 'url': a['live']['bitrate0'] + SelectAwayGame, 'image': image})
    except: pass

    try: l2.append({'name': n2 % 'Away Whole', 'url': a['vod-whole']['bitrate0'], 'image': image})
    except: pass

    try: l2.append({'name': n2 % 'Away Continuous', 'url': a['vod-continuous']['bitrate0'], 'image': image})
    except: pass

    try: l2.append({'name': n2 % 'Away Condensed', 'url': a['vod-condensed']['bitrate0'], 'image': image})
    except: pass

    if finish == 'false':
        for i in l1: addDir(i['name'], i['url'], 'nhlresolver', i['image'], '0', isFolder=False)
    else:
        for i in l2: addDir(i['name'], i['url'], 'nhlresolver', i['image'], '0', isFolder=False)

    if l1 == [] and l2 == []: return xbmc.executebuiltin("Notification(%s,%s, %s, %s)" % (name, '[COLOR red]Feed not available yet[/COLOR]', 3000, addonIcon))


def NHLRESOLVER(url):

    try:
        try: url, SelectGame, Side = re.compile('(.+?)x0xe(.+?)x0xe(.+?)$').findall(url)[0]
        except: SelectGame, Side = None, None


        header = '|' + urllib.urlencode({'User-Agent': 'PS4 libhttp/1.76 (PlayStation 4)'})
        base = re.compile('(.*/).+[.]m3u8').findall(url)


        if not url.endswith('m3u8'):
            player().run(url + header, SelectGame ,Side)
            return


        result = GETURL(url)

        result = re.compile('BANDWIDTH=(\d*)\n(.+?[.]m3u8)').findall(result)
        result = [(int(int(i[0]) / 1000), i[1]) for i in result]
        result = sorted(result, reverse=True)
        result = [(str(i[0]), base[0] + i[1]) for i in result]

        q = [i[0] for i in result]
        u = [i[1] for i in result]
        select = xbmcgui.Dialog().select('Pick A Bandwidth', q)
        if select == -1: return
        url = u[select]

        player().run(url + header, SelectGame ,Side)
    except:
        return


class player(xbmc.Player):
    def __init__ (self):
        xbmc.Player.__init__(self)

    def run(self, url, SelectGame ,Side):

        if SelectGame == None or Side == None:
            item = xbmcgui.ListItem(path=url)
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)
            return


        command = ['java','-jar',jarfile,SelectGame,Side]

        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        self.process = subprocess.Popen(command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            startupinfo=startupinfo)

        if os.name == 'posix':
            success = False
            success, output = FuckNeulionClient.request_proxy_hack(SelectGame,Side)

        xbmc.sleep(1000)

        item = xbmcgui.ListItem(path=url)
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)


        for i in range(0, 240):
            if self.isPlayingVideo(): break
            xbmc.sleep(1000)
        while self.isPlayingVideo():
            xbmc.sleep(1000)
        xbmc.sleep(5000)


    def onPlayBackStarted(self):
        return

    def onPlayBackEnded(self):
        try: self.process.kill()
        except: pass

    def onPlayBackStopped(self):
        try: self.process.kill()
        except: pass


def addDir(name, url, mode, image, fanart, isFolder=True):

    u=sys.argv[0]+"?name="+urllib.quote_plus(name)+"&url="+urllib.quote_plus(url)+"&image="+urllib.quote_plus(image)+"&fanart="+urllib.quote_plus(fanart)+"&mode="+str(mode)

    if image == '0': image = addonIcon
    if fanart == '0': fanart = addonFanart

    cm = []

    item = xbmcgui.ListItem(name, iconImage=image, thumbnailImage=image)
    item.setInfo(type="Video", infoLabels = {'title': name})

    item.addContextMenuItems(cm, replaceItems=False)
    item.setProperty('Fanart_Image', fanart)

    if not isFolder == True:
        item.setProperty("IsPlayable","true")

    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=item,isFolder=isFolder)


