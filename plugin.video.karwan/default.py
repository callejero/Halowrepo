# -*- coding: utf-8 -*-


import xbmc,xbmcgui,xbmcplugin,sys

icons = "http://karwan.tv/images/tvlogo/"
icon = xbmc.translatePath("special://home/addons/plugin.video.Karwan-kurdtv/icon.png")
plugin_handle = int(sys.argv[1])
mode = sys.argv[2]
	
def add_video_item(url, infolabels, img=''):
    if 'rtmp://' in url:
        url = url.replace('<playpath>',' playpath=')
        url = url + ' swfUrl=http://p.jwpcdn.com/6/11/jwplayer.flash.swf pageUrl=http://karwan.tv live=1'
    url = 'plugin://plugin.video.Dal/?playkurd=' + url + '***' + infolabels['title'] + '***' + img
    listitem = xbmcgui.ListItem(infolabels['title'], iconImage=img, thumbnailImage=img)
    listitem.setInfo('video', infolabels)
    listitem.setProperty('IsPlayable', 'false')
    xbmcplugin.addDirectoryItem(plugin_handle, url, listitem)
    return
	
def iptvxtra_play():
    idx = mode.replace("?playkurd=", "").replace("###", "|").replace("#x#", "?").replace("#h#", "http://").split('***')
    xbmc.executebuiltin('XBMC.Notification('+idx[1]+' , KARWAN:TV ,5000,'+idx[2]+')')

    if idx[0] <> '':
        import resources.lib.requests as requests
        xxx = idx[0]
        ref = xxx.replace('live/','').replace('php','html')
        r = requests.get(xxx, headers={"Referer": ref})
        r = r.text.strip().replace('\n',' ')
        #print r.encode('utf-8')
        xxx = find_between(r,'file:',',')
        idx[0] = xxx.replace(' ','').replace("'","").replace('"','').replace('}','').strip()
        #print idx[0]
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

def main():

    add_video_item('http://karwan.tv/live/kurdsat-news-tv.php'						,{ 'title': 'KurdSat News'}, icons + 'kurdsat-news-tv.png')
    add_video_item('http://karwan.tv/live/kurdsat-tv.php'							,{ 'title': 'KurdSat TV'}, icons + 'kurdsat-tv.png')
    add_video_item('http://karwan.tv/live/kurdistan-tv.php'							,{ 'title': 'Kurdistan TV'}, icons + 'kurdistan-tv.png')	
    add_video_item('http://karwan.tv/live/zagros-tv.php'							,{ 'title': 'Zagros TV'}, icons + 'zagros-tv.png')
    add_video_item('http://karwan.tv/live/nalia-tv.php'								,{ 'title': 'Nalia TV'}, icons + 'nalia-tv.png')
    add_video_item('http://karwan.tv/live/nalia-2-tv.php'							,{ 'title': 'Nalia 2 TV'}, icons + 'nalia-2-tv.png')
    add_video_item('http://karwan.tv/live/rudaw-tv.php'								,{ 'title': 'Rudaw TV'}, icons + 'rudaw.png')
    add_video_item('http://karwan.tv/live/knn-tv.php'								,{ 'title': 'KNN TV'}, icons + 'knn-tv.png')
    add_video_item('http://karwan.tv/live/geli-kurdistan-tv.php'					,{ 'title': 'Geli Kurdistan'}, icons + 'geli-kurdistan-tv.png')
    add_video_item('http://karwan.tv/live/gem-kurd-tv.php'							,{ 'title': 'GEM Kurd TV'}, icons + 'gem-kurd-tv.png')
    add_video_item('http://karwan.tv/live/korek-tv.php'								,{ 'title': 'Korek TV'}, icons + 'korek-tv.png')
    add_video_item('http://karwan.tv/live/falcon-eye-tv.php'								,{ 'title': 'Falcon Eye TV'}, icons + 'falcon-eye-tv.png')
    add_video_item('http://karwan.tv/live/cihan-tv.php'								,{ 'title': 'Cihan TV'}, icons + 'cihan-tv.png')
    add_video_item('http://karwan.tv/live/waar-tv.php'								,{ 'title': 'WAAR TV'}, icons + 'waar-tv.png')
    add_video_item('http://karwan.tv/live/waar-sport-tv.php'						,{ 'title': 'WAAR Sport TV'}, icons + 'waar-sport-tv.png')
    add_video_item('http://karwan.tv/live/rengin-tv.php'							,{ 'title': 'Batman TV'}, icons + 'batman-tv.png')
    add_video_item('http://karwan.tv/live/vin-tv.php'								,{ 'title': 'Vin TV'}, icons + 'vin-tv.png')
    add_video_item('http://karwan.tv/live/rojhelat-tv.php'							,{ 'title': 'Rojhelat TV'}, icons + 'rojhelat.png')
    add_video_item('http://karwan.tv/live/komala-tv.php'							,{ 'title': 'Komala TV'}, icons + 'komala-tv.png')
    add_video_item('http://karwan.tv/live/imc-tv.php'								,{ 'title': 'IMC TV'}, icons + 'imc-tv.png')
    add_video_item('http://karwan.tv/live/med-nuce-tv.php'							,{ 'title': 'MED Nuce TV'}, icons + 'med-nuce-tv.png')
    add_video_item('http://karwan.tv/live/sterk-tv.php'								,{ 'title': 'Sterk TV'}, icons + 'sterk-tv.png')
    add_video_item('http://karwan.tv/live/med-muzik-tv.php'							,{ 'title': 'MED Muzik TV'}, icons + 'med-muzik-tv.png')
    add_video_item('http://karwan.tv/live/damla-tv.php'								,{ 'title': 'Damla TV'}, icons + 'damla-tv.png')
    add_video_item('http://karwan.tv/live/tv-10.php'								,{ 'title': 'TV 10'}, icons + 'tv-10.png')
    add_video_item('http://karwan.tv/live/yol-tv.php'								,{ 'title': 'Yol TV'}, icons + 'yol-tv.png')
    add_video_item('http://karwan.tv/live/denge-tv.php'								,{ 'title': 'Denge TV'}, icons + 'denge-tv.png')
    add_video_item('http://karwan.tv/live/speda-tv.php'								,{ 'title': 'Speda TV'}, icons + 'speda-tv.png')
    add_video_item('http://karwan.tv/live/ronahi-tv.php'							,{ 'title': 'Ronahi TV'}, icons + 'ronahi-tv.png')
    add_video_item('http://karwan.tv/live/korek-tv.php'								,{ 'title': 'Korek TV'}, icons + 'korek-tv.png')
    add_video_item('http://karwan.tv/live/kurdmax-tv.php'							,{ 'title': 'KurdMAX TV'}, icons + 'kurdmax-tv.png')
    add_video_item('http://karwan.tv/live/newroz-tv.php'							,{ 'title': 'Newroz TV'}, icons + 'newroz-tv.png')
    add_video_item('http://karwan.tv/live/kanal4.php'								,{ 'title': 'Kanal 4'}, icons + 'kanal4.png')
    add_video_item('http://karwan.tv/live/amozhgary-tv.php'							,{ 'title': 'Amozhgary TV'}, icons + 'amozhgary-tv.png')
    add_video_item('http://karwan.tv/live/4sem-tv.php'								,{ 'title': '4 Sem TV'}, icons + '4sem-tv.png')
    add_video_item('http://karwan.tv/live/gk-silemani-tv.php'						,{ 'title': 'GK Silemani TV'}, icons + 'gk-silemani-tv.png')
    add_video_item('http://karwan.tv/live/cira-tv.php'								,{ 'title': 'Cira TV'}, icons + 'cira-tv.png')
    add_video_item('http://karwan.tv/live/jamawar-tv.php'							,{ 'title': 'Jamawar TV'}, icons + 'jamawar-tv.png')
    add_video_item('http://karwan.tv/live/payam-tv.php'								,{ 'title': 'Payam TV'}, icons + 'payam-tv.png')
    add_video_item('http://karwan.tv/live/km-tv.php'								,{ 'title': 'KM TV'}, icons + 'kmtv.png')
    add_video_item('http://karwan.tv/live/kirkuk-tv.php'							,{ 'title': 'KIRKUK TV'}, icons + 'kirkuk-tv.png')
    add_video_item('http://karwan.tv/live/pelistank-tv.php'							,{ 'title': 'PELISTANK TV'}, icons + 'pelistank-tv.png')
    add_video_item('http://karwan.tv/live/zarok-tv.php'								,{ 'title': 'Zarok TV'}, icons + 'zarok-tv.png')
    add_video_item('http://karwan.tv/live/evin-tv.php'								,{ 'title': 'Evin Tv'}, icons + 'evin-tv.png')
    add_video_item('http://karwan.tv/live/berivan-tv.php'							,{ 'title': 'Berivan TV'}, icons + 'berivan-tv.PNG')
    add_video_item('http://karwan.tv/live/rega-tv.php'								,{ 'title': 'REGA TV'}, icons + 'rega-tv.png')
    add_video_item('http://karwan.tv/live/rudaw-tv.php'								,{ 'title': 'Rudaw TV English'}, icons + 'rudaw.png')
    add_video_item('http://karwan.tv/live/al-hurria-tv.php'							,{ 'title': 'Al Hurria TV'}, icons + 'al-hurria-tv.png')
    add_video_item('http://karwan.tv/live/kurdmax-pepule.php'									,{ 'title': 'KurdMax Pepule TV'}, icons + 'kurdmax-tv.png')
    add_video_item('http://karwan.tv/live/super-tv.php'								,{ 'title': 'Super TV'}, icons + 'super-tv.png')
    add_video_item('http://karwan.tv/live/ozgur-gun-tv.php'								,{ 'title': 'Özgür Gün TV'}, icons + 'ozgur-gun-tv.png')								,{ 'title': 'Super TV'}, icons + 'super-tv.png').png')
    add_video_item('http://karwan.tv/live/bangawaz-tv.php'								,{ 'title': 'Bangawaz TV'}, icons + 'bangawaz-tv.png')
    add_video_item('http://karwan.tv/live/cnn-kurd-tv.php'								,{ 'title': 'CNN KURD TV'}, icons + 'cnn-kurd-tv.png')
    add_video_item('http://karwan.tv/live/carin-tv.php'								,{ 'title': 'Arin TV'}, icons + 'arin-tv.png')
    add_video_item('http://karwan.tv/live/anb-sat-tv.php'								,{ 'title': 'ANB SAT TV '}, icons + 'anb-sat-tv.png')
    add_video_item('http://karwan.tv/live/tv-yek.php'								,{ 'title': 'TV YEK '}, icons + 'tv-yek.png')
    add_video_item('http://karwan.tv/live/arzaq-kurdistan-tv.php'								,{ 'title': 'Arzaq Kurdistan TV  '}, icons + 'arzaq-kurdistan-tv.png')
    add_video_item('http://karwan.tv/live/raboon-tv.php'								,{ 'title': 'Raboon TV'}, icons + 'raboon-tv.png')
    add_video_item('http://karwan.tv/live/dengbej-tv.php'								,{ 'title': 'Dengbej TV'}, icons + 'dengbej-tv.png')
    add_video_item('http://karwan.tv/live/suryoyo-sat-tv.php'								,{ 'title': 'Suryoyo Sat TV'}, icons + 'suryoyo-sat-tv.png')
    add_video_item('http://karwan.tv/live/kurdan-tv.php'								,{ 'title': 'kurdan TV'}, icons + 'kurdan-tv.png')
    add_video_item('http://karwan.tv/live/kurdan-tv.php'								,{ 'title': 'kurdan TV'}, icons + 'kurdan-tv.png')


    xbmcplugin.endOfDirectory(plugin_handle)

if 'playkurd' in mode:
    iptvxtra_play()
else:
    main()
