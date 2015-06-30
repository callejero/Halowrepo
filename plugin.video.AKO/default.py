# -*- coding: iso-8859-1 -*-
# please visit 

import xbmc,xbmcgui,xbmcplugin,sys,urllib2
import resources.lib.requests as requests
from resources.lib.BeautifulSoup import BeautifulStoneSoup, BeautifulSoup, BeautifulSOAP

if 'extrafanart' in sys.argv[2]: sys.exit(0)

icons = "687474703A2F2F6B617277616E2E74762F696D616765732F74766C6F676F2F"
icon = xbmc.translatePath("special://home/addons/plugin.video.iptvxtra-kurdtv/icon.png")
plugin_handle = int(sys.argv[1])
md5 = 'hex'
mode = sys.argv[2]
	
def add_video_item(url, title, img=''):
    #xba = (url + '***' + title + '***' + img).encode(md5)
    url = 'plugin://plugin.video.AKO/?playkurd=' + url.encode(md5) + '***' + title + '***' + img
    listitem = xbmcgui.ListItem(title, iconImage=img, thumbnailImage=img)
    listitem.setInfo( type="Video", infoLabels={ "Label": title, "Title": title } )
    listitem.setProperty('IsPlayable', 'false')
    xbmcplugin.addDirectoryItem(plugin_handle, url, listitem)
    return
	
def iptvxtra_play():
    idx = mode.replace("?playkurd=", "").replace("###", "|").replace("#x#", "?").replace("#h#", "http://").split('***')
    xbmc.executebuiltin('XBMC.Notification('+idx[1]+' , KARWANTV ,5000,'+idx[2]+')')

    if idx[0] <> '':
        xxx = idx[0].decode(md5)
        ref = xxx.replace('live/','').replace('php','html')
        r = requests.get(xxx, headers={"Referer": ref})
        r = r.text.strip().replace('\n',' ')
        xxx = find_between(r,'file:',',')
        idx[0] = xxx.replace(' ','').replace("'","").replace('"','').replace('}','').replace('manifest.f4m','playlist.m3u8').strip()
        iudy = '73776655726C3D687474703A2F2F702E6A777063646E2E636F6D2F362F31312F6A77706C617965722E666C6173682E737766207061676555726C3D687474703A2F2F6B617277616E2E7476206C6976653D31'
        if 'rtmp://' in idx[0]: idx[0] = idx[0] + ' ' + iudy.decode(md5)

    xbmcPlayer = xbmc.Player()
    listitem = xbmcgui.ListItem( idx[1], iconImage=idx[2], thumbnailImage=idx[2])
    playlist = xbmc.PlayList( xbmc.PLAYLIST_VIDEO )
    playlist.clear()
    playlist.add(idx[0], listitem )
    xbmcPlayer.play(playlist,None,False)
    sys.exit(0)

def find_between(s,first,last):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

def auth():
    try:
        payload = {'loc': '6B757264697374616E','h':'0','sh':'servhost','la':'Q'}
        r = requests.get("http://www.iptvxtra.net/xbmc/_form/rsx.php", params=payload)
        linx = r.text.replace('.','7').replace('/','A').decode(md5).split('***')
        req = urllib2.Request(linx[0])
        req.add_header('Referer', linx[1])
        response = urllib2.urlopen(req)
        frame = response.read()
    except: frame = ''
    return frame

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

if 'playkurd' in mode:
    iptvxtra_play()
    sys.exit(0)
else:
    main()
