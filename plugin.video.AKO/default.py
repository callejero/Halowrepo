# -*- coding: iso-8859-1 -*-
# please visit http://halow.x10.bz

import xbmc,xbmcgui,xbmcplugin,sys,urllib2
from resources.lib.BeautifulSoup import BeautifulStoneSoup, BeautifulSoup, BeautifulSOAP

icons = "http://karwan.tv/images/tvlogo/"
icon = xbmc.translatePath("special://home/addons/plugin.video.Karwan-kurdtv/icon.png")
plugin_handle = int(sys.argv[1])
mode = sys.argv[2]
	
def add_video_item(url, title, img=''):
    url = 'plugin://plugin.video.AKO/?playkurd=' + url + '***' + title + '***' + img
    listitem = xbmcgui.ListItem(title, iconImage=img, thumbnailImage=img)
    listitem.setInfo( type="Video", infoLabels={ "Label": title, "Title": title } )
    listitem.setProperty('IsPlayable', 'false')
    xbmcplugin.addDirectoryItem(plugin_handle, url, listitem)
    return
	
def iptvxtra_play():
    idx = mode.replace("?playkurd=", "").replace("###", "|").replace("#x#", "?").replace("#h#", "http://").split('***')
    xbmc.executebuiltin('XBMC.Notification('+idx[1]+' , KARWANTV ,5000,'+idx[2]+')')

    if idx[0] <> '':
        import resources.lib.requests as requests
        xxx = idx[0]
        ref = xxx.replace('live/','').replace('php','html')
        r = requests.get(xxx, headers={"Referer": ref})
        r = r.text.strip().replace('\n',' ')
        xxx = find_between(r,'file:',',')
        idx[0] = xxx.replace(' ','').replace("'","").replace('"','').replace('}','').replace('manifest.f4m','playlist.m3u8').strip()
        if 'rtmp://' in idx[0]:
            idx[0] = idx[0] + ' swfUrl=http://p.jwpcdn.com/6/11/jwplayer.flash.swf pageUrl=http://karwan.tv live=1'

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

def get_url():
        req = urllib2.Request('http://srv1.iptvxtra.net/xbmc/xml/kurdistan.xml')
        response = urllib2.urlopen(req)
        link=response.read()
        return link

def main():
	
    link=get_url()
	
    soup = BeautifulSOAP(link, convertEntities=BeautifulStoneSoup.XML_ENTITIES)
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
else:
    main()
