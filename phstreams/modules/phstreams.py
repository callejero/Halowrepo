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

import urllib,urllib2,re,os,sys,threading,datetime
import xbmc,xbmcplugin,xbmcgui,xbmcaddon,xbmcvfs

try:
    from sqlite3 import dbapi2 as database
except:
    from pysqlite2 import dbapi2 as database


class Thread(threading.Thread):
    def __init__(self, target, *args):
        self._target = target
        self._args = args
        threading.Thread.__init__(self)
    def run(self):
        self._target(*self._args)



phLink = 'http://mecca.watchkodi.com/phstreams.xml'
phSearch = 'http://%s/search/search.xml'


dataPath = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo("profile"))
if not xbmcvfs.exists(dataPath): xbmcvfs.mkdir(dataPath)

announcements = os.path.join(dataPath, 'announcements.db')
datacache = os.path.join(dataPath,'cache.db')
metacache = os.path.join(dataPath,'metacache.db')
searchcache = os.path.join(dataPath,'search.db')

addonName = xbmcaddon.Addon().getAddonInfo('name')
addonIcon = xbmcaddon.Addon().getAddonInfo('icon')
addonFanart = xbmcaddon.Addon().getAddonInfo('fanart')
addonId = xbmcaddon.Addon().getAddonInfo("id")

metaSetting = xbmcaddon.Addon().getSetting("meta")




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


def CACHE(function, timeout, *args):
    try:
        response = None

        f = repr(function)
        f = re.sub('.+\smethod\s|.+function\s|\sat\s.+|\sof\s.+', '', f)

        import hashlib
        a = hashlib.md5()
        for i in args: a.update(str(i))
        a = str(a.hexdigest())
    except:
        pass

    try:
        dbcon = database.connect(datacache)
        dbcur = dbcon.cursor()
        dbcur.execute("SELECT * FROM rel_list WHERE func = '%s' AND args = '%s'" % (f, a))
        match = dbcur.fetchone()

        response = eval(match[2].encode('utf-8'))

        t1 = int(re.sub('[^0-9]', '', str(match[3])))
        t2 = int(datetime.datetime.now().strftime("%Y%m%d%H%M"))
        update = abs(t2 - t1) >= int(timeout*60)
        if update == False:
            return response
    except:
        pass

    try:
        r = function(*args)
        if (r == None or r == []) and not response == None:
            return response
        elif (r == None or r == []):
            return r
    except:
        return

    try:
        r = repr(r)
        t = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        dbcur.execute("CREATE TABLE IF NOT EXISTS rel_list (""func TEXT, ""args TEXT, ""response TEXT, ""added TEXT, ""UNIQUE(func, args)"");")
        dbcur.execute("DELETE FROM rel_list WHERE func = '%s' AND args = '%s'" % (f, a))
        dbcur.execute("INSERT INTO rel_list Values (?, ?, ?, ?)", (f, a, r, t))
        dbcon.commit()
    except:
        pass

    try:
        return eval(r.encode('utf-8'))
    except:
        pass


def CACHE_META(function, timeout, *args):
    try:
        response = None

        f = repr(function)
        f = re.sub('.+\smethod\s|.+function\s|\sat\s.+|\sof\s.+', '', f)

        import hashlib
        a = hashlib.md5()
        for i in args: a.update(str(i))
        a = str(a.hexdigest())
    except:
        pass

    try:
        dbcon = database.connect(metacache)
        dbcur = dbcon.cursor()
        dbcur.execute("SELECT * FROM rel_list WHERE func = '%s' AND args = '%s'" % (f, a))
        match = dbcur.fetchone()

        response = eval(match[2].encode('utf-8'))

        t1 = int(re.sub('[^0-9]', '', str(match[3])))
        t2 = int(datetime.datetime.now().strftime("%Y%m%d%H%M"))
        update = abs(t2 - t1) >= int(timeout*60)
        if update == False:
            return response
    except:
        pass

    try:
        r = function(*args)
        if (r == None or r == []) and not response == None:
            return response
        elif (r == None or r == []):
            return r
    except:
        return

    try:
        insert = True
        if r['cover_url'] == '' or r['backdrop_url'] == '': insert = False
        r = repr(r)
        t = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        dbcur.execute("CREATE TABLE IF NOT EXISTS rel_list (""func TEXT, ""args TEXT, ""response TEXT, ""added TEXT, ""UNIQUE(func, args)"");")
        dbcur.execute("DELETE FROM rel_list WHERE func = '%s' AND args = '%s'" % (f, a))
        if insert == True: dbcur.execute("INSERT INTO rel_list Values (?, ?, ?, ?)", (f, a, r, t))
        dbcon.commit()
    except:
        pass

    try:
        return eval(r.encode('utf-8'))
    except:
        pass




def ROOT():
    DIRECTORY('0', phLink, '0', '0', '0', '0', '0')


def DIRECTORY(name, url, audio, image, fanart, playable, content):

    link = CACHE(GETURL, 0, url)
    link = str(link).replace('\r','').replace('\n','').replace('\t','').replace('&nbsp;','')


    try: fanart = re.findall('<fanart>(.+?)</fanart>', link)[0]
    except: fanart = '0'


    try:
        notify = re.compile('<notify>(.+?)</notify>').findall(link)[0]

        vip = re.findall('<poster>(.+?)</poster>', link)[0]
        if not re.search('[a-zA-Z]', vip): raise Exception()

        version = re.findall('<new>(.+?)</new>', notify)[0]
        if not version.isdigit(): raise Exception()

        title = '[B]Announcement From %s![/B]' % vip
        msg1 = re.findall('<message1>(.+?)</message1>', notify)[0]
        msg2 = re.findall('<message2>(.+?)</message2>', notify)[0]
        msg3 = re.findall('<message3>(.+?)</message3>', notify)[0]

        dbcon = database.connect(announcements)
        dbcur = dbcon.cursor()
        dbcur.execute("CREATE TABLE IF NOT EXISTS announcements (""vip TEXT, ""version TEXT, ""UNIQUE(vip)"");")
        dbcur.execute("SELECT * FROM announcements WHERE vip = '%s'" % vip)

        try: match = int(dbcur.fetchone()[1])
        except: match = -1
        if int(version) > match:
            xbmcgui.Dialog().ok(str(title), str(msg1), str(msg2), str(msg3))

        dbcur.execute("DELETE FROM announcements WHERE vip = '%s'" % vip)
        dbcur.execute("INSERT INTO announcements Values (?, ?)", (vip, version))
        dbcon.commit()
        dbcon.close()
    except:
        pass


    infos = re.compile('<info>(.+?)</info>').findall(link)

    for info in infos:
        try:
            name = re.findall('<message>(.+?)</message>', info)[0]

            try: image = re.findall('<thumbnail>(.+?)</thumbnail>', info)[0]
            except: image = '0'

            addDir(name, '0', '0', image, fanart, '0', '0', {}, isFolder=False)
        except:
            pass


    popups = re.compile('<popup>(.+?)</popup>').findall(link)

    for popup in popups:
        try:
            name = re.findall('<name>(.+?)</name>', popup)[0]

            url = re.findall('<popImage>(.+?)</popImage>', popup)[0]

            try: image = re.findall('<thumbnail>(.+?)</thumbnail>', popup)[0]
            except: image = '0'

            try: audio = re.findall('<sound>(.+?)</sound>', popup)[0]
            except: audio = '0'

            addDir(name, url, 'vpop', image, fanart, audio, '0', {}, isFolder=False)
        except:
            pass


    special = re.compile('<name>([^<]+)</name><link>([^<]+)</link><thumbnail>([^<]+)</thumbnail><date>([^<]+)</date>').findall(link)
    for name, url, image, date in special:
        if re.search(r'\d+', date): name += ' [COLOR red] Updated %s[/COLOR]' % date
        addDir(name, url, 'ndmode', image, fanart, '0', '0', {}, isFolder=True)

    special = re.compile('<name>([^<]+)</name><link>([^<]+)</link><thumbnail>([^<]+)</thumbnail><mode>([^<]+)</mode>').findall(link)
    for name, url, image, mode in special:
        addDir(name, url, mode, image, fanart, '0', '0', {}, isFolder=True)



    meta = False

    try: content = re.findall('<meta>(.+?)</meta>', link)[0]
    except: content = '0'

    try: tvshow = re.findall('<tvshow>(.+?)</tvshow>', link)[0]
    except: tvshow = '0'

    if content in ['seasons', 'episodes'] and tvshow == '0':
        content = '0'

    if content in ['movies', 'tvshows'] and metaSetting == 'true':
        try:
            from metahandler import metahandlers
            metaget = metahandlers.MetaData(preparezip=False)
            meta = True
        except:
            meta = False

    elif content in ['seasons', 'episodes']:
        try:
            from metahandler import metahandlers
            metaget = metahandlers.MetaData(preparezip=False)
            #tvd = metaget.get_meta('tvshow', tvshow)
            tvd = CACHE_META(metaget.get_meta, 24, 'tvshow', tvshow, '', '', '')
        except:
            tvd = {}


    dirs = re.compile('<dir>(.+?)</dir>').findall(link)

    totalItems = len(dirs)

    for dir in dirs:
        try:
            data = {}

            name = re.findall('<name>(.+?)</name>', dir)[0]

            url = re.findall('<link>(.+?)</link>', dir)[0]

            try: image = re.findall('<thumbnail>(.+?)</thumbnail>', dir)[0]
            except: image = '0'

            try: fanart2 = re.findall('<fanart>(.+?)</fanart>', dir)[0]
            except: fanart2 = fanart

            if meta == True and content =='tvshows':
                try:
                    title = cleantitle(name).encode('utf-8')
                    data = {'title': title, 'tvshowtitle': title}

                    #data = metaget.get_meta('tvshow', title)
                    data = CACHE_META(metaget.get_meta, 24, 'tvshow', title, '', '', '')

                    metafanart = data['backdrop_url']
                    if not metafanart == '': fanart2 = metafanart
                except:
                    pass

            elif content =='tvshows':
                try:
                    title = cleantitle(name).encode('utf-8')
                    data = {'title': title, 'tvshowtitle': title}
                except:
                    pass

            elif content =='seasons':
                try:
                    title = cleantitle(tvshow).encode('utf-8')
                    data = {'title': title, 'tvshowtitle': title}

                    data.update(tvd)

                    metafanart = tvd['backdrop_url']
                    if not metafanart == '': fanart2 = metafanart
                except:
                    pass

            addDir(name, url, 'ndmode', image, fanart2, '0', content, data, totalItems=totalItems, isFolder=True)
        except:
            pass

    items = re.compile('<item>(.+?)</item>').findall(link)

    try: sort = re.findall('<sort>(.+?)</sort>', link)[0]
    except: sort = ''
    if sort == 'yes': items = sorted(items)
    totalItems = len(items)

    for item in items:
        try:

            data = {}

            name = re.findall('<title>(.+?)</title>', item)[0]

            url = re.findall('<link>(.+?)</link>', item)[0]

            try: image = re.findall('<thumbnail>(.+?)</thumbnail>', item)[0]
            except: image = '0'

            try: fanart2 = re.findall('<fanart>(.+?)</fanart>', item)[0]
            except: fanart2 = fanart

            if meta == True and content == 'movies':
                try:
                    title = cleantitle(name).encode('utf-8')
                    data = {'title': title}

                    title, year = re.compile('(.+?)[(](\d{4})[)]').findall(name)[0]
                    title = cleantitle(title).encode('utf-8')
                    data = {'title': title, 'year': year}

                    #data = metaget.get_meta('movie', title, year=year)
                    data = CACHE_META(metaget.get_meta, 24, 'movie', title, '', '', year)

                    metafanart = data['backdrop_url']
                    if not metafanart == '': fanart2 = metafanart
                    metaimage = data['cover_url']
                    if not metaimage == '': image = metaimage
                except:
                    pass

            elif content =='movies':
                try:
                    title = cleantitle(name).encode('utf-8')
                    data = {'title': title}

                    title, year = re.compile('(.+?)[(](\d{4})[)]').findall(name)[0]
                    title = cleantitle(title).encode('utf-8')
                    data = {'title': title, 'year': year}
                except:
                    pass

            elif content == 'episodes':
                try:
                    title = cleantitle(name).encode('utf-8')
                    data = {'title': title, 'tvshowtitle': tvshow}
                except:
                    pass
                try:
                    i = cleaneptitle(tvshow, title)
                    title, season, episode = i[0].encode('utf-8'), i[1], i[2]
                    data = {'title': title, 'tvshowtitle': tvshow, 'season': season, 'episode': episode}
                except:
                    pass
                try:
                    data.update({'year': tvd['year'], 'imdb_id' : tvd['imdb_id'], 'tvdb_id' : tvd['tvdb_id'], 'tvshowtitle': tvd['TVShowTitle'], 'genre' : tvd['genre'], 'studio': tvd['studio'], 'status': tvd['status'], 'duration' : tvd['duration'], 'rating': tvd['rating'], 'mpaa' : tvd['mpaa'], 'plot': tvd['plot'], 'cast': tvd['cast']})

                    metafanart = tvd['backdrop_url']
                    if not metafanart == '': fanart2 = metafanart
                except:
                    pass


            if 'sublink' in url:
                addDir(name, url, 'sublinks', image, fanart2, '0', content, data, totalItems=totalItems, isFolder=True)
            else:
                addDir(name, url, 'resolver', image, fanart2, '0', content, data, totalItems=totalItems, isFolder=False)
        except:
            pass


def SUBLINKS(name, url, audio, image, fanart, playable, content):

    match=re.compile('<sublink>(.+?)</sublink>').findall(url)
    if len(match) == 0: return

    try:
        title = cleantitle(name).encode('utf-8')
        data = {'title': title}

        title, year = re.compile('(.+?)[(](\d{4})[)]').findall(name)[0]
        title = cleantitle(title).encode('utf-8')
        data = {'title': title, 'year': year}

        if not content == 'movies': raise Exception()

        from metahandler import metahandlers
        metaget = metahandlers.MetaData(preparezip=False)

        #data = metaget.get_meta('movie', title, year=year)
        data = CACHE_META(metaget.get_meta, 24, 'movie', title, '', '', year)

        metafanart = data['backdrop_url']
        if not metafanart == '': fanart = metafanart
        metaimage = data['cover_url']
        if not metaimage == '': image = metaimage
    except:
        pass

    for i in range(0, len(match)):
        url = match[i]
        label = '%s Link %s' % (name, str(i+1))
        addDir(label, url, 'resolver', image, fanart, '0', content, data, isFolder=False)


def RESOLVER(name, url, audio, image, fanart, playable, content):

    import commonresolvers
    url = commonresolvers.get(url).result

    if url == None:
        return xbmc.executebuiltin("Notification(%s,%s, %s, %s)" % (addonName, '[COLOR red]Unplayable stream[/COLOR]', 3000, addonIcon))


    if type(url) == list and len(url) == 1:
        url = url[0]['url']

    elif type(url) == list:
        url = sorted(url, key=lambda k: k['quality'])
        for i in url: i.update((k, '720p') for k, v in i.iteritems() if v == 'HD')
        for i in url: i.update((k, '480p') for k, v in i.iteritems() if v == 'SD')
        q = [i['quality'].upper() for i in url]
        u = [i['url'] for i in url]
        select = xbmcgui.Dialog().select(addonName, q)
        if select == -1: return
        url = u[select]


    if playable == 'true':
        item = xbmcgui.ListItem(path=url)
        return xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)


    elif '.f4m'in url:
        try:
            name = cleantitle(name)

            from f4mproxy.F4mProxy import f4mProxyHelper
            return f4mProxyHelper().playF4mLink(url, name, None, None,'',image)
        except:
            return

    else:
        name = cleantitle(name)

        item = xbmcgui.ListItem(path=url, iconImage=image, thumbnailImage=image)
        item.setInfo( type="Video", infoLabels = {'title': name} )

        xbmc.PlayList(xbmc.PLAYLIST_VIDEO).clear()
        xbmc.Player().play(url, item)


def SEARCH_ROOT():
    try:
        match = []
        dbcon = database.connect(searchcache)
        dbcur = dbcon.cursor()
        dbcur.execute("SELECT * FROM search WHERE video_type ='Movie'")
        match = dbcur.fetchall()
        dbcon.close()
    except:
        match = []

    addDir('Search...', '0', 'simsearch', '0', '0', '0', '0', {}, isFolder=True)
    addDir('Clear History', '0', 'clearsearch', '0', '0', '0', '0', {}, isFolder=False)

    for query in match:
        try:
            query = eval(query[2])
            addDir('%s...' % query, query, 'savedsearch', '0', '0', '0', '0', {}, isFolder=True)
        except:
            pass


def SEARCH_CLEAR():
    try:
        dbcon = database.connect(searchcache)
        dbcur = dbcon.cursor()
        dbcur.execute("DROP TABLE IF EXISTS search")
        dbcur.execute("VACUUM")
        dbcon.commit()

        xbmc.executebuiltin("Notification(%s,%s, %s, %s)" % (addonName, '[COLOR gold]Search History Cleared[/COLOR]', 3000, addonIcon))
        xbmc.executebuiltin('Container.Refresh')
    except:
        pass


def SEARCH(query=None):

    if (query == None or query == ''):
        keyboard = xbmc.Keyboard('', 'Search')
        keyboard.doModal()
        if not (keyboard.isConfirmed()): return
        query = keyboard.getText()

    if (query == None or query == ''): return


    try:
        import hashlib
        query_id = hashlib.md5()
        for i in query: query_id.update(str(i))
        query_id = str(query_id.hexdigest())

        dbcon = database.connect(searchcache)
        dbcur = dbcon.cursor()
        dbcur.execute("CREATE TABLE IF NOT EXISTS search (""video_type TEXT, ""query_id TEXT, ""query TEXT, ""UNIQUE(video_type, query_id)"");")
        dbcur.execute("SELECT * FROM search WHERE video_type = 'Movie' AND query_id = '%s'" % query_id)
        match = dbcur.fetchone()

        if not match == None:
            dbcon.close(); raise Exception()

        dbcur.execute("INSERT INTO search Values (?, ?, ?)", ('Movie', query_id, repr(query)))
        dbcon.commit()
        dbcon.close()
    except:
        pass


    import urlparse

    global global_search ; global_search = []

    def worker(url): global_search.append(str(GETURL(url)))

    servers = str(GETURL(phLink)).replace('\n','')
    servers = re.findall('</name><link>(.+?)</link>', servers)
    servers = [urlparse.urlparse(i).netloc for i in servers]
    servers = [phSearch % i for i in servers if not 'mecca' in i]

    threads = []
    for server in servers: threads.append(Thread(worker, server))
    [i.start() for i in threads]
    [i.join() for i in threads]

    urls = global_search ; global_search = []
    urls = [str(i).replace('\n','') for i in urls]
    urls = [re.findall('<link>(.+?)</link>', i)[:30] for i in urls]
    urls = sum(urls, [])

    threads = []
    for url in urls: threads.append(Thread(worker, url))
    [i.start() for i in threads]
    [i.join() for i in threads]

    links = global_search ; global_search = []


    for link in links:
        try:
            link = str(link).replace('\r','').replace('\n','').replace('\t','').replace('&nbsp;','')

            try: fanart = re.findall('<fanart>(.+?)</fanart>', link)[0]
            except: fanart = '0'

            try: vip = re.findall('<poster>(.+?)</poster>', link)[0]
            except: vip = ''

            if vip == 'Team Phoenix': vip = ''

            try: content = re.findall('<meta>(.+?)</meta>', link)[0]
            except: content = '0'

            try: tvshow = re.findall('<tvshow>(.+?)</tvshow>', link)[0]
            except: tvshow = '0'

            if content in ['seasons', 'episodes'] and tvshow == '0':
                content = '0'


            dirs = re.compile('<dir>(.+?)</dir>').findall(link)

            for dir in dirs:
                try:
                    data = {}

                    name = re.findall('<name>(.+?)</name>', dir)[0]
                    name = cleantitle(name)

                    if not query.lower() in name.lower() : raise Exception()

                    url = re.findall('<link>(.+?)</link>', dir)[0]

                    try: image = re.findall('<thumbnail>(.+?)</thumbnail>', dir)[0]
                    except: image = '0'

                    try: fanart2 = re.findall('<fanart>(.+?)</fanart>', dir)[0]
                    except: fanart2 = fanart

                    if content =='tvshows':
                        try:
                            title = cleantitle(name).encode('utf-8')
                            data = {'title': title, 'tvshowtitle': title}
                        except:
                            pass

                    if re.search('[a-zA-Z]', vip): name += ' [COLOR orange]%s[/COLOR]' % vip

                    addDir(name, url, 'ndmode', image, fanart2, '0', content, data, isFolder=True)
                except:
                    pass


            items = re.compile('<item>(.+?)</item>').findall(link)

            for item in items:
                try:

                    data = {}

                    name = re.findall('<title>(.+?)</title>', item)[0]
                    name = cleantitle(name)

                    if not query.lower() in name.lower() : raise Exception()

                    url = re.findall('<link>(.+?)</link>', item)[0]

                    try: image = re.findall('<thumbnail>(.+?)</thumbnail>', item)[0]
                    except: image = '0'

                    try: fanart2 = re.findall('<fanart>(.+?)</fanart>', item)[0]
                    except: fanart2 = fanart

                    if content =='movies':
                        try:
                            title = cleantitle(name).encode('utf-8')
                            data = {'title': title}

                            title, year = re.compile('(.+?)[(](\d{4})[)]').findall(name)[0]
                            title = cleantitle(title).encode('utf-8')
                            data = {'title': title, 'year': year}
                        except:
                            pass

                    if re.search('[a-zA-Z]', vip): name += ' [COLOR orange]%s[/COLOR]' % vip


                    if 'sublink' in url:
                        addDir(name, url, 'sublinks', image, fanart2, '0', content, data, isFolder=True)
                    else:
                        addDir(name, url, 'resolver', image, fanart2, '0', content, data, isFolder=False)
                except:
                    pass
        except:
            pass


def SETTINGS():
    xbmc.executebuiltin('Addon.OpenSettings(%s)' % addonId)



def cleantitle(name):
    name = re.sub('(\.|\_|\(|\[|\s)(Link \d*|link \d*)(\.|\_|\)|\]|$)', '', name)
    name = re.sub('\(\d{4}.+?\d{4}\)$', '', name)
    name = re.sub('\s\[COLOR.+?\].+?\[/COLOR\]|\[/COLOR\]\[COLOR.+?\]\s.+?\[/COLOR\]|\[COLOR.+?\]|\[/COLOR\]', '', name)
    name = re.sub('\s\s+', ' ', name)
    name = name.strip()
    return name


def cleaneptitle(tvshow, name):
    try:
        p = re.compile('(S\d*E\d*)').findall(name)
        p += re.compile('(s\d*e\d*)').findall(name)
        p += re.compile('(Season \d* Episode \d*)').findall(name)
        p += re.compile('(\d*x Episode \d*)').findall(name)
        p += re.compile('(\d*x\d*)').findall(name)
        p = p[0]

        name = name.replace(tvshow, '').replace(p, '')
        name = re.sub('-|:', '', name)
        name = re.sub('\s\s+', ' ', name)
        name = name.strip()

        season = re.compile('(\d*)').findall(p)
        season = [i for i in season if i.isdigit()][0]
        season = '%01d' % int(season)

        episode = re.compile('(\d*)').findall(p)
        episode = [i for i in episode if i.isdigit()][-1]
        episode = '%01d' % int(episode)

        if re.match('[A-Z0-9]', name) == None:
            name = '%s S%02dE%02d' % (tvshow, int(season), int(episode))

        return (name, season, episode)
    except:
        return


def addDir(name, url, mode, image, fanart, audio, content, data, totalItems=0, isFolder=True):

    if not str(image).lower().startswith('http'):
        image = addonIcon

    if not str(fanart).lower().startswith('http'):
        fanart = addonFanart


    if content in ['movies', 'episodes']:
        playable = 'true'
    else:
        playable = 'false'


    u=sys.argv[0]+"?name="+urllib.quote_plus(name)+"&url="+urllib.quote_plus(url)+"&audio="+urllib.quote_plus(audio)+"&image="+urllib.quote_plus(image)+"&fanart="+urllib.quote_plus(fanart)+"&playable="+urllib.quote_plus(playable)+"&content="+str(content)+"&mode="+str(mode)

    cm = []

    if content in ['movies', 'tvshows']:
        data.update({'trailer': '%s?mode=trailer&name=%s' % (sys.argv[0], urllib.quote_plus(name))})
        cm.append(('[COLOR gold]Watch Trailer[/COLOR]', 'RunPlugin(%s?mode=trailer&name=%s)' % (sys.argv[0], urllib.quote_plus(name))))

    if not 'plot' in data:
        data.update({'plot': 'Discover Great Streaming Playlists!'})

    if content == 'movies':
        cm.append(('[COLOR gold]Movie Information[/COLOR]', 'XBMC.Action(Info)'))
    elif content in ['tvshows', 'seasons']:
        cm.append(('[COLOR gold]TV Show Information[/COLOR]', 'XBMC.Action(Info)'))
    elif content == 'episodes':
        cm.append(('[COLOR gold]Episode Information[/COLOR]', 'XBMC.Action(Info)'))       

    if content == 'movies' and not isFolder == True:
        downloader_file = name
        try: downloader_file = '%s (%s)' % (data['title'], data['year'])
        except: pass
        cm.append(('[COLOR gold]Download This File[/COLOR]', 'RunPlugin(%s?mode=downloader_add&name=%s&url=%s&image=%s)' % (sys.argv[0], urllib.quote_plus(downloader_file), urllib.quote_plus(url), urllib.quote_plus(image))))

    elif content == 'episodes' and not isFolder == True:
        downloader_file = name
        try: downloader_file = '%s S%02dE%02d' % (data['tvshowtitle'], int(data['season']), int(data['episode']))
        except: pass
        cm.append(('[COLOR gold]Download This File[/COLOR]', 'RunPlugin(%s?mode=downloader_add&name=%s&url=%s&image=%s)' % (sys.argv[0], urllib.quote_plus(downloader_file), urllib.quote_plus(url), urllib.quote_plus(image))))


    item = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=image)

    try: item.setArt({'poster': image, 'tvshow.poster': image, 'season.poster': image, 'banner': image, 'tvshow.banner': image, 'season.banner': image})
    except: pass
    item.setProperty('Fanart_Image', fanart)

    item.setInfo(type="Video", infoLabels=data)

    item.addContextMenuItems(cm, replaceItems=False)

    if playable == 'true':
        item.setProperty("IsPlayable","true")

    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=item,totalItems=totalItems,isFolder=isFolder)

    xbmcplugin.setContent(int(sys.argv[1]), content)


