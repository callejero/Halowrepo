# -*- coding: iso-8859-1 -*-
# please visit http://halowtv.com

import resources.lib.requests as requests
import xbmc,xbmcgui,xbmcplugin,xbmcaddon,sys,urllib2,os,hashlib
from resources.lib.BeautifulSoup import BeautifulStoneSoup, BeautifulSoup, BeautifulSOAP

if 'extrafanart' in sys.argv[2]: sys.exit(0)
	
if 'playkurd' in sys.argv[2]:
    url = sys.argv[2].replace('?playkurd=','')
    px = xbmc.translatePath("special://home/addons/plugin.video.AKO/resources/lib/zapping.py")
    xbmc.executebuiltin('RunScript('+px+',url='+url+')')
    sys.exit(0)

icons = "687474703A2F2F6B617277616E2E74762F696D616765732F74766C6F676F2F"
icon = xbmc.translatePath("special://home/addons/plugin.video.AKO/icon.png")
iconx = xbmc.translatePath("special://home/addons/plugin.video.AKO/iconx.png")
plugin_handle = int(sys.argv[1])
__settings__ = xbmcaddon.Addon(id="plugin.video.AKO")
user = __settings__.getSetting("user")
pwd = __settings__.getSetting("password")
md5 = 'hex'
mode = sys.argv[2]
	
def main():	
    soup = BeautifulSOAP(auth(), convertEntities=BeautifulStoneSoup.XML_ENTITIES)
    items = soup.findAll("item")
    for item in items:
            try:
                videoTitle=item.title.string
            except: pass
            try:
                url=item.link.string
            except: pass
            try:
                thumbnail=item.thumbnail.string
            except: pass

            add_video_item(url,videoTitle,thumbnail)
    
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

def add_video_item(url, title, img=''):
    url = 'plugin://plugin.video.AKO/?playkurd=' + url.encode(md5) + '***' + title + '***' + img + '***' + hashlib.md5('#user='+user+'pass='+pwd).hexdigest()
    listitem = xbmcgui.ListItem(title, iconImage=img, thumbnailImage=img)
    listitem.setInfo( type="Video", infoLabels={ "Label": title, "Title": title } )
    listitem.setProperty('IsPlayable', 'false')
    listitem.setProperty( "Fanart_Image", img )
    xbmcplugin.addDirectoryItem(plugin_handle, url, listitem)
    return
	
def auth():
    try:
        lox = hashlib.md5('#user='+user+'pass='+pwd).hexdigest()
        payload = {'loc': lox,'h':'0','sh':'servhost','la':'Q'}
        r = requests.get("http://www.iptvxtra.net/xbmc/_form/rsx.php", params=payload)
        if '6B.5.26469.3.4616E5F.3' == r.text.strip():
            xbmc.executebuiltin('XBMC.Notification(Login Fehler , KARWAN TV ,20000,'+iconx+')')
            xbmcaddon.Addon("plugin.video.iptvxtra-kurdtv").openSettings()
            sys.exit(0)
        if '6B.5.26469.3.469995F.3' == r.text.strip():
            xbmc.executebuiltin('XBMC.Notification(Login Fehler , KARWAN TV ,30000,'+iconx+')')
            sys.exit(0)
        linx = r.text.replace('.','7').replace('/','A').strip().decode(md5).split('***')
        req = urllib2.Request(linx[0])
        req.add_header('Referer', linx[1])
        response = urllib2.urlopen(req)
        frame = response.read()
    except: frame = ''
    return frame

main()
