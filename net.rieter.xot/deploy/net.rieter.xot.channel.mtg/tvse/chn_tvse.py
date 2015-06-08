﻿# coding:UTF-8
import time
import datetime

import mediaitem
import chn_class
# import proxyinfo

from helpers import subtitlehelper
from regexer import Regexer
from logger import Logger
from urihandler import UriHandler
from helpers.jsonhelper import JsonHelper
from helpers.languagehelper import LanguageHelper
# from addonsettings import AddonSettings
from streams.m3u8 import M3u8


class Channel(chn_class.Channel):
    def __init__(self, channelInfo):
        """Initialisation of the class.

        Arguments:
        channelInfo: ChannelInfo - The channel info object to base this channel on.

        All class variables should be instantiated here and this method should not
        be overridden by any derived classes.

        """

        chn_class.Channel.__init__(self, channelInfo)

        # ============== Actual channel setup STARTS here and should be overwritten from derived classes ===============
        # The following data was taken from http://playapi.mtgx.tv/v1/channels
        channelId = None
        if self.channelCode == "se3":
            self.mainListUri = "http://www.tv3play.se/program"
            self.noImage = "tv3seimage.png"
            channelId = "1209|6000|6001"

        elif self.channelCode == "se6":
            self.mainListUri = "http://www.tv6play.se/program"
            self.noImage = "tv6seimage.png"
            channelId = "959"

        elif self.channelCode == "se8":
            self.mainListUri = "http://www.tv8play.se/program"
            self.noImage = "tv8seimage.png"
            channelId = "801"

        elif self.channelCode == "se10":
            self.mainListUri = "http://www.tv10play.se/program"
            self.noImage = "tv10seimage.png"
            channelId = "5462"

        elif self.channelCode == "sesport":
            raise NotImplementedError('ViaSat sport is not in this channel anymore.')

        # Danish channels
        elif self.channelCode == "tv3dk":
            self.mainListUri = "http://www.tv3play.dk/programmer"
            self.noImage = "tv3noimage.png"
            channelId = "3687|6200|6201"

        # EE channels
        elif self.channelCode == "tv3ee":
            self.mainListUri = "http://www.tv3play.ee/sisu"
            self.noImage = "tv3noimage.png"
            channelId = "1375|6301|6302"

        elif self.channelCode == "tv6ee":
            self.mainListUri = "http://www.tv3play.ee/sisu"
            self.noImage = "tv6seimage.png"
            channelId = "6300"

        # Lithuanian channels
        elif self.channelCode == "tv3lt":
            self.mainListUri = "http://www.tv3play.lt/programos"
            self.noImage = "tv3ltimage.png"
            channelId = "3000|6503"

        elif self.channelCode == "tv6lt":
            self.mainListUri = "http://www.tv3play.lt/programos"
            self.noImage = "tv6ltimage.png"
            channelId = "6501"

        elif self.channelCode == "tv8lt":
            self.mainListUri = "http://www.tv3play.lt/programos"
            self.noImage = "tv8seimage.png"
            channelId = "6502"

        # Letvian Channel
        elif self.channelCode == "se3lv":
            self.mainListUri = "http://www.tvplay.lv/parraides"
            self.noImage = "tv3lvimage.png"
            channelId = "1482|6400|6401|6402|6403|6404|6405"

        # Norwegian Channels
        elif self.channelCode == "no3":
            self.mainListUri = "http://www.tv3play.no/programmer"
            self.noImage = "tv3noimage.png"
            channelId = "1550|6100|6101"

        elif self.channelCode == "no4":
            self.mainListUri = "http://www.viasat4play.no/programmer"
            self.noImage = "viasat4noimage.png"
            channelId = "935"

        elif self.channelCode == "no6":
            self.mainListUri = "http://www.tv6play.no/programmer"
            self.noImage = "viasat4noimage.png"
            channelId = "1337"

        # setup the urls
        # self.swfUrl = "http://flvplayer.viastream.viasat.tv/flvplayer/play/swf/MTGXPlayer-0.6.9.swf"
        # self.swfUrl = "http://flvplayer.viastream.viasat.tv/flvplayer/play/swf/MTGXPlayer-1.2.2.swf"
        self.swfUrl = "http://flvplayer.viastream.viasat.tv/flvplayer/play/swf/MTGXPlayer-1.8.swf"

        # setup the main parsing data
        # the epsiode item regex is based on the channelId's. This is because the website has a filter options and shows
        # different channels on the same URL.
        self.episodeItemRegex = 'data-channel-id="(?:%s)"[^>]*>\W+<div class="clip-inner">\W+' \
                                '<a\W+href="([^"]+)"[^>]*>[\w\W]{0,300}?<img[^>]+data-src="([^"]+)"[^>]*>' \
                                '[\w\W]{0,200}?<h3[^>]+>([^<]+)' % (channelId, )
        self.videoItemJson = ('_embedded', 'videos')
        self.pageNavigationJson = ("_links", "next")
        self.pageNavigationJsonIndex = 0

        #===============================================================================================================
        # non standard items
        self.episodeLabel = LanguageHelper.GetLocalizedString(LanguageHelper.EpisodeId)
        self.seasonLabel = LanguageHelper.GetLocalizedString(LanguageHelper.SeasonId)

        #===============================================================================================================
        # Test Cases
        #  No GEO Lock: Extra Extra
        #  GEO Lock:
        #  Multi Bitrate: Glamourama

        # ====================================== Actual channel setup STOPS here =======================================
        return

    def CreateEpisodeItem(self, resultSet):
        """Creates a new MediaItem for an episode

        Arguments:
        resultSet : list[string] - the resultSet of the self.episodeItemRegex

        Returns:
        A new MediaItem of type 'folder'

        This method creates a new MediaItem from the Regular Expression or Json
        results <resultSet>. The method should be implemented by derived classes
        and are specific to the channel.

        """

        Logger.Trace(resultSet)

        url = resultSet[0]
        name = resultSet[2]
        thumbUrl = resultSet[1]
        item = mediaitem.MediaItem(name, url)
        item.description = resultSet[1]
        item.thumb = thumbUrl
        item.icon = self.icon
        return item

    def PreProcessFolderList(self, data):
        """Performs pre-process actions for data processing/

        Arguments:
        data : string - the retrieve data that was loaded for the current item and URL.

        Returns:
        A tuple of the data and a list of MediaItems that were generated.

        Accepts an data from the ProcessFolderList method, BEFORE the items are
        processed. Allows setting of parameters (like title etc) for the channel.
        Inside this method the <data> could be changed and additional items can
        be created.

        The return values should always be instantiated in at least ("", []).

        """

        Logger.Info("Performing Pre-Processing")
        items = []

        # if the main list was retrieve using json, are the current data is json, just do the default stuff.
        if data.lstrip().startswith("{"):
            return data, items

        # now we determine the ID and load the json data
        dataId = Regexer.DoRegex('data-format-id="(\d+)"', data)[-1]
        Logger.Debug("Found FormatId = %s", dataId)

        programUrl = "http://playapi.mtgx.tv/v1/videos?format=%s&order=-airdate&type=program" % (dataId, )
        data = UriHandler.Open(programUrl, proxy=self.proxy)

        clipUrl = "http://playapi.mtgx.tv/v1/videos?format=%s&order=-updated&type=clip" % (dataId, )
        clipTitle = LanguageHelper.GetLocalizedString(LanguageHelper.Clips)
        clipItem = mediaitem.MediaItem("\a.: %s :." % (clipTitle, ), clipUrl)
        clipItem.thumb = self.noImage
        items.append(clipItem)

        Logger.Debug("Pre-Processing finished")
        return data, items

    def CreatePageItem(self, resultSet):
        """Creates a MediaItem of type 'page' using the resultSet from the regex.

        Arguments:
        resultSet : tuple(string) - the resultSet of the self.pageNavigationRegex

        Returns:
        A new MediaItem of type 'page'

        This method creates a new MediaItem from the Regular Expression or Json
        results <resultSet>. The method should be implemented by derived classes
        and are specific to the channel.

        """

        Logger.Debug("Starting CreatePageItem")
        Logger.Trace(resultSet)

        url = resultSet["href"]
        page = url.rsplit("=", 1)[-1]

        item = mediaitem.MediaItem(page, url)
        item.type = "page"
        Logger.Debug("Created '%s' for url %s", item.name, item.url)
        return item

    def CreateVideoItem(self, resultSet):
        """Creates a MediaItem of type 'video' using the resultSet from the regex.

        Arguments:
        resultSet : tuple (string) - the resultSet of the self.videoItemRegex

        Returns:
        A new MediaItem of type 'video' or 'audio' (despite the method's name)

        This method creates a new MediaItem from the Regular Expression or Json
        results <resultSet>. The method should be implemented by derived classes
        and are specific to the channel.

        If the item is completely processed an no further data needs to be fetched
        the self.complete property should be set to True. If not set to True, the
        self.UpdateVideoItem method is called if the item is focussed or selected
        for playback.

        """

        Logger.Trace(resultSet)

        drmLocked = False
        geoBlocked = resultSet["is_geo_blocked"]
        # hideGeoBloced = AddonSettings().HideGeoLocked()
        # if geoBlocked and hideGeoBloced:
        #     Logger.Warning("GeoBlocked item")
        #     return None

        title = resultSet["title"]
        if "_links" not in resultSet or \
                "stream" not in resultSet["_links"] or \
                "href" not in resultSet["_links"]["stream"]:
            Logger.Warning("No streams found for %s", title)
            return None

        # the description
        description = resultSet["description"].strip()  # The long version
        summary = resultSet["summary"].strip()          # The short version
        #Logger.Trace("Comparing:\nDesc: %s\nSumm:%s", description, summary)
        if description.startswith(summary):
            pass
        else:
            # the descripts starts with the summary. Don't show
            description = "%s\n\n%s" % (summary, description)

        videoType = resultSet["type"]
        if not videoType == "program":
            title = "%s (%s)" % (title, videoType.title())

        elif resultSet["format_position"]["is_episodic"]:  # and resultSet["format_position"]["episode"] != "0":
            # make sure we show the episodes and seaso
            # season = int(resultSet["format_position"]["season"])
            episode = int(resultSet["format_position"]["episode"])
            # name = "s%02de%02d" % (season, episode)
            webisode = resultSet.get("webisode", False)

            # if the name had the episode in it, translate it
            if episode > 0 and not webisode:
                description = "%s\n\n%s" % (title, description)
                title = "%s - %s %s %s %s" % (resultSet["format_title"],
                                              self.seasonLabel,
                                              resultSet["format_position"]["season"],
                                              self.episodeLabel,
                                              resultSet["format_position"]["episode"])
            else:
                Logger.Debug("Found episode number '0' for '%s', using name instead of episode number", title)

        url = resultSet["_links"]["stream"]["href"]
        item = mediaitem.MediaItem(title, url)

        dateInfo = None
        dateFormat = "%Y-%m-%dT%H:%M:%S"
        if "broadcasts" in resultSet and len(resultSet["broadcasts"]) > 0:
            dateInfo = resultSet["broadcasts"][0]["air_at"]
            Logger.Trace("Date set from 'air_at'")

            if "playable_from" in resultSet["broadcasts"][0]:
                startDate = resultSet["broadcasts"][0]["playable_from"]
                playableFrom = time.strptime(startDate[0:-6], dateFormat)
                playableFrom = datetime.datetime(*playableFrom[0:6])  # the datetime.strptime does not work in Kodi
                if playableFrom > datetime.datetime.now():
                    drmLocked = True

        elif "publish_at" in resultSet:
            dateInfo = resultSet["publish_at"]
            Logger.Trace("Date set from 'publish_at'")

        if dateInfo is not None:
            # publish_at=2007-09-02T21:55:00+00:00
            info = dateInfo.split("T")
            dateInfo = info[0]
            timeInfo = info[1]
            dateInfo = dateInfo.split("-")
            timeInfo = timeInfo.split(":")
            item.SetDate(dateInfo[0], dateInfo[1], dateInfo[2], timeInfo[0], timeInfo[1], 0)

        item.type = "video"
        item.complete = False
        item.icon = self.icon
        item.isGeoLocked = geoBlocked
        item.isDrmProtected = drmLocked

        thumbData = resultSet['_links'].get('image', None)
        if thumbData is not None:
            # item.thumbUrl = thumbData['href'].replace("{size}", "thumb")
            item.thumb = thumbData['href'].replace("{size}", "230x150")

        item.description = description

        srt = resultSet.get("sami_path")
        if srt:
            Logger.Debug("Storing SRT path: %s", srt)
            part = item.CreateNewEmptyMediaPart()
            part.Subtitle = srt
        return item

    def UpdateVideoItem(self, item):
        """Updates an existing MediaItem with more data.

        Arguments:
        item : MediaItem - the MediaItem that needs to be updated

        Returns:
        The original item with more data added to it's properties.

        Used to update none complete MediaItems (self.complete = False). This
        could include opening the item's URL to fetch more data and then process that
        data or retrieve it's real media-URL.

        The method should at least:
        * set at least one MediaItemPart with a single MediaStream.
        * set self.complete = True.

        if the returned item does not have a MediaItemPart then the self.complete flag
        will automatically be set back to False.

        """

        Logger.Debug('Starting UpdateVideoItem for %s (%s)', item.name, self.channelName)

        if True:
            spoofIp = self._GetSetting("spoof_ip", "0.0.0.0")
            if spoofIp:
                data = UriHandler.Open(item.url, proxy=self.proxy, additionalHeaders={"X-Forwarded-For": spoofIp})
            else:
                data = UriHandler.Open(item.url, proxy=self.proxy)
        else:
            from debug.router import Router
            data = Router.GetVia("se", item.url, self.proxy)

        json = JsonHelper(data)

        # see if there was an srt already
        if item.MediaItemParts:
            part = item.MediaItemParts[0]
            if part.Subtitle:
                part.Subtitle = subtitlehelper.SubtitleHelper.DownloadSubtitle(part.Subtitle, format="dcsubtitle",
                                                                               proxy=self.proxy)
        else:
            part = item.CreateNewEmptyMediaPart()

        for q in ("high", 3500), ("hls", 2700), ("medium", 2100):
            url = json.GetValue("streams", q[0])
            Logger.Trace(url)
            if not url:
                continue

            if ".f4m" in url:
                # Kodi does not like the f4m streams
                continue

            if url.startswith("http") and ".m3u8" in url:
                for s, b in M3u8.GetStreamsFromM3u8(url, self.proxy):
                    part.AppendMediaStream(s, b)

                if not part.MediaStreams and "manifest.m3u8":
                    Logger.Warning("No streams found in %s, trying alternative with 'master.m3u8'", url)
                    url = url.replace("manifest.m3u8", "master.m3u8")
                    for s, b in M3u8.GetStreamsFromM3u8(url, self.proxy):
                        part.AppendMediaStream(s, b)

            elif url.startswith("rtmp"):
                # rtmp://mtgfs.fplive.net/mtg/mp4:flash/sweden/tv3/Esport/Esport/swe_skillcompetition.mp4.mp4
                oldUrl = url
                if not url.endswith(".flv") and not url.endswith(".mp4"):
                    url += '.mp4'

                if "/mp4:" in url:
                    # in this case we need to specifically set the path
                    # url = url.replace('/mp4:', '//') -> don't do this, but specify the path
                    server, path = url.split("mp4:", 1)
                    url = "%s playpath=mp4:%s" % (server, path)

                if oldUrl != url:
                    Logger.Debug("Updated URL from - to:\n%s\n%s", oldUrl, url)

                url = self.GetVerifiableVideoUrl(url)
                part.AppendMediaStream(url, q[1])

            else:
                part.AppendMediaStream(url, q[1])

        if part.MediaStreams:
            item.complete = True
        Logger.Trace("Found mediaurl: %s", item)
        return item
