# -*- coding: utf-8 -*-

import xbmcgui,xbmc,os,sys,hashlib
import requests as requests
mode = sys.argv[1]
md5 = 'hex'
netx = xbmc.translatePath("special://home/addons/plugin.video.iptvxtra-kurdtv/resources/lib/netx.png")
iudy = '73776655726C3D687474703A2F2F702E6A777063646E2E636F6D2F362F31312F6A77706C617965722E666C6173682E737766207061676555726C3D687474703A2F2F6B617277616E2E7476206C6976653D31'


def main():
    idx = mode.replace("?playkurd=", "").replace("url=", "").replace("###", "|").replace("#x#", "?").replace("#h#", "http://").split('***')
    xbmc.executebuiltin('XBMC.Notification('+idx[1]+' , einen Moment der Sender wird geladen ,15000,'+idx[2]+')')
    get_stream(idx[3])

    if idx[0] <> '':
        xxx = idx[0].decode(md5)
        ref = xxx.replace('live/','').replace('php','html')
        r = requests.get(xxx, headers={"Referer": ref})
        r = r.text.strip().replace('\/','/').replace('","','').replace(' ','').replace("'",'"')
        xx1 = 'http://' + find_between(r,'return(["http://','"')
        xx2 = find_between(r,'return([""].join("")+','.join')
        xx3 = find_between(r,'document.getElementById("','"')
        xx2x = find_between(r,'var'+xx2+'=["','"')
        if xx2x == '': xx2x = find_between(r,'<spanstyle="display:none"id='+xx2+'>','</span>').strip()
        xx3x = find_between(r,'<spanstyle="display:none"id='+xx3+'>','</span>').strip()
        if xx3x == '': xx3x = find_between(r,'var'+xx3+'=["','"')
        idx[0] = xx1 + xx2x + xx3x
        if 'rtmp://' in idx[0]: idx[0] = idx[0] + ' ' + iudy.decode(md5)

    xbmcPlayer = xbmc.Player()
    listitem = xbmcgui.ListItem( idx[1], iconImage=idx[2], thumbnailImage=idx[2])
    playlist = xbmc.PlayList( xbmc.PLAYLIST_VIDEO )
    playlist.clear()
    playlist.add(idx[0], listitem )
    xbmcPlayer.play(playlist,None,False)
    xbmc.executebuiltin( "Dialog.Close(infodialog)" )
    sys.exit(0)

def find_between(s,first,last):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

def parse(sHtmlContent, sPattern, iMinFoundValue = 1, ignoreCase = False):
        if ignoreCase:
            aMatches = re.compile(sPattern, re.DOTALL|re.I).findall(sHtmlContent)
        else:
            aMatches = re.compile(sPattern, re.DOTALL).findall(sHtmlContent)
        if (len(aMatches) >= iMinFoundValue):                
            return True, aMatches
        return False, aMatches

def get_stream(lox):
    payload = {'loc': lox,'la':'Q'}
    r = requests.get("http://api.iptvxtra.net/check.php", params = payload )
    x = int(r.text)
    if x > 5:
        if x == 7: xbmc.executebuiltin('XBMC.Notification( verbotener Mehrfach-Login !!! , Dein Zugang wird gleichzeitig von mehreren Standorten aus benutzt - bei 5 Fehlern wird der Zugang bis 24.00 GMT-0 gesperrt - Kodi bitte neu starten ,60000,'+netx+')')
        if x == 8: xbmc.executebuiltin('XBMC.Notification( verbotener Mehrfach-Login !!! , Dein Zugang wurde automatisch bis 24.00 GMT-0 gesperrt ,60000,'+netx+')')
        if x == 9: xbmc.executebuiltin('XBMC.Notification( Fehler in den Zugangsdaten  !!! , Ein Fehler wurde in den Zugangsdaten erkannt - Passwort oder Username muss verkehrt sein ,60000,'+netx+')')
        if x == 10: xbmc.executebuiltin('XBMC.Notification( gesperrter Zugang !!! , Dein Zugang ist auf unbestimmte Zeit gesperrt - wende dich per EMail an uns ,60000,'+netx+')')
        if x == 11: xbmc.executebuiltin('XBMC.Notification( kein Zugang !!! , Dein Zugang ist aus einem anderen Land registriert worden - der Zugang ist vorläufig gesperrt ,60000,'+netx+')')
        sys.exit(0)
    return x


main()