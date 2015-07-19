import unittest
import mock
import json

import dreamfilm
import resolvers
from mocks import Xbmc, Xbmcplugin, Xbmcgui
from navigation import Navigation


class ResolverTests(unittest.TestCase):

    def test_vk_resolver(self):
        with open('fixtures/vknew.html') as f:
            html = f.read()
            formats = resolvers.vk_streams(html)
            self.assertEqual(len(formats), 2)

class ParseTests(unittest.TestCase):

    def test_google_stream_resolver(self):
        with open('fixtures/google_player.html') as f:
            html = f.read()
            formats = resolvers.google_streams(html)
            self.assertEqual(len(formats), 3)

    def test_google_stream_serie_resolver(self):
        with open('fixtures/google_player_serie.html') as f:
            html = f.read()
            formats = resolvers.google_streams(html)
            self.assertEqual(len(formats), 2)


class APITests(unittest.TestCase):

    def test_parse_apirespone(self):
        with open('fixtures/api_search.json') as f:
            apiresponse = f.read()
            bom_stripped = dreamfilm._strip_bom(apiresponse)
            items = dreamfilm._apiresponse_to_items(bom_stripped)
            self.assertEqual(len(items), 25)

    def test_parse_season_response(self):
        with open('fixtures/api_seasons.json') as f:
            api_resonse = f.read()
            seasons = dreamfilm._series_to_list(api_resonse, 123)
            self.assertEqual(len(seasons), 7)

    def test_api_url_generation(self):
        expected = 'http://www.dreamfilmhd.org/API/api.php?type=list&offset=0&limit=25&q=Bad%20santa&sort=alpha'
        url = dreamfilm._api_url(type='list', q="Bad santa", sort="alpha")
        self.assertEqual(expected, url)

    def test_paged_api_url_generation(self):
        pager = dreamfilm._paged_api_url(type='list', q="Bad santa", sort="alpha")
        page1 = 'http://www.dreamfilmhd.org/API/api.php?type=list&offset=25&limit=25&q=Bad%20santa&sort=alpha'
        page2 = 'http://www.dreamfilmhd.org/API/api.php?type=list&offset=50&limit=25&q=Bad%20santa&sort=alpha'
        self.assertEqual(pager(1), page1)
        self.assertEqual(pager(2), page2)


if __name__ == '__main__':
    unittest.main()
