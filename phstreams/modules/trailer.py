# -*- coding: utf-8 -*-

'''
    Genesis Add-on
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

import urllib,urllib2,urlparse,re,base64,xbmc,xbmcgui

try:
    import CommonFunctions as common
except:
    import commonfunctionsdummy as common
try:
    import json
except:
    import simplejson as json

class getUrl(object):
    def __init__(self, url, timeout='10'):
        headers = {}
        headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; rv:34.0) Gecko/20100101 Firefox/34.0'
        request = urllib2.Request(url, headers=headers)
        response = urllib2.urlopen(request, timeout=int(timeout))
        result = response.read()
        response.close()
        self.result = result


class trailer:
    def __init__(self):
        self.youtube_base = 'http://www.youtube.com'
        self.key_link = 'QUl6YVN5QkN3QkxTaFVFelhpT2NlTnVsaUNsWTBpY0U2TTRBZGRV'
        self.key_link = '&key=%s' % base64.urlsafe_b64decode(self.key_link)
        self.search_link = 'https://www.googleapis.com/youtube/v3/search?part=snippet&type=video&maxResults=5&q=%s'
        self.youtube_search = 'https://www.googleapis.com/youtube/v3/search?q='
        self.youtube_watch = 'http://www.youtube.com/watch?v=%s'

    def play(self, name, url):
        url = self.worker(name, url)
        if url == None: return
        item = xbmcgui.ListItem(path=url)
        item.setProperty("IsPlayable", "true")
        xbmc.Player().play(url, item)

    def worker(self, name, url):
        try:
            if url.startswith(self.youtube_base):
                url = self.resolve(url)
                if url == None: raise Exception()
                return url
            elif not url.startswith('http://'):
                url = self.youtube_watch % url
                url = self.resolve(url)
                if url == None: raise Exception()
                return url
            else:
                raise Exception()
        except:
            query = name + ' trailer'
            query = self.youtube_search + query
            url = self.resolve_search(query)
            if url == None: return
            return url

    def resolve_search(self, url):
        try:
            query = urlparse.parse_qs(urlparse.urlparse(url).query)['q'][0]

            url = self.search_link % urllib.quote_plus(query) + self.key_link

            result = getUrl(url).result

            items = json.loads(result)['items']
            items = [(i['id']['videoId']) for i in items]

            for url in items:
                url = self.resolve(url)
                if not url is None: return url
        except:
            return

    def resolve(self, url):
        try:
            id = url.split("?v=")[-1].split("/")[-1].split("?")[0].split("&")[0]
            result = getUrl('http://www.youtube.com/watch?v=%s' % id).result

            message = common.parseDOM(result, "div", attrs = { "id": "unavailable-submessage" })
            message = ''.join(message)

            alert = common.parseDOM(result, "div", attrs = { "id": "watch7-notification-area" })

            if len(alert) > 0: raise Exception()
            if re.search('[a-zA-Z]', message): raise Exception()

            url = 'plugin://plugin.video.youtube/?action=play_video&videoid=%s' % id
            return url
        except:
            return


