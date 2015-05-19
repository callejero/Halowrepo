# -*- coding: utf-8 -*-

import os
import sys
import re
import urllib
import urllib2
import htmllib
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import base64
import time
import base64
import string
import tempfile
#import tvdb_api
import subprocess as sp
import webbrowser
import urlparse
import zipfile
import json
#from selenium import webdriver
#from selenium.webdriver.common.keys import Keys
#import selenium.webdriver.support.ui as ui
#from selenium.webdriver.support.wait import WebDriverWait
#from selenium.webdriver.common.by import By
#from selenium.webdriver.support import expected_conditions as EC
import xml.etree.ElementTree as ET
from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup
from xml.dom.minidom import parseString
from sys import platform as _platform
import datetime
import time
import iso8601
import locale
import mechanize
import posixpath

global thisPlugin
global XBMCPROFILE
global RESOURCE_FOLDER
global ROOT_FOLDER
#global tvDb

try:
    from sqlite3 import dbapi2 as sqlite
    xbmc.log("Loading sqlite3 as DB engine")
except:
    from pysqlite2 import dbapi2 as sqlite
    xbmc.log("Loading pysqlite2 as DB engine")

thisPlugin = int(sys.argv[1])
__settings__ = xbmcaddon.Addon(id='plugin.video.viaplay')
__language__ = __settings__.getLocalizedString
ROOT_FOLDER = __settings__.getAddonInfo('path')
XBMCPROFILE = xbmc.translatePath('special://profile')
RESOURCE_FOLDER = os.path.join(unicode(ROOT_FOLDER,'utf-8'), 'resources')
LIB_FOLDER = os.path.join(RESOURCE_FOLDER, 'lib')
CHANNELS_FOLDER=os.path.join(RESOURCE_FOLDER, 'channel_icons')
VIAPLAYER_PATH = os.path.join(LIB_FOLDER, 'viaplayLauncher.exe')
AUTOHOTKEY_PATH = os.path.join(LIB_FOLDER, 'MceRemoteHandler.exe')
AUTOHOTKEY_XBMC_PATH= os.path.join(LIB_FOLDER, 'ActivateXbmc.exe')
SETTINGS_PLATFORM = __settings__.getSetting("PLATFORM")
SETTINGS_USERNAME = __settings__.getSetting("Username")
SETTINGS_PASSWORD = __settings__.getSetting("Password")
SETTINGS_USETVDB =(__settings__.getSetting("UseTvdb").lower() == "true")
SETTINGS_USE_IPAD =(__settings__.getSetting("UseIPAD").lower() == "true")
SETTINGS_USE_ANDROID =(__settings__.getSetting("UseAndroid").lower() == "true")
SETTINGS_USE_SUBTITLES=(__settings__.getSetting("UseSubtitles").lower() == "true")
SETTINGS_SORTBYADDED = (__settings__.getSetting("SortByAdded").lower() == "true")
SETTINGS_USE_PARENTAL_CONTROL = (__settings__.getSetting("UseParentalControl").lower() == "true")
SETTINGS_PINCODE = __settings__.getSetting("Pincode")
SETTING_CHECKVERSION=(__settings__.getSetting("CheckVersion").lower() == "true")
#tvDb = tvdb_api.Tvdb(apikey="5736416B121F48D5")
SETTINGS_COUNTRY = __settings__.getSetting("Country")
PLATFORM_WIN=1
PLATFORM_LINUX=2
PLAFORM_MAC=3
ContentTypeTV='episode'
ContentTypeMovie='movie'
ContentTypeSport='sport'
check_version=1

class StreamQuality(object):
    def __init__(self, bandWidth=None,filename=None,resolution=None):
        self.bandWidth=bandWidth
        self.filename=filename
        self.resolution=resolution

class StreamInfoEx(object):
    def __init__(self, streamUrl=None,subtitleUrl=None,rawUrl=None):
        self.streamUrl=streamUrl
        self.subtitleUrl=subtitleUrl
        self.rawUrl=rawUrl

class SportEvent(object):
    def __init__(self, starttime=None,day=None,dayname=None, title=None, image_url=None, item_url=None,productId=None):
        self.starttime = starttime
        self.day=day
        self.dayname=dayname
        self.title = title
        self.image_url = image_url
        self.item_url = item_url
        self.productId=productId

class Link(object):
	def __init__(self, type=None, name=None, cmd=None, url=None):
		self.type = type
		self.name = name
		self.cmd = cmd
		self.url = url

class CachedTv(object):
	def __init__(self, seriesName=None, seriesId=None, dataUrl=None, fanartUrl=None):
		self.seriesName = seriesName
		self.seriesId = seriesId
		self.dataUrl = dataUrl
		self.fanartUrl = fanartUrl

class TvSeries(object):
	def __init__(self, season=None, episode=None, episodeTitle=None,filename=None, name=None):
		self.season = season
		self.episode = episode
		self.episodeTitle = episodeTitle
		self.name = name
		self.filename=filename

class EpisodeStreamInfo(object):
	def __init__(self, title=None, episodeTitle=None, synopsis=None):
		self.title = title
		self.episodeTitle = episodeTitle
		self.synopsis = synopsis
		
class StreamInfo(object):
	def __init__(self, title=None,episodeTitle=None, image=None):
		self.title = title
		self.episodeTitle = episodeTitle
		self.image = image

class TvSchedule(object):
    def __init__(self, starttime=None,program=None,synopsis=None):
        self.starttime = starttime
        self.program=program
        self.synopsis=synopsis

class Channel(object):
    def __init__(self, name=None,image=None,url=None,epg=None):
        self.name = name
        self.image=image
        self.url=url
        self.epg=epg

def RemoveFile(path):
	if(os.path.exists(path)):
		xbmc.log('File was found, trying to delete it')
		os.remove(path)
		xbmc.log('File was removed')

def GetJson(url):
    page=urllib2.urlopen(url)
    jsonData = page.read()
    objs = json.loads(jsonData)

    return objs

def GetSecureJson(url):

    username = urllib.quote_plus(SETTINGS_USERNAME)
    password=urllib.quote_plus(SETTINGS_PASSWORD)

    mech = mechanize.Browser()
    mech.set_handle_robots(False)
    
    secureUrl=GetLoginUrl()+username+"&password="+password

    mech.open(secureUrl)
    
    mech.open(url)
    
    jsonData = mech.response().get_data()
    objs = json.loads(jsonData)
    
    return objs

def GetSecureAdultJson(url,url2):

    username = urllib.quote_plus(SETTINGS_USERNAME)
    password=urllib.quote_plus(SETTINGS_PASSWORD)

    mech = mechanize.Browser()
    mech.set_handle_robots(False)
    
    secureUrl=GetLoginUrl()+username+"&password="+password

    mech.open(secureUrl)
    
    mech.open(url)
    
    mech.open(url2)

    jsonData = mech.response().get_data()
    objs = json.loads(jsonData)
    
    return objs

def GetAdultContent(url):
    verification=GetAgeVerificationUrl()

    objs = GetSecureAdultJson(verification,url)
    return objs

def GetChannels(country):
    root = os.path.join(ROOT_FOLDER,"resources","channel_icons")

    if SETTINGS_USE_ANDROID:
        path = os.path.join(root, "channels_internal.json")
    else:
        path = os.path.join(root, "channels.json")

    file = open(path.decode('utf-8'),'r')
    jsonData = file.read()
    file.close()

    objs = json.loads(jsonData)

    channels=[]

    for item in objs[u'dsData'][u'Channels']:
        if item[u'Country']==country:
            if len(item['EPG']) > 0:
                epg=GetCurrentTVSchedule(item['EPG'])
            else:
                epg=None
            imgPath= os.path.join(root.decode('utf-8'), item['Image'])
            channels.append(Channel(item['Name'],imgPath,item['Url'],epg))

    return channels

def GetCurrentTVSchedule(url):

    if len(url)==0:
        return TvSchedule("","","")

    page=urllib2.urlopen(url)
    data = page.read()

    soup = BeautifulSoup(data)
    #<div class="program-info act">
    result=soup.findAll('div', attrs={'class' : 'program-info act'})
    if len(result)==0:
        result=soup.findAll('div', attrs={'class' : 'program-info act odd'})

    program = result[0].contents[1].contents[0].contents[0]
    synposis=unicode(result[0].contents[5].string).encode('utf-8').strip()
    startTime=str(result[0].contents[3].string)
    
    return TvSchedule(startTime,program,synposis)

def AddStarredContent(productId):
    xbmc.log("AddStarredContent productId: " + productId)
    url = GetStarredDomain()+"/setStarStatus/"+productId+"/1"
    objs=GetSecureJson(url)

    return bool(objs['success'])

def RemoveStarredContent(productId):
    xbmc.log("RemoveStarredContent productId: " + productId)
    url = GetStarredDomain()+"/setStarStatus/"+productId+"/0"
    objs=GetSecureJson(url)

    return bool(objs['success'])

def GetAllStarredContent():
    links = GetLinks('ALL_STARRED')
    url=""

    for link in links:
        url = link.url

    GetStarredContent(url,ContentTypeTV)
    GetStarredContent(url,ContentTypeMovie)
    GetStarredContent(url,ContentTypeSport)

def GetAllWatchedContent():
    links = GetLinks('ALL_WATCHED')
    url=""

    for link in links:
        url = link.url

    GetStarredContent(url,ContentTypeTV)
    GetStarredContent(url,ContentTypeMovie)
    GetStarredContent(url,ContentTypeSport)

def GetStarredContent(url,type):
    objs = GetSecureJson(url)

    for block in objs['_embedded']['viaplay:blocks']:
        for product in block['_embedded']['viaplay:products']:
            itemType=str(product['type'])
            if itemType==type:
                title=unicode(product['content']['title']).encode('utf-8')
                synopsis=unicode(product['content']['synopsis']).encode('utf-8')
                image_url=str(product['content']['images']['landscape']['url'])
                product_url=str(product['_links']['self']['href'])
                prodId=str(product['system']['productId'])

                if itemType== ContentTypeMovie:
                    parentalRating = str(product[u'content'][u'parentalRating'])
                else:
                    parentalRating=""

                if itemType == ContentTypeTV:
                    title = title + " - " + unicode(product['content']['series']['season']['title']).encode('utf-8') + " - Avsnitt " + str(product['content']['series']['episodeNumber'])
                
                if itemType==ContentTypeSport:
                    producttime = iso8601.parse_date(str(product['epg']['start'])) + datetime.timedelta(hours=GetTimeDifference())
                    starttime=producttime.strftime('%Y-%m-%d %H:%M')
                    title = title + " (" + starttime +")"

                listItem = xbmcgui.ListItem(title)

                if product_url.endswith('-hd'):
                    overlay=xbmcgui.ICON_OVERLAY_HD
                    listItem.setLabel2(" (HD)")
                else:
                    overlay=xbmcgui.ICON_OVERLAY_NONE
                    
                if itemType==ContentTypeMovie:
                    boxart_url=str(product['content']['images']['boxart']['url'])
                    listItem.setThumbnailImage(boxart_url)
                    listItem.setProperty("Fanart_Image", image_url)
                else:
                    listItem.setThumbnailImage(image_url)

                infoLabels = { "Title": title,"Genre": "","Year": "","Director": [""],"Cast": [""],"Plot": synopsis,'videoresolution':'','overlay':overlay }
                listItem.setInfo(type="Video", infoLabels=infoLabels)

                if itemType==ContentTypeTV:
                    seasonNo=int(product['content']['series']['season']['seasonNumber'])
                    episodeNo=int(product['content']['series']['episodeNumber'])

                    overlay=xbmcgui.ICON_OVERLAY_NONE
                    playcount=0

                    if IsWatchedProduct(prodId):
                        overlay=xbmcgui.ICON_OVERLAY_WATCHED
                        playcount=1
                    else:
                        overlay=xbmcgui.ICON_OVERLAY_UNWATCHED
                        playcount=0

                    infoLabels = { "Title": title,"tvshowtitle": title,"season": seasonNo,"episode": episodeNo,"plotoutline": synopsis,"plot": synopsis,"overlay":overlay,"playcount":playcount}
                    listItem.setInfo(type="Video", infoLabels=infoLabels)
                    item_url=str(sys.argv[0]) + '?' + "url=" + urllib.quote_plus(product_url) + "&mode=play&productid=" + prodId+"&contenttype=tv" #+"?partial=true&block=1"
                        
                elif itemType==ContentTypeMovie:
                    item_url=str(sys.argv[0]) + '?' + "url=" + urllib.quote_plus(product_url) + "&mode=play&productid=" + prodId+"&contenttype=movie&parentalrating="+urllib.quote_plus(parentalRating)
                elif itemType==ContentTypeSport:
                    item_url=str(sys.argv[0]) + '?' + "url=" + urllib.quote_plus(product_url) + "&mode=play&productid=" + prodId+"&contenttype=sport"

                cm_url_remove = str(sys.argv[0]) + '?' + "productid=" + prodId+"&mode=remove_watched"
                cm_url_add = str(sys.argv[0]) + '?' + "productid=" + prodId+"&mode=add_watched"

                menu_txt_MarkAsShown=unicode(__language__(4041)).encode('utf-8')
                menu_txt_MarkNotAsShown=unicode(__language__(4042)).encode('utf-8')

                cm_url_remove_starred = str(sys.argv[0]) + '?' + "productid=" + prodId+"&mode=remove_starred"
                cm_url_add_star = str(sys.argv[0]) + '?' + "productid=" + prodId+"&mode=add_starred"

                menu_txt_AddStar=unicode(__language__(4043)).encode('utf-8')
                menu_txt_RemoveStarred=unicode(__language__(4044)).encode('utf-8')

                listItem.addContextMenuItems([(menu_txt_MarkAsShown, "XBMC.RunPlugin(%s)" % (cm_url_add),),(menu_txt_MarkNotAsShown, "XBMC.RunPlugin(%s)" % (cm_url_remove),),(menu_txt_AddStar, "XBMC.RunPlugin(%s)" % (cm_url_add_star),),(menu_txt_RemoveStarred, "XBMC.RunPlugin(%s)" % (cm_url_remove_starred),)],replaceItems=True)

                xbmcplugin.addDirectoryItem(thisPlugin,item_url,listItem)

#def GetEpisodeInfo(url):
#    page=urllib2.urlopen(url)
#    soup = BeautifulSoup(page.read())
#    #<head prefix="og: http://ogp.me/ns# fb: http://ogp.me/ns/fb# video: http://ogp.me/ns/video# website: http://ogp.me/ns/website#">
#    #<meta property="og:title" content="The Walking Dead - Säsong 1 Avsnitt 4">og:description
#    title =GetContentValue(str(soup.find("meta", {"property": 'og:title'})),"\"",3)
    
#    list = title.split(" - ")
#    title = list[0]
#    episodeTitle = list[1]

#    return StreamInfo(title,episodeTitle,"")
    
#def GetMovieInfo(url):
#    page=urllib2.urlopen(url)
#    soup = BeautifulSoup(page.read())
#    #<head prefix="og: http://ogp.me/ns# fb: http://ogp.me/ns/fb# video: http://ogp.me/ns/video# website: http://ogp.me/ns/website#">
#    #<meta property="og:title" content="The Walking Dead - Säsong 1 Avsnitt 4">og:description
#    title =GetContentValue(str(soup.find("meta", {"property": 'og:title'})),"\"",3)
#    image =GetContentValue(str(soup.find("meta", {"property": 'og:image'})),'\"',3)

#    return StreamInfo(title,"",image)

def CheckForParentalControl(value):

    allowedYear=GetParentalYear()
    xbmc.log("CheckForParentalControl GetParentalYear: " + str(allowedYear))
    currentYear = TranslateFromBBFC(value)

    if currentYear == allowedYear or currentYear > allowedYear:
        input = get_input(unicode(__language__(4053)).encode('utf-8'),"",True)

        if input == SETTINGS_PINCODE:
            return True
        else:
            return False
    else:
        return True


def GetParentalDomain():
	if SETTINGS_COUNTRY=="0":
		return "https://account.viaplay.se/parental"
	elif SETTINGS_COUNTRY=="1":
		return "https://account.viaplay.dk/parental"
	elif SETTINGS_COUNTRY=="2":
		return "https://account.viaplay.no/parental"
	elif SETTINGS_COUNTRY=="3":
		return "https://account.viaplay.fi/parental"
		
	return "https://account.viaplay.se/parental"

def TranslateFromBBFC(value):
    if value=="U" or value=="PG":
        return 7
    elif value=="12" or value=="12a":
        return 12
    elif value=="15":
        return 15
    elif value=="18" or value=="R18":
        return 18
    
    return 7 

def GetParentalYear():

    username = urllib.quote_plus(SETTINGS_USERNAME)
    password=urllib.quote_plus(SETTINGS_PASSWORD)

    mech = mechanize.Browser()
    mech.set_handle_robots(False)

    secureUrl=GetLoginUrl()+username+"&password="+password
    url = GetParentalDomain()

    mech.open(secureUrl)
    mech.open(url)

    mech.select_form(nr=0)
    mech["ParentalControlLoginForm[pin]"] = SETTINGS_PINCODE

    mech.submit()
    html = mech.response().get_data()

    soup = BeautifulSoup(html)
    
    result=soup.findAll('select', attrs={'name' : 'ParentalControlSettingsForm[parentalLabel]'})

    value =0

    for item in result[0].contents:
        if 'selected' in str(item):
            value = int(item.attrs[0][1])

    if value==2:
        return 7
    elif value==4:
        return 12
    elif value==5:
        return 15
    elif value==7:
        return 18

    return 0

def GetContentValue(value,splitValue,index):
    list=value.split(splitValue)
    return str(list[index])

def EscapeXml_subtitle(value):
	string =str(value)
	string = string.replace('å','&aring;')
	string = string.replace('ä','&auml;')
	string = string.replace('ö','&ouml;')
	string = string.replace('Å','&Aring;')
	string = string.replace('Ä','&Auml;')
	string = string.replace('Ö','&Ouml;')
	string = string.replace('...','&hellip;')
	string = string.replace('\"','&quot;')
	string = string.replace('&','&amp;')
	string = string.replace('ø','&oslash;')
	string = string.replace('Ø','&Oslash;')
	string = string.replace('æ','&aelig;')
	string = string.replace('Æ','&AElig;')
	string = string.replace('É','&Eacute;')
	string = string.replace('é','&eacute;')
	return string
	
def EscapeXml_old(value):
	string =str(value)
	string = string.replace('å','&aring;')
	string = string.replace('ä','&auml;')
	string = string.replace('ö','&ouml;')
	#string = string.replace('Å','&Aring;')
	#string = string.replace('Ä','&Auml;')
	#string = string.replace('Ö','&Ouml;')
	string = string.replace('...','&hellip;')
	#string = string.replace('\"','&quot;')
	string = string.replace('&','&amp;')
	# string = string.replace('ø','&oslash;')
	# string = string.replace('Ø','&Oslash;')
	# string = string.replace('æ','&aelig;')
	# string = string.replace('Æ','&AElig;')
	string = string.replace('É','&Eacute;')
	string = string.replace('é','&eacute;')
	return string
	
def EscapeXml(value):
	string =str(value)
	string = string.replace('å','&#229;')
	string = string.replace('ä','&#228;')
	string = string.replace('ö','&#246;')
	string = string.replace('Å','&#197;')
	string = string.replace('Ä','&#196;')
	string = string.replace('Ö','&#214;')
	#string = string.replace('.','&#46;')
	#string = string.replace('\"','&#34;')
	#string = string.replace('&','&#38;')
	string = string.replace('ø','&#248;')
	string = string.replace('Ø','&#216;')
	string = string.replace('æ','&#230;')
	string = string.replace('Æ','&#198;')
	string = string.replace('É','&#201;')
	string = string.replace('é','&#233;')
	return string

def DownloadFile(url,path):
	result=urllib2.urlopen(url)
	localFile = open(unicode(path,'utf-8'), 'wb')
	localFile.write(result.read())
	localFile.close()
	# u = urllib2.urlopen(url)
	# localFile = open(path, 'w')
	# localFile.write(u.read())
	# localFile.close()

def GetFanArtBannerURL():
	xbmc.log("GetFanArtBannerURL")
	zip_dir = xbmc.translatePath('special://profile/addon_data/plugin.video.viaplay/tmp/')
	#zip_dir = unicode(zip_dir,'utf-8')
	data_path = os.path.join(zip_dir, "banners.xml")
	xbmc.log("Data_path: " + data_path)
	
	xml = open(unicode(data_path,'utf-8'), 'r').read()
	
	xbmc.log("Parse tree")
	tree = ET.parse(unicode(data_path,'utf-8'))
	xbmc.log("Tree getroot")
	root = tree.getroot()
	xbmc.log("Find all banners")
	banners = root.findall("Banner")
	
	for banner in banners:
		if(banner.find("BannerType").text =="fanart"):
			url = urlparse.urljoin("http://thetvdb.com/banners/",str(banner.find("BannerPath").text).strip())
			xbmc.log("URL: " + url)
			return url
			
	xbmc.log("No banner url was found!")
	return ""

def GetSeries(seriesID):
	url = "http://thetvdb.com/api/5736416B121F48D5/series/"+seriesID+"/all/sv.zip"
	#dir = os.path.dirname(__file__)
	zip_dir = xbmc.translatePath('special://profile/addon_data/plugin.video.viaplay/tmp')
	#zip_dir = str(zip_dir).encode("utf-8")
	zip_path = os.path.join( zip_dir, 'all.zip')
	#zip_path = xbmc.translatePath(os.path.join( 'special://profile/addon_data/plugin.video.viaplay/tmp/', 'all.zip'  ))
	#zip_url = "file:" + urllib.pathname2url(zip_path)
	
	#zip_dir = zip_dir.decode('utf8')
	#zip_path = zip_path.decode('utf8')
	#zip_url = zip_url.decode('utf8')
	
	#zip_dir=unicode(zip_dir,'utf-8')
	#zip_path = unicode(zip_path,'utf-8')
	xbmc.log("Zip_dir: " + zip_dir)
	xbmc.log("Zip_path: " + zip_path)
	#xbmc.log("Zip_url: " + zip_url)
	

	if not os.path.exists(zip_dir.decode('utf-8')):
		xbmc.log("Path does not exist, create folder")
		os.makedirs(zip_dir.decode('utf-8'))

	RemoveFile(zip_path)
	
	xbmc.log("Remove old files before extracting new ones...")
	for the_file in os.listdir(zip_dir.decode('utf-8')):
		file_path = os.path.join(zip_dir.decode('utf-8'), the_file)
		#xbmc.log("Remove file: " + unicode(file_path).decode('utf-8'))
		RemoveFile(file_path)
	
	xbmc.log("Download data from TheTvDb")
	#result = urllib.urlretrieve(url, "all.zip")
	DownloadFile(url,zip_path)
	#xbmc.log("Result: " + result)
	
	#extract_path = os.path.join(dir, "resources" + os.sep + "tvdb")
	data_path = os.path.join(zip_dir, "sv.xml")
	
	#xbmc.log("Open zip-file: " + zip_path)
	zip = zipfile.ZipFile(unicode(zip_path,'utf-8'))
	xbmc.log("Extract zip-file")
	zip.extractall(unicode(zip_dir,'utf-8'))
	
	xbmc.log("Open xml-file")
	xml = open(unicode(data_path,'utf-8'), 'r').read()
	
	xbmc.log("Parse tree")
	tree = ET.parse(unicode(data_path,'utf-8'))
	xbmc.log("Tree getroot")
	root = tree.getroot()
	xbmc.log("Find all episodes")
	episodes = root.findall("Episode")
	
	series=[]
	xbmc.log("Find all series")
	seriesObj = root.findall("Series")
	xbmc.log("Get Series name")
	seriesName = seriesObj[0].find("SeriesName").text
	
	xbmc.log("Add episodes to collection")
	for episode in episodes:
		series.append(TvSeries(episode.find("SeasonNumber").text,episode.find("EpisodeNumber").text,episode.find("EpisodeName").text,episode.find("filename").text,seriesName))
	
	xbmc.log("All episodes added to collection")
	return series

def GetEpisodeName(seasonNo,episodeNo,episodes):
    for episode in episodes:
        if(str(episode.season)==str(seasonNo) and str(episode.episode)==str(episodeNo)):
			if (episode.episodeTitle==None):
				return ""
			else:
				return episode.episodeTitle
				
def GetEpisodeThumbnail(seasonNo,episodeNo,episodes):
    for episode in episodes:
        if(str(episode.season)==str(seasonNo) and str(episode.episode)==str(episodeNo)):
			if (episode.episodeTitle==None):
				return ""
			else:
				return str(episode.filename)

def GetSeriesID(seriesName):
    url ="http://thetvdb.com/api/GetSeries.php?seriesname="+urllib.quote_plus(seriesName)+"&language=sv"
    xbmc.log("TvDb GetSeriesID URL: " +url)
    result=urllib2.urlopen(url)
    xml = result.read()
    xml = xml.replace("\n","")
    xml = EscapeXml(xml)
    
    xbmc.log("TheTvDb GetSeriesID XML: " + xml)
    root = ET.fromstring(xml)
    #root = tree.getroot()
    xbmc.log("Find Series in XML")
    series = root.findall("Series")

    xbmc.log("Check if series is None")
    if(series==None):
        xbmc.log("Returning None")
        return None

    xbmc.log("Check if series is zero")
    if(len(series)<1):
        xbmc.log("Returning None")
        return None
    
    xbmc.log("The length of series is " + str(len(series)))
    xbmc.log("Go through each series")

    for serie in series:
        tvdbName = serie.find('SeriesName').text.lower().encode("utf-8")
        if(tvdbName==seriesName.lower()):
            return str(serie.find("seriesid").text)
        elif seriesName.lower() in tvdbName:
            return str(serie.find("seriesid").text)

def GetSeasonBannerURL(season):
	xbmc.log("GetSeasonBannerURL")
	zip_dir = xbmc.translatePath('special://profile/addon_data/plugin.video.viaplay/tmp/')
	data_path = os.path.join(zip_dir, "banners.xml")
	xbmc.log("Data_path: " + data_path)
	
	xml = open(unicode(data_path,'utf-8'), 'r').read()
	
	xbmc.log("Parse tree")
	tree = ET.parse(unicode(data_path,'utf-8'))
	xbmc.log("Tree getroot")
	root = tree.getroot()
	xbmc.log("Find all banners")
	banners = root.findall("Banner")
	
	for banner in banners:
		if(banner.find("BannerType").text =="season"):
			if(banner.find("Season").text ==str(season)):
				url = urlparse.urljoin("http://thetvdb.com/banners/",str(banner.find("BannerPath").text).strip())
				xbmc.log("URL: " + url)
				return url
			
	xbmc.log("No banner url was found!")
	return ""

def CreateDatabase():
    try:
        checkFile = os.path.join(str(ROOT_FOLDER), 'favorites.db')
        xbmc.log('Path to database: ' + checkFile)
        havefile = os.path.isfile(checkFile)
        if(not havefile):
            con = sqlite.connect(checkFile)
            with con:
                cur = con.cursor()
                cur.execute("CREATE TABLE Favorites(Id INTEGER PRIMARY KEY, Title TEXT, Type TEXT, Url TEXT, Poster TEXT, Year INTEGER, Director TEXT, Desc TEXT);")
                cur.execute("CREATE TABLE Version(Version INTEGER);")
                cur.execute("CREATE TABLE WatchedEpisodes(Id INTEGER PRIMARY KEY, Title TEXT, Season INTEGER, Episode INTEGER);")
                cur.execute("CREATE TABLE TvCache(Id INTEGER PRIMARY KEY, SeriesName TEXT, SeriesId TEXT, DataUrl TEXT, FanArtUrl TEXT);")
                cur.execute("CREATE TABLE WatchedProduct(Id INTEGER PRIMARY KEY, ProductId TEXT);")
                cur.execute("INSERT INTO Version (Version) VALUES(4)")
                
    except:
        xbmc.log("Could not create database")
        return None

def UpgradeDatabase():
    xbmc.log("Check for database upgrade")
    version = DatabaseVersion()
    checkFile = DatabasePath()
    havefile = os.path.isfile(checkFile)
    if(havefile):
        con = sqlite.connect(checkFile)
        with con:
            cur = con.cursor()
            if version =="1":
                cur.execute("CREATE TABLE WatchedEpisodes(Id INTEGER PRIMARY KEY, Title TEXT, Season INTEGER, Episode INTEGER);")
                cur.execute("UPDATE Version SET Version = 2")
                xbmc.log("Database was upgraded to version: 2")
            if version=="2":
                cur.execute("CREATE TABLE TvCache(Id INTEGER PRIMARY KEY, SeriesName TEXT, SeriesId INTEGER, DataUrl TEXT, FanArtUrl TEXT);")
                cur.execute("UPDATE Version SET Version = 3")
                xbmc.log("Database was upgraded to version: 3")
            if version=="3":
                cur.execute("CREATE TABLE WatchedProduct(Id INTEGER PRIMARY KEY, ProductId TEXT);")
                cur.execute("UPDATE Version SET Version = 4")
                xbmc.log("Database was upgraded to version: 4")

def DatabasePath():
	path = os.path.join(ROOT_FOLDER, 'favorites.db')
	return path

# Retrieves the current database version
def DatabaseVersion():
	con = sqlite.connect(DatabasePath())
	with con:
		cur = con.cursor()
		cur.execute("SELECT Version FROM Version")
		rows = cur.fetchall()
		return str(rows[0][0])

# Adds an episode as watched to the database.
def AddWatchedEpisode(title, season, episode):
	path = DatabasePath()
	con = sqlite.connect(path)
	with con:
		cur = con.cursor()
		cur.execute('''INSERT INTO WatchedEpisodes (Title,Season,Episode) VALUES(?,?,?)''', (title,season,episode))

def AddWatchedProduct(productId):

    if productId ==None:
        return ""
    elif len(productId)==0:
        return ""
    
    path = DatabasePath()
    con = sqlite.connect(path)
    with con:
        cur = con.cursor()
        cur.execute("INSERT INTO WatchedProduct (ProductId) VALUES('"+str(productId)+"')")

def AddCachedTV(seriesName,seriesId, dataUrl, fanartUrl):
	try:
		path = DatabasePath()
		con = sqlite.connect(path)
		with con:
			cur = con.cursor()
			cur.execute('''INSERT INTO TvCache (SeriesName,SeriesId,DataUrl,FanArtUrl) VALUES(?,?,?,?)''', (seriesName,seriesId,dataUrl,fanartUrl))
	except:
		xbmc.log("Failed to cache TV series")
		
def RemoveWatchedEpisode(title,season,episode):
	path = DatabasePath()
	con = sqlite.connect(path)
	with con:
		cur = con.cursor()
		cur.execute('''DELETE FROM WatchedEpisodes WHERE Title=? AND Season=? AND Episode=?''',(title,season,episode))

def RemoveWatchedProduct(productId):
	path = DatabasePath()
	con = sqlite.connect(path)
	with con:
		cur = con.cursor()
		cur.execute('''DELETE FROM WatchedProduct WHERE ProductId=?''',(productId))
		
def AddFavorite(title,type,url,poster,year,director,desc):
	path = DatabasePath()#os.path.join(str(ROOT_FOLDER), 'favorites.db')
	con = sqlite.connect(path)
	with con:
		cur = con.cursor()
		cur.execute('''INSERT INTO Favorites (Title,Type,Url,Poster,Year,Director,Desc) VALUES(?,?,?,?,?,?,?)''', (title,type,url,poster,year,director,desc))

def RemoveFavorite(id):
	path = os.path.join(str(ROOT_FOLDER), 'favorites.db')
	con = sqlite.connect(path)
	with con:
		cur = con.cursor()
		cur.execute("DELETE FROM Favorites WHERE Id="+str(id))

def IsWatchedEpisode(title,season,episode):
	path = DatabasePath()
	con = sqlite.connect(path)
	value=False
	
	with con:
		cur = con.cursor()
		cur.execute('''SELECT * FROM WatchedEpisodes WHERE Title=? AND Season=? AND Episode=?''',(unicode(title).encode('utf-8'),season,episode))

		row = cur.fetchone()
		if row is None:
			value=False
		else:
			value=True
	return value

def IsWatchedProduct(productId):

    if productId == None:
        return False

	path = DatabasePath()
	con = sqlite.connect(path)
	value=False
	
	with con:
		cur = con.cursor()
		cur.execute("SELECT * FROM WatchedProduct WHERE ProductId="+str(productId))

		row = cur.fetchone()
		if row is None:
			value=False
		else:
			value=True
	return value

def GetCachedTv(seriesName):
	#try:
	path = DatabasePath()
	con = sqlite.connect(path)
	xbmc.log("GetCachedTv, seriesName: " + seriesName)
	
	with con:
		cur = con.cursor()
		cur.execute("SELECT SeriesName,SeriesId,DataUrl,FanArtUrl FROM TvCache WHERE SeriesName='"+seriesName+"'")

		row = cur.fetchone()
		if row is None:
			return None
		else:
			xbmc.log("Adding class CachedTV")
			return CachedTv(str(row[0]),str(row[1]),str(row[2]),str(row[3]))

	return None
	#except:
		#return None
	
	
def LoadTvFavorites():
	path = DatabasePath()#os.path.join(str(ROOT_FOLDER), 'favorites.db')
	con = sqlite.connect(path)
	with con:
		cur = con.cursor()
		cur.execute("SELECT * FROM Favorites WHERE Type='tv' ORDER BY Title Asc")

		rows = cur.fetchall()

		for row in rows:
			id=str(row[0])
			title = unicode(row[1]).encode('utf-8')
			poster = str(row[4])
			url = str(row[3])
			listItem = xbmcgui.ListItem(title)
			listItem.setThumbnailImage(poster)
			infoLabels = { "Title": title,"tvshowtitle": title }
			listItem.setInfo(type="Video", infoLabels=infoLabels)
			item_url=str(sys.argv[0]) + '?' + "url=" + urllib.quote_plus(url) + "&mode=series&title=" + urllib.quote_plus(title)
			
			cm_url = str(sys.argv[0]) + '?' + "id=" + urllib.quote_plus(id) + "&mode=remove_tv_favorite" + "&title="+urllib.quote_plus(title)
			listItem.addContextMenuItems([(unicode(__language__(4020)).encode('utf-8'), "XBMC.RunPlugin(%s)" % (cm_url),)],replaceItems=True)

			xbmcplugin.addDirectoryItem(thisPlugin,item_url,listItem,isFolder=True)
	xbmc.executebuiltin("Container.SetViewMode(500)")
def ReloadSettings():
	__settings__ = xbmcaddon.Addon(id='plugin.video.viaplay')
	__language__ = __settings__.getLocalizedString
	SETTINGS_COUNTRY = __settings__.getSetting("Country")
		
def GetLinks(url_Type):
	linksDir = os.path.join(RESOURCE_FOLDER, 'links')
	filepath = os.path.join(linksDir, GetLinksFilename())
	#filepath = filepath.decode('utf8')
	#xbmc.log('GetLinks filepath: ' + filepath)
	file = open(filepath,'r')
	data = file.read()
	file.close()
	
	dom = parseString(data)
	test=dom.getElementsByTagName('Links')
	
	links=[]
	for item in test:
		if item.childNodes[1].childNodes[0].nodeValue==url_Type:
			url = FixHtmlString(str(item.childNodes[7].childNodes[0].nodeValue))
			#name = FixHtmlString(unicode(item.childNodes[3].childNodes[0].nodeValue).encode('utf-8'))
			links.append(Link(item.childNodes[1].childNodes[0].nodeValue,item.childNodes[3].childNodes[0].nodeValue,item.childNodes[5].childNodes[0].nodeValue,url))
	return links

def DoesSeriesExistAtTvDb(series_name):
    try:
        t = tvdb_api.Tvdb(language="sv")
        series =  t[unicode(series_name)]
        xbmc.log('DoesSeriesExistAtTvDb: True')
        return True
    except Exception as ex:
        xbmc.log('DoesSeriesExistAtTvDb: False ' + str(ex) + ' series_name = ' + series_name)
        return False

def CreatePlayerCoreFactory(path):
	xml =""
	xml +="<playercorefactory>"
	xml +="<players>"
	xml +="<player name=\"IE\" type=\"ExternalPlayer\">"
	xml +="<filename>"+str(VIAPLAYER_PATH)+"</filename>"
	xml +="<args>-k \"{1}\"</args>"
	xml +="<hidexbmc>false</hidexbmc>"
	xml +="<hideconsole>false</hideconsole>"
	xml +="<warpcursor>none</warpcursor>"
	xml +="</player>"
	xml +="</players>"
	xml +="<rules action=\"prepend\">"
	xml +="<rule name=\"html\" filetypes=\"html\" player=\"IE\" />"
	xml +="</rules>"
	xml +="</playercorefactory>"
	
	f = open(path,'w+')
	f.write(xml)
	f.close()
	
#def checkplayercore():
#	xbmc.log('CheckPlayerCore')
#	checkFile = os.path.join(str(XBMCPROFILE), 'playercorefactory.xml')
#	havefile = os.path.isfile(checkFile)
#	xbmc.log('Path to playercorefactory: ' + checkFile)
#	if(not havefile):
#        #copy file data from addon folder
#		xbmc.log('Platform is: ' + os.name)
#		if(os.name=='nt'):
#			xbmc.log('Create playercorefactory.xml for Windows')
#			CreatePlayerCoreFactory(checkFile)
#			xbmcgui.Dialog().ok( "Viaplay add-on", __language__(4011) ) #You need to restart XBMC before you can use the Viaplay add-on.
#		else:
#			xbmc.log('The platform is not windows, create playercorefactory for other platform')
#			fileWithData = os.path.join(str(RESOURCE_FOLDER), 'playercorefactory.xml')
#			if not os.path.exists('C:\Program Files (x86)'):
#				fileWithData = os.path.join(str(RESOURCE_FOLDER), 'playercorefactory32.xml')
#			if not os.path.exists('C:\Program Files'):
#				fileWithData = os.path.join(str(RESOURCE_FOLDER), 'playercorefactoryOSX.xml')
#				xbmc.log('Create playercorefactoryOSX.xml for Mac OSX')
#			data = open(str(fileWithData),'r').read()
#			f = open(checkFile,'w+')
#			f.write(data)
#			f.close()
    
#def checkadvsettings():
#    checkFile = os.path.join(str(XBMCPROFILE), 'advancedsettings.xml')
#    havefile = os.path.isfile(checkFile)
#    if(not havefile):
#        #copy file from addon folder
#        fileWithData = os.path.join(str(RESOURCE_FOLDER), 'advancedsettings.xml')
#        data = open(str(fileWithData),'r').read()
#        f = open(checkFile,'w+')
#        f.write(data)
#        f.close()

def SortListItems():
	if(not SETTINGS_SORTBYADDED):
		xbmcplugin.addSortMethod( thisPlugin, sortMethod=xbmcplugin.SORT_METHOD_LABEL )
		
def parameters_string_to_dict(param_string):
	params = {}
	
	if param_string:
		pairs = param_string[1:].split("&")

		for pair in pairs:

			split = pair.split('=')

			if (len(split)) == 2:
				params[split[0]] = split[1]
	
	return params

def GetLinksFilename():
    if SETTINGS_USE_ANDROID:
        if SETTINGS_COUNTRY=="0":
            return "viaplay_se_internal.xml"
        elif SETTINGS_COUNTRY=="1":
            return "viaplay_dk_internal.xml"
        elif SETTINGS_COUNTRY=="2":
            return "viaplay_no_internal.xml"
        elif SETTINGS_COUNTRY=="3":
            return "viaplay_fi_internal.xml"

        return "viaplay_se_internal.xml"
    else:
        if SETTINGS_COUNTRY=="0":
            return "viaplay_se.xml"
        elif SETTINGS_COUNTRY=="1":
            return "viaplay_dk.xml"
        elif SETTINGS_COUNTRY=="2":
            return "viaplay_no.xml"
        elif SETTINGS_COUNTRY=="3":
            return "viaplay_fi.xml"

        return "viaplay_se.xml"

def GetLoginUrl(type='pc'):
	if SETTINGS_COUNTRY=="0":
		return "https://login.viaplay.se/api/login/v1?deviceKey="+type+"-se&returnurl=https%3A%2F%2Fcontent.viaplay.se%2F"+type+"-se%2Fstarred&username="
	elif SETTINGS_COUNTRY=="1":
		return "https://login.viaplay.dk/api/login/v1?deviceKey="+type+"-dk&returnurl=https%3A%2F%2Fcontent.viaplay.dk%2F"+type+"-dk%2Fstarred&username="
	elif SETTINGS_COUNTRY=="2":
		return "https://login.viaplay.no/api/login/v1?deviceKey="+type+"-no&returnurl=https%3A%2F%2Fcontent.viaplay.no%2F"+type+"-no%2Fstarred&username="
	elif SETTINGS_COUNTRY=="3":
		return "https://login.viaplay.fi/api/login/v1?deviceKey="+type+"-fi&returnurl=https%3A%2F%2Fcontent.viaplay.fi%2F"+type+"-fi%2Fstarred&username="
		
	return "https://login.viaplay.se/api/login/v1?deviceKey="+type+"-se&returnurl=https%3A%2F%2Fcontent.viaplay.se%2F"+type+"-se%2Fstarred&username="

def GetStarredDomain():
	if SETTINGS_COUNTRY=="0":
		return "https://star.viaplay.se"
	elif SETTINGS_COUNTRY=="1":
		return "https://star.viaplay.dk"
	elif SETTINGS_COUNTRY=="2":
		return "https://star.viaplay.no"
	elif SETTINGS_COUNTRY=="3":
		return "https://star.viaplay.fi"
		
	return "https://star.viaplay.se"

def GetAdultName():
    if SETTINGS_COUNTRY=="0":
        return "erotik"
    elif SETTINGS_COUNTRY=="1":
        return "erotik"
    elif SETTINGS_COUNTRY=="2":
        return "erotikk"
    elif SETTINGS_COUNTRY=="3":
        return "erotiikka"
      
    return "erotik"

def GetAgeVerificationUrl():
	if SETTINGS_COUNTRY=="0":
		return "https://login.viaplay.se/api/ageVerification/v1?deviceKey=pc-se"
	elif SETTINGS_COUNTRY=="1":
		return "https://login.viaplay.dk/api/ageVerification/v1?deviceKey=pc-dk"
	elif SETTINGS_COUNTRY=="2":
		return "https://login.viaplay.no/api/ageVerification/v1?deviceKey=pc-no"
	elif SETTINGS_COUNTRY=="3":
		return "https://login.viaplay.fi/api/ageVerification/v1?deviceKey=pc-fi"
		
	return "https://login.viaplay.se/api/ageVerification/v1?deviceKey=pc-se"

def GetDomain():
	if SETTINGS_COUNTRY=="0":
		return "http://viaplay.se"
	elif SETTINGS_COUNTRY=="1":
		return "http://viaplay.dk"
	elif SETTINGS_COUNTRY=="2":
		return "http://viaplay.no"
	elif SETTINGS_COUNTRY=="3":
		return "http://viaplay.fi"
		
	return "http://viaplay.se"


def GetContentDomain(type='pc'):
    #https://content.viaplay.se/pc-se
	if SETTINGS_COUNTRY=="0":
		return "https://content.viaplay.se/"+type+"-se"
	elif SETTINGS_COUNTRY=="1":
		return "https://content.viaplay.dk/"+type+"-dk"
	elif SETTINGS_COUNTRY=="2":
		return "https://content.viaplay.no/"+type+"-no"
	elif SETTINGS_COUNTRY=="3":
		return "https://content.viaplay.fi/"+type+"-fi"
		
	return "https://content.viaplay.se/"+type+"-se"

def GetStreamUrlForCountry():
	if SETTINGS_COUNTRY=="0":
		return "http://viaplay.se/player?stream="
	elif SETTINGS_COUNTRY=="1":
		return "http://viaplay.dk/player?stream="
	elif SETTINGS_COUNTRY=="2":
		return "http://viaplay.no/player?stream="
	elif SETTINGS_COUNTRY=="3":
		return "http://viaplay.fi/player?stream="
		
	return "http://viaplay.se/player?stream="

def GetTimeDifference():
	if SETTINGS_COUNTRY=="0":
		return 1 #"SE"
	elif SETTINGS_COUNTRY=="1":
		return 1 #"DK"
	elif SETTINGS_COUNTRY=="2":
		return 1 #"NO"
	elif SETTINGS_COUNTRY=="3":
		return 2 #"FI"
		
	return 1 #"SE"
	
def GetWeekdayName(day):
    if day==0: # Monday
        return unicode(__language__(4034)).encode('utf-8')
    elif day==1: # Tuesday
        return unicode(__language__(4035)).encode('utf-8')
    elif day==2: #Wendnesday
        return unicode(__language__(4036)).encode('utf-8')
    elif day==3: # Thursday
        return unicode(__language__(4037)).encode('utf-8')
    elif day==4: # Friday
        return unicode(__language__(4038)).encode('utf-8')
    elif day==5: #Saturday
        return unicode(__language__(4039)).encode('utf-8')
    elif day==6: #Sunday
        return unicode(__language__(4040)).encode('utf-8')

    return unicode(__language__(4034)).encode('utf-8')

def GetCountryFullname():
	if SETTINGS_COUNTRY=="0":
		return "Sweden"
	elif SETTINGS_COUNTRY=="1":
		return "Denmark"
	elif SETTINGS_COUNTRY=="2":
		return "Norway"
	elif SETTINGS_COUNTRY=="3":
		return "Finland"
		
	return "Sweden"

def GetCountry():
	if SETTINGS_COUNTRY=="0":
		return "SE"
	elif SETTINGS_COUNTRY=="1":
		return "DK"
	elif SETTINGS_COUNTRY=="2":
		return "NO"
	elif SETTINGS_COUNTRY=="3":
		return "FI"
		
	return "SE"
	
def GetLanguage():
	if SETTINGS_COUNTRY=="0":
		return "Swedish"
	elif SETTINGS_COUNTRY=="1":
		return "Danish"
	elif SETTINGS_COUNTRY=="2":
		return "Norwegian"
	elif SETTINGS_COUNTRY=="3":
		return "Finnish"
		
	return "Swedish"

def LoadMoviesAlphabeticalJson(url):
    objs=GetJson(url)

    for product in objs['_embedded']['viaplay:blocks'][0]['_embedded']['viaplay:products']:
        if 'title' in product['content']:
            title =unicode(product['content']['title']).encode('utf-8')
            movie_url = str(product['_links']['viaplay:page']['href'])
            #parentalrating=str(product[u'content'][u'parentalRating'])
            productId="0"

            listItem = xbmcgui.ListItem(title)
            infoLabels = { "Title": title,"tvshowtitle": title }
            listItem.setInfo(type="Video", infoLabels=infoLabels)
            item_url=str(sys.argv[0]) + '?' + "url=" + urllib.quote_plus(movie_url) + "&mode=play&productid="+productId+"&contenttype=movie" #&parentalrating="+urllib.quote_plus(parentalrating)
            xbmcplugin.addDirectoryItem(thisPlugin,item_url,listItem,isFolder=False)

    xbmcplugin.addSortMethod( thisPlugin, sortMethod=xbmcplugin.SORT_METHOD_LABEL )
    xbmc.executebuiltin("Container.SetViewMode(50)")

def LoadTvAlphabeticalJson(url):
    objs = GetJson(url)

    for product in objs[u'_embedded'][u'viaplay:blocks'][0][u'_embedded'][u'viaplay:products']:
        title = unicode(product['content']['series']['title']).encode('utf-8')
        item_url = product['_links']['viaplay:page']['href']
        
        listItem = xbmcgui.ListItem(title)
        infoLabels = { "Title": title,"tvshowtitle": title }
        listItem.setInfo(type="Video", infoLabels=infoLabels)
        #item_url=str(sys.argv[0]) + '?' + "url=" + urllib.quote_plus(tv_url) + "&mode=seasons&title=" + urllib.quote_plus(title)
        item_url=str(sys.argv[0]) + '?' + "url=" + urllib.quote_plus(item_url) + "&mode=seasons&title=" + urllib.quote_plus(title)
        xbmcplugin.addDirectoryItem(thisPlugin,item_url,listItem,isFolder=True)

    xbmcplugin.addSortMethod( thisPlugin, sortMethod=xbmcplugin.SORT_METHOD_LABEL )
    xbmc.executebuiltin("Container.SetViewMode(50)")

def LoadTvByAlphabet(url):
	page=urllib2.urlopen(url)
	soup = BeautifulSoup(page.read())
	
	alphabet=soup.findAll('ul', attrs={'class' : 'atoz-list'})
	for letter in alphabet:
		for series in letter.findAll('li'):
			if series.contents[1].name=='h4':
				tv_title= FixHtmlString(unicode(series.contents[1].contents[0].string).encode('utf-8'))
				tv_url = urlparse.urljoin(GetDomain() , str(series.contents[1].contents[0].attrs[0][1]))
				#tv_cover_url=GetSeriesCover(tv_url)
				listItem = xbmcgui.ListItem(tv_title)
				#listItem.setThumbnailImage(tv_cover_url)
				infoLabels = { "Title": tv_title,"tvshowtitle": tv_title }
				listItem.setInfo(type="Video", infoLabels=infoLabels)
				item_url=str(sys.argv[0]) + '?' + "url=" + urllib.quote_plus(tv_url) + "&mode=series"
				xbmcplugin.addDirectoryItem(thisPlugin,item_url,listItem,isFolder=True)
	xbmcplugin.addSortMethod( thisPlugin, sortMethod=xbmcplugin.SORT_METHOD_LABEL )
	xbmc.executebuiltin("Container.SetViewMode(50)")
def LoadMoviesByAlphabet(url):
    #url = "http://viaplay.se/tv/samtliga/17235/alphabetical"
	page=urllib2.urlopen(url)
	soup = BeautifulSoup(page.read())
	
	alphabet=soup.findAll('ul', attrs={'class' : 'atoz-list'})
	for letter in alphabet:
		for series in letter.findAll('li'):
			if series.contents[1].name=='h4':
				movie_title= FixHtmlString(unicode(series.contents[1].contents[0].string).encode('utf-8'))
				movie_url = urlparse.urljoin(GetDomain() , str(series.contents[1].contents[0].attrs[0][1]))
				movie_genre = unicode(series.contents[3].string).encode('utf-8')
				#tv_cover_url=GetSeriesCover(tv_url)
				listItem = xbmcgui.ListItem(movie_title)
				#listItem.setThumbnailImage(tv_cover_url)
				infoLabels = { "Title": movie_title + GetHDTag('',movie_genre,'') }
				listItem.setInfo(type="Video", infoLabels=infoLabels)
				item_url=str(sys.argv[0]) + '?' + "url=" + urllib.quote_plus(movie_url) + "&mode=play&contenttype=movie"
				xbmcplugin.addDirectoryItem(thisPlugin,item_url,listItem,isFolder=False)
	xbmcplugin.addSortMethod( thisPlugin, sortMethod=xbmcplugin.SORT_METHOD_LABEL )
	xbmc.executebuiltin("Container.SetViewMode(50)")
def GetSeriesCover(url):
    page=urllib2.urlopen(url)
    soup = BeautifulSoup(page.read())

    section=soup.findAll('div', attrs={'class' : 'content'})
    return Get_PosterUrl(str(section[0].contents[1].contents[1]))
#Loads a specific view which contains only mixed episodes from different series.
def LoadEpisodesView(url):
	try:
		page=urllib2.urlopen(url)
		soup = BeautifulSoup(page.read())

		items=soup.findAll('ul', attrs={'class' : 'media-list tv clearfix'})
		for item in items:
			for series in item.findAll('li'):
				tv_url = urlparse.urljoin(GetDomain() , str(series.contents[1].attrs[2][1]))
				xbmc.log('Episode url: ' + tv_url)
				tv_title = unicode(series.contents[7].contents[1].contents[1].attrs[1][1]).encode('utf-8')
				tv_image = Get_PosterUrl(str(series.contents[1].contents[1]))
				tv_season = int(GetSeason(series.contents[1].attrs[2][1]))
				tv_episode = int(GetEpisode(series.contents[1].attrs[2][1]))
				tv_synopsis = FixHtmlString(unicode(str(series.contents[7].contents[9].string)).encode('utf-8'))
				listItem = xbmcgui.ListItem(tv_title)
				listItem.setThumbnailImage(tv_image)
				infoLabels = { "Title": tv_title,"tvshowtitle": tv_title,"season": tv_season,"episode": tv_episode,"plotoutline": tv_synopsis,"plot": tv_synopsis}
				listItem.setInfo(type="Video", infoLabels=infoLabels)
				item_url=str(sys.argv[0]) + '?' + "url=" + urllib.quote_plus(tv_url) + "&mode=play"
				xbmcplugin.addDirectoryItem(thisPlugin,item_url,listItem)
		xbmcplugin.addSortMethod( thisPlugin, sortMethod=xbmcplugin.SORT_METHOD_LABEL )
		xbmcplugin.setContent(thisPlugin, 'episodes')
		xbmc.executebuiltin("Container.SetViewMode(504)")
	except Exception as ex:
		xbmc.log("Error in LoadEpisodesView")
		xbmc.log("LoadEpisodesView, URL: " + url)
		#xbmc.log("Error: " + ex)

def SetupSportScheduleMenu(sportEvents,url):
    
    list =[]
    
    locale.setlocale(locale.LC_ALL, '')
    for event in sportEvents:
        day = unicode(event.starttime.strftime('%A %d %B')).encode('utf-8')
        if day not in list:
            list.append(day)
            listItem = xbmcgui.ListItem(day)
            item_url=str(sys.argv[0]) + '?' + "url=" + urllib.quote_plus(url) + "&mode=sportscheduleday&day=" +urllib.quote_plus(day)
            xbmcplugin.addDirectoryItem(thisPlugin,item_url,listItem,isFolder=True)

        

def LoadSportScheduleJson(url):
    
    objs = GetJson(url)
    sportEvents=[]

    timezone = 1 # Time will differ from fi and the rest se,no,dk.

    for block in objs['_embedded']['viaplay:blocks']:
        if block['type']=='dynamicList':
            for product in block['_embedded']['viaplay:products']:
                starttime = iso8601.parse_date(str(product['epg']['start'])) + datetime.timedelta(hours=timezone)
                title = unicode(product['content']['title']).encode('utf-8')
                image_url = str(product['content']['images']['landscape']['url'])
                item_url=str(product['_links']['self']['href'])
                day = int(starttime.date().weekday())
                dayname= GetWeekdayName(day)
                sportEvents.append(SportEvent(starttime,day,dayname,title,image_url,item_url,productid))
                

    
    return sportEvents

def GetTotalPageCountAdultContent(url):
    objs = GetAdultContent(url)
    count = int(objs['_embedded']['viaplay:blocks'][0]['pageCount'])

    return count

def LoadMoviesAdultJson(url):
    #xbmc.log("LoadMoviesAdultJson URL: " + url)
    maxCount = GetTotalPageCountAdultContent(url)

    if '?' in url:
        divider="&"
    else:
        divider="?"

    index=0
    while index < maxCount:
        index =index+1
        new_url = url + divider +"block=1&partial=1&pageNumber="+str(index)
        objs = GetAdultContent(new_url)

        for product in objs[u'_embedded'][u'viaplay:products']:
            title = unicode(product['content']['title']).encode('utf-8')

            if 'people' in product['content']:
                if 'directors' in product['content']['people']:
                    director= unicode(product['content']['people']['directors'][0]).encode('utf-8')
                else:
                    director=[""]

                if 'actors' in product['content']['people']:
                    actors=product['content']['people']['actors']
                else:
                    actors=[""]
            else:
                director=[""]
                actors=[""]

            if 'synopsis' in product['content']:
                synopsis = unicode(product['content']['synopsis']).encode('utf-8')
            else:
                synopsis =""
        
            if 'boxart' in product['content']['images']:
                image_boxart = str(product['content']['images']['boxart']['url'])
            else:
                image_boxart =""

            if 'landscape' in product['content']['images']:
                image_landscape = str(product['content']['images']['landscape']['url'])
            else:
                image_landscape =""

            if 'year' in product['content']['production']:
                prodYear = int(product['content']['production']['year'])
            else:
                prodYear =0

            if 'country' in product['content']['production']:
                prodCountry=unicode(product['content']['production']['country']).encode('utf-8')
            else:
                prodCountry=""

            if 'duration' in product[u'content']:
                if 'milliseconds' in product[u'content'][u'duration']:
                    duration = long(product[u'content'][u'duration'][u'milliseconds'])
                else:
                    duration =0
            else:
                duration=0

            if 'href' in product['_links']['viaplay:page']:
                item_url = str(product['_links']['viaplay:page']['href'])
            else:
                item_url=""
        
            if 'parentalRating' in product[u'content']:
                parentalRating=str(product[u'content'][u'parentalRating'])
            else:
                parentalRating=""
            
            prodId=str(product['system']['productId'])

            listItem = xbmcgui.ListItem(title)

            if item_url.endswith('-hd'):
                overlay=xbmcgui.ICON_OVERLAY_HD
                listItem.setLabel2(" (HD)")
            else:
                overlay=xbmcgui.ICON_OVERLAY_NONE

            listItem.setThumbnailImage(image_boxart)

            infoLabels = { "Title": title,"Genre": "","Year": prodYear,"Director": director,"Cast": actors,"Plot": synopsis,'videoresolution':'','overlay':overlay }
            listItem.setInfo(type="Video", infoLabels=infoLabels)
            movie_url=str(sys.argv[0]) + '?' + "url=" + urllib.quote_plus(item_url) + "&mode=play&productid=" + prodId+"&contenttype=movie&parentalrating="+urllib.quote_plus(parentalRating)
        
            cm_url_remove = str(sys.argv[0]) + '?' + "productid=" + prodId+"&mode=remove_watched"
            cm_url_add = str(sys.argv[0]) + '?' + "productid=" + prodId+"&mode=add_watched"

            menu_txt_MarkAsShown=unicode(__language__(4041)).encode('utf-8')
            menu_txt_MarkNotAsShown=unicode(__language__(4042)).encode('utf-8')

            cm_url_remove_starred = str(sys.argv[0]) + '?' + "productid=" + prodId+"&mode=remove_starred"
            cm_url_add_star = str(sys.argv[0]) + '?' + "productid=" + prodId+"&mode=add_starred"

            menu_txt_AddStar=unicode(__language__(4043)).encode('utf-8')
            menu_txt_RemoveStarred=unicode(__language__(4044)).encode('utf-8')

            #listItem.addContextMenuItems([(menu_txt_MarkAsShown, "XBMC.RunPlugin(%s)" % (cm_url_add),),(menu_txt_MarkNotAsShown, "XBMC.RunPlugin(%s)" % (cm_url_remove),),(menu_txt_AddStar, "XBMC.RunPlugin(%s)" % (cm_url_add_star),),(menu_txt_RemoveStarred, "XBMC.RunPlugin(%s)" % (cm_url_remove_starred),)],replaceItems=True)

            xbmcplugin.addDirectoryItem(thisPlugin,movie_url,listItem)

def LoadMoviesJson(url):
    
    objs = GetJson(url)

    for product in objs[u'_embedded'][u'viaplay:products']:
        title = unicode(product['content']['title']).encode('utf-8')
        xbmc.log("LoadMoviesJson Title: " + title)

        if 'people' in product['content']:
            if 'directors' in product['content']['people']:
                director= unicode(product['content']['people']['directors'][0]).encode('utf-8')
            else:
                director=[""]

            if 'actors' in product['content']['people']:
                actors=product['content']['people']['actors']
            else:
                actors=[""]
        else:
            director=[""]
            actors=[""]

        if 'synopsis' in product['content']:
            synopsis = unicode(product['content']['synopsis']).encode('utf-8')
        else:
            synopsis =""
        
        if 'boxart' in product['content']['images']:
            image_boxart = str(product['content']['images']['boxart']['url'])
        else:
            image_boxart =""

        if 'landscape' in product['content']['images']:
            image_landscape = str(product['content']['images']['landscape']['url'])
        else:
            image_landscape =""

        if 'year' in product['content']['production']:
            prodYear = int(product['content']['production']['year'])
        else:
            prodYear =0

        if 'country' in product['content']['production']:
            prodCountry=unicode(product['content']['production']['country']).encode('utf-8')
        else:
            prodCountry=""

        if 'duration' in product[u'content']:
            if 'milliseconds' in product[u'content'][u'duration']:
                duration = long(product[u'content'][u'duration'][u'milliseconds'])
            else:
                duration =0
        else:
            duration=0

        if 'href' in product['_links']['viaplay:page']:
            item_url = str(product['_links']['viaplay:page']['href'])
        else:
            item_url=""
        
        if 'parentalRating' in product[u'content']:
            parentalRating=str(product[u'content'][u'parentalRating'])
        else:
            parentalRating=""
            
        #parentalRating = str(product[u'content'][u'parentalRating'])

        #product[u'system'][u'productId']
        #if 'productId' in product['system']:
        prodId=str(product['system']['productKey'])
        #else:
        #    prodId=""

        strmSeriesTitle=""
        strmEpisodeName = title
        strmImage=image_boxart

        listItem = xbmcgui.ListItem(title)

        if item_url.endswith('-hd'):
            overlay=xbmcgui.ICON_OVERLAY_HD
            listItem.setLabel2(" (HD)")
        else:
            overlay=xbmcgui.ICON_OVERLAY_NONE

        listItem.setThumbnailImage(image_boxart)

        infoLabels = { "Title": title,"Genre": "","Year": prodYear,"Director": director,"Cast": actors,"Plot": synopsis,'videoresolution':'','overlay':overlay }
        listItem.setInfo(type="Video", infoLabels=infoLabels)
        movie_url=str(sys.argv[0]) + '?' + "url=" + urllib.quote_plus(item_url) + "&mode=play&productid=" + prodId+"&contenttype=movie&parentalrating="+urllib.quote_plus(parentalRating) + "&strmtitle=" + urllib.quote_plus(strmSeriesTitle)+"&strmname="+urllib.quote_plus(strmEpisodeName)+"&strmimage="+urllib.quote_plus(strmImage)
        
        cm_url_remove = str(sys.argv[0]) + '?' + "productid=" + prodId+"&mode=remove_watched"
        cm_url_add = str(sys.argv[0]) + '?' + "productid=" + prodId+"&mode=add_watched"

        menu_txt_MarkAsShown=unicode(__language__(4041)).encode('utf-8')
        menu_txt_MarkNotAsShown=unicode(__language__(4042)).encode('utf-8')

        cm_url_remove_starred = str(sys.argv[0]) + '?' + "productid=" + prodId+"&mode=remove_starred"
        cm_url_add_star = str(sys.argv[0]) + '?' + "productid=" + prodId+"&mode=add_starred"

        menu_txt_AddStar=unicode(__language__(4043)).encode('utf-8')
        menu_txt_RemoveStarred=unicode(__language__(4044)).encode('utf-8')

        listItem.addContextMenuItems([(menu_txt_MarkAsShown, "XBMC.RunPlugin(%s)" % (cm_url_add),),(menu_txt_MarkNotAsShown, "XBMC.RunPlugin(%s)" % (cm_url_remove),),(menu_txt_AddStar, "XBMC.RunPlugin(%s)" % (cm_url_add_star),),(menu_txt_RemoveStarred, "XBMC.RunPlugin(%s)" % (cm_url_remove_starred),)],replaceItems=True)


        xbmcplugin.addDirectoryItem(thisPlugin,movie_url,listItem)

def GetEpisodesJson(url,fanarturl):
    xbmc.log("GetEpisodesJson URL: " + url)
    objs = GetJson(url)

    if SETTINGS_USE_ANDROID:
        seriesTitle =unicode(objs[u'_embedded'][u'viaplay:blocks'][0][u'_embedded'][u'viaplay:article'][u'content'][u'title']).encode('utf-8')
    else:
        seriesTitle = unicode(objs['_embedded']['viaplay:products'][0]['content']['title']).encode('utf-8')

    episodes=None

    if(SETTINGS_USETVDB):
        id=GetSeriesID(seriesTitle)

        if(id!=None):
            xbmc.log("ID is not None")
            xbmc.log("TheTvDb Series ID: "+id)
            episodes=GetSeries(id)
            fanArtUrl = GetFanArtBannerURL()
        else:
            xbmc.log("ID is None!")

    if SETTINGS_USE_ANDROID:
        items =objs['_embedded']['viaplay:blocks'][1]
    else:
        items = objs

    for obj in items['_embedded']['viaplay:products']:
        if obj['type']=='episode':
            episodeNo=int(obj['content']['series']['episodeNumber'])
            seasonNo=int(obj['content']['series']['season']['seasonNumber'])
            seasonName = unicode(obj['content']['series']['season']['title']).encode('utf-8')
            title = unicode(obj['content']['series']['episodeTitle']).encode('utf-8') #+ " " + str(episodeNo)
            synopsis=unicode(obj['content']['synopsis']).encode('utf-8')
            image_url=str(obj['content']['images']['landscape']['url'])
            episode_url=str(obj['_links']['self']['href'])
            
            if 'productId' in obj['system']:
                productId=str(obj['system']['productId'])
            else:
                productId=""

            tmpTitle=""

            if(episodes!=None):
                xbmc.log("Episode no: " + str(episodeNo))
                xbmc.log("Season no: " + str(seasonNo))
                episode_Name=FormatValue(GetEpisodeName(seasonNo,episodeNo,episodes))
                tmpTitle=episode_Name

                if(episode_Name=="None"):
                    xbmc.log("episode_Name is None!")
                    episode_Name = title
                else:
                    episode_Name=str(episodeNo) + ". " + episode_Name
            else:
                episode_Name=title

            if IsWatchedProduct(productId):
                overlay=xbmcgui.ICON_OVERLAY_WATCHED & xbmcgui.ICON_OVERLAY_HD
                playcount=1
            else:
                overlay=xbmcgui.ICON_OVERLAY_UNWATCHED
                playcount=0

            if len(tmpTitle)==0:
                tmpTitle=episode_Name

            strmSeriesTitle=seriesTitle+" ("+str(seasonNo)+"x"+str(episodeNo)+")"
            strmEpisodeName = tmpTitle
            strmImage=image_url

            listItem = xbmcgui.ListItem(episode_Name)
            listItem.setThumbnailImage(image_url)
            listItem.setProperty("Fanart_Image", fanarturl)
            infoLabels = { "Title": episode_Name,"tvshowtitle": episode_Name,"season": seasonNo,"episode": episodeNo,"plotoutline": synopsis,"plot": synopsis,"overlay":overlay,"playcount":playcount}
            listItem.setInfo(type="Video", infoLabels=infoLabels)
            item_url=str(sys.argv[0]) + '?' + "url=" + urllib.quote_plus(episode_url) + "&mode=play&productid=" + productId+"&contenttype=tv" + "&strmtitle=" + urllib.quote_plus(strmSeriesTitle)+"&strmname="+urllib.quote_plus(strmEpisodeName)+"&strmimage="+urllib.quote_plus(strmImage)

            cm_url_remove = str(sys.argv[0]) + '?' + "productid=" + productId+"&mode=remove_watched"
            cm_url_add = str(sys.argv[0]) + '?' + "productid=" + productId+"&mode=add_watched"

            menu_txt_MarkAsShown=unicode(__language__(4041)).encode('utf-8')
            menu_txt_MarkNotAsShown=unicode(__language__(4042)).encode('utf-8')

            cm_url_remove_starred = str(sys.argv[0]) + '?' + "productid=" + productId+"&mode=remove_starred"
            cm_url_add_star = str(sys.argv[0]) + '?' + "productid=" + productId+"&mode=add_starred"

            menu_txt_AddStar=unicode(__language__(4043)).encode('utf-8')
            menu_txt_RemoveStarred=unicode(__language__(4044)).encode('utf-8')

            listItem.addContextMenuItems([(menu_txt_MarkAsShown, "XBMC.RunPlugin(%s)" % (cm_url_add),),(menu_txt_MarkNotAsShown, "XBMC.RunPlugin(%s)" % (cm_url_remove),),(menu_txt_AddStar, "XBMC.RunPlugin(%s)" % (cm_url_add_star),),(menu_txt_RemoveStarred, "XBMC.RunPlugin(%s)" % (cm_url_remove_starred),)],replaceItems=True)

            xbmcplugin.addDirectoryItem(thisPlugin,item_url,listItem)

    xbmcplugin.addSortMethod( thisPlugin, sortMethod=xbmcplugin.SORT_METHOD_LABEL )
    xbmcplugin.setContent(thisPlugin, 'episodes')
    xbmc.executebuiltin("Container.SetViewMode(504)")

def GetSeasonsJson(url):
    xbmc.log("GetSeasonsJson URL: " + url)
    objs = GetJson(url)

    title = unicode(objs['_embedded']['viaplay:blocks'][0]['title']).encode('utf-8')
    seasonPosterUrl = str(objs['_embedded']['viaplay:blocks'][0]['_embedded']['viaplay:article']['content']['images']['boxart']['url'])
    fanArtUrl = str(objs['_embedded']['viaplay:blocks'][0]['_embedded']['viaplay:article']['content']['images']['landscape']['url'])

    xbmc.log("GetSeasonsJson title: " + title)

    if(SETTINGS_USETVDB):
        id=GetSeriesID(title)

        if(id!=None):
            xbmc.log("ID is not None")
            xbmc.log("TheTvDb Series ID: "+id)
            GetSeries(id)
            fanArtUrl = GetFanArtBannerURL()
        else:
            xbmc.log("ID is None!")

    for obj in objs['_embedded']['viaplay:blocks']:
        if obj['type']=='season-list':
            
            if SETTINGS_USE_ANDROID:
                season = unicode(__language__(4024)).encode('utf-8') + " " + str(obj['title'])
                url = urllib.quote_plus(objs['_links']['self']['href'])
                url = url + urllib.quote_plus("?seasonNumber=" + str(obj['title']))
            else:
                season = unicode(__language__(4024)).encode('utf-8') + " " + str(obj['title'])
                url = urllib.quote_plus(obj['_links']['self']['href'])
                 
            listItem = xbmcgui.ListItem(season)
            
            if(SETTINGS_USETVDB):
                if(id!=None):
                    if SETTINGS_USE_ANDROID:
                        seasonPosterUrlNew = GetSeasonBannerURL(int(obj['title']))
                    else:
                        seasonPosterUrlNew = GetSeasonBannerURL(int(obj['title']))

                    if seasonPosterUrlNew !=None:
                        seasonPosterUrl=seasonPosterUrlNew
                        
                    listItem.setThumbnailImage(seasonPosterUrl)
                    listItem.setProperty("Fanart_Image", fanArtUrl)
                else:
                    listItem.setThumbnailImage(seasonPosterUrl)
                    listItem.setProperty("Fanart_Image", fanArtUrl)
                    
            else:
                listItem.setThumbnailImage(seasonPosterUrl)
                listItem.setProperty("Fanart_Image", fanArtUrl)
                
            xbmc.log("Title: " + title + " Season: " + season + " url: " + url)
            item_url=str(sys.argv[0]) + '?' + "url=" + url + "&mode=episodes&title=" + urllib.quote_plus(title) + "&fanart=" + urllib.quote_plus(fanArtUrl)
            xbmcplugin.addDirectoryItem(thisPlugin,item_url,listItem,isFolder=True)
    SortListItems()
    xbmc.executebuiltin("Container.SetViewMode(50)")

def GetInternalPlaybackImage(url):
    objs = GetJson(url)
    type = objs['_embedded']['viaplay:blocks'][0]['_embedded']['viaplay:product']['type']

    if type=='episode':
        return objs['_embedded']['viaplay:blocks'][0]['_embedded']['viaplay:product']['content']['images']['landscape']['url']
    elif type=='movie':
        return objs['_embedded']['viaplay:blocks'][0]['_embedded']['viaplay:product']['content']['images']['boxart']['url']
    else:
        return ""

def LoadTvSeriesJson(url):
    
    objs = GetJson(url)

    for o in objs['_embedded']['viaplay:products']: #objs['_embedded']['viaplay:blocks'][0][u'_embedded'][u'viaplay:products']:
        title= unicode(o['content']['series']['title']).encode('utf-8')
        synopsis = unicode(o['content']['series']['synopsis']).encode('utf-8')
        tv_url = str(o['_links']['viaplay:page']['href']) # holds the content for the series
        
        if 'landscape' in o['content']['images']:
            tv_image= unicode(o['content']['images']['landscape']['url']).encode('utf-8')
        else:
            tv_image=os.path.join(RESOURCE_FOLDER, 'viaplay.png')

        listItem = xbmcgui.ListItem(title)
        listItem.setThumbnailImage(tv_image)
        infoLabels = { "Title": title,"tvshowtitle": title }
        listItem.setInfo(type="Video", infoLabels=infoLabels)
        item_url=str(sys.argv[0]) + '?' + "url=" + urllib.quote_plus(tv_url) + "&mode=seasons&title=" + urllib.quote_plus(title)
        cm_url = str(sys.argv[0]) + '?' + "title=" + urllib.quote_plus(title) + "&mode=add_tv_favorite" + "&url="+urllib.quote_plus(tv_url) +"&poster=" + urllib.quote_plus(tv_image)
        menu_title = unicode(__language__(4019)).encode('utf-8')
        listItem.addContextMenuItems([(menu_title, "XBMC.RunPlugin(%s)" % (cm_url),)],replaceItems=True)

        xbmcplugin.addDirectoryItem(thisPlugin,item_url,listItem,isFolder=True)

def GetShowData(name):
	db = tvdb_api.Tvdb(cache = True,language="sv",apikey="5736416B121F48D5") #,apikey="5736416B121F48D5"
	#db = tvDb(cache = True,language='sv')
	xbmc.log("Tvdb type:" + str(type(db)))
	return db[name]
	
def LoadTvSeries(url):
    #url="http://viaplay.se/tv"
	page=urllib2.urlopen(url)
	soup = BeautifulSoup(page.read())
	#DoesSeriesExistAtTvDb('Fringe')
	#show = tvDb["Fringe"]
	#xbmc.log("Epsiode name: " + show[1][1])
	
	items=soup.findAll('ul', attrs={'class' : 'media-list tv clearfix'})
	for item in items:
		for series in item.findAll('li'):
			tv_devices = "" #str(series.attrs[2][1])
			Is_IosWeb= bool(tv_devices.find("iosweb") >0)
			
			if(SETTINGS_USE_IPAD==True):
				if(Is_IosWeb==False):
					continue
			
			tv_url = urlparse.urljoin(GetDomain(), str(series.contents[1].attrs[2][1])) #GetDomain() + '/' + str(series.contents[1].attrs[2][1])
			tv_title = unicode(series.contents[7].contents[1].contents[1].attrs[1][1]).encode('utf-8')
			tv_image = Get_PosterUrl(str(series.contents[1].contents[1]))
			xbmc.log("tv_image url: " + tv_image)
			tv_image = DownloadPoster(tv_image,"tv")
			listItem = xbmcgui.ListItem(tv_title)
			listItem.setThumbnailImage(tv_image)
			infoLabels = { "Title": tv_title,"tvshowtitle": tv_title }
			listItem.setInfo(type="Video", infoLabels=infoLabels)
			item_url=str(sys.argv[0]) + '?' + "url=" + urllib.quote_plus(tv_url) + "&mode=series&title=" + urllib.quote_plus(tv_title)
			cm_url = str(sys.argv[0]) + '?' + "title=" + urllib.quote_plus(tv_title) + "&mode=add_tv_favorite" + "&url="+urllib.quote_plus(tv_url) +"&poster=" + urllib.quote_plus(tv_image)
			menu_title = unicode(__language__(4019)).encode('utf-8')
			listItem.addContextMenuItems([(menu_title, "XBMC.RunPlugin(%s)" % (cm_url),)],replaceItems=True)
			
			xbmcplugin.addDirectoryItem(thisPlugin,item_url,listItem,isFolder=True)
	#xbmcplugin.addSortMethod( thisPlugin, sortMethod=xbmcplugin.SORT_METHOD_LABEL )
	SortListItems()
	#xbmcplugin.setContent(thisPlugin, 'tvshows')
	xbmc.executebuiltin("Container.SetViewMode(500)")
def GetShowData(name):
	db = tvdb_api.Tvdb(cache = True,language="sv",apikey="5736416B121F48D5") #,apikey="5736416B121F48D5"
	#db = tvDb(cache = True,language='sv')
	xbmc.log("Tvdb type:" + str(type(db)))
	return db[name]

def CheckURL(url):
	if(url.find("episode") >-1):
		return GetSeriesUrlFromEpisode(url)
	elif(url.find("season")>-1):
		newUrl=""
		list = url.split("/")
		for item in list:
			if item.find("season-") ==-1:
				if(str(item)=="http:"):
					newUrl = "http:/"
				else:
					newUrl += str(item)+"/"
			else:
				return newUrl
	else:
		return url
	
def GetSeriesUrlFromEpisode(url):
    try:
        page=urllib2.urlopen(url)
        soup = BeautifulSoup(page.read())
        result = soup.findAll('dd',attrs={'data-metadata-type':'format'})
        return str(result[0].contents[0].attrs[1][1])
    except:
        return ""
	
def LoadEpisodes(url,seriesName):
	try:
		xbmc.log("LoadEpisoded URL: " + url)
		url = CheckURL(url)
		xbmc.log("Url after CheckUrl: " + url)
		xbmc.log("GetFanArt from url")
		url_fan_art=GetFanArt(url)
		xbmc.log("FanArtUrl: " + url_fan_art)

		page=urllib2.urlopen(url)
		soup = BeautifulSoup(page.read())
		#fanart = soup.findAll('div',attrs={'class':'content'})
		seasons=soup.findAll('div', attrs={'class' : 'media-wrapper seasons'})
		fanArtUrl=""
		
		xbmc.log("Step1")
		if(SETTINGS_USETVDB):
			xbmc.log("Call to GetCachedTv")
			cachedTv=GetCachedTv(seriesName)

			if(cachedTv==None):
				xbmc.log("No cached TVdb id was found")
				id=GetSeriesID(seriesName)
			else:
				xbmc.log("Using cached TVdb ID")
				id=cachedTv.seriesId

			if(id!=None):
				xbmc.log("ID is not None")
				xbmc.log("TheTvDb Series ID: "+id)
				episodes=GetSeries(id)
				if(cachedTv==None):
					xbmc.log("Downloading fanart from the TVdb")
					fanArtUrl = GetFanArtBannerURL()
					xbmc.log("Add tv series to cache")
					dataUrl = "http://thetvdb.com/api/5736416B121F48D5/series/"+id+"/all/sv.zip"
					AddCachedTV(seriesName,id, dataUrl, fanArtUrl)
				else:
					xbmc.log("Using cached fanart")
					fanArtUrl=cachedTv.fanartUrl
			else:
				xbmc.log("ID is None")
				episodes=None
		else:
			episodes=None
		
		for season in seasons:
			for episode in season.findAll('li'):
				xbmc.log("Step2")
				episode_url =  urlparse.urljoin(GetDomain() , str(episode.contents[1].attrs[2][1]))
				xbmc.log('Episode url: ' + episode_url)
				#test = episode.contents[1].contents[3].contents[0]
				try:
					title = str(episode.contents[1].contents[3].contents[0]).encode('utf-8')
				except UnicodeDecodeError:
					title = str(episode.contents[1].contents[3].contents[0]).decode('utf-8')
				else:
					title = episode.contents[1].contents[3].contents[0]
				episode_image = Get_PosterUrl(str(episode.contents[1].contents[1]))
				try:
					episode_season = int(GetSeason(episode.contents[1].attrs[2][1]))
				except:
					episode_season=1
				try:
					episode_no = int(GetEpisode(episode_url))
				except:
					episode_no=1
				
				url_title = GetTitleFromUrl(str(episode.contents[1].attrs[2][1]))
				if IsWatchedEpisode(url_title,episode_season,episode_no):
					overlay=xbmcgui.ICON_OVERLAY_WATCHED
					playcount=1
				else:
					overlay=xbmcgui.ICON_OVERLAY_UNWATCHED
					playcount=0

				episode_synopsis = FixHtmlString(unicode(str(episode.contents[7].contents[9].string)).encode('utf-8'))
				episode_title = unicode(__language__(4024)).encode('utf-8') + str(episode_season) + " " + unicode(__language__(4025)).encode('utf-8') + str(episode_no)#title
				
				if(episodes!=None):
					episode_Name=FormatValue(GetEpisodeName(episode_season,episode_no,episodes))
					if(episode_Name=="None"):
						episode_Name=None
					#episode_Name= str(GetEpisodeName(episode_season,episode_no,episodes)).encode('utf-8')
					# try:
						# episode_Name= unicode(GetEpisodeName(episode_season,episode_no,episodes)).encode('utf-8')
					# except UnicodeDecodeError:
						# episode_Name= str(GetEpisodeName(episode_season,episode_no,episodes)).decode('utf-8')
					# else:
						# episode_Name= GetEpisodeName(episode_season,episode_no,episodes)

					if(episode_Name!=None):
						episode_title = episode_title + " - " + episode_Name
					episode_thumbnail = GetEpisodeThumbnail(episode_season,episode_no,episodes)
					if(episode_thumbnail!=None):
						episode_image="http://thetvdb.com/banners/"+episode_thumbnail
				listItem = xbmcgui.ListItem(title)
				xbmc.log("episode_image: " + episode_image)
				episode_image=DownloadPoster(episode_image,"movie") #use the movie instead of tv because the type movie get's the correct image.
				listItem.setThumbnailImage(episode_image)
				
				url_fan_art_downloaded=DownloadPoster(url_fan_art,"fanart")

				if(SETTINGS_USETVDB):
					xbmc.log("UseTvDb FanArtUrl: " + fanArtUrl)
					if(len(fanArtUrl) > 0):
						fanArtUrl=DownloadPoster(fanArtUrl,"movie")
						listItem.setProperty("Fanart_Image", fanArtUrl)
					else:
						listItem.setProperty("Fanart_Image", url_fan_art_downloaded)
				else:
					listItem.setProperty("Fanart_Image", url_fan_art_downloaded)
				
				IpadInfo="&season=" + urllib.quote_plus(str(episode_season)) +"&episode="+ urllib.quote_plus(str(episode_no)) + "&image="+urllib.quote_plus(episode_image)
				infoLabels = { "Title": episode_title,"tvshowtitle": title,"season": episode_season,"episode": episode_no,"plotoutline": episode_synopsis,"plot": episode_synopsis,"overlay":overlay,"playcount":playcount}
				listItem.setInfo(type="Video", infoLabels=infoLabels)
				item_url=str(sys.argv[0]) + '?' + "url=" + urllib.quote_plus(episode_url) + "&mode=play" + IpadInfo
				
				cm_url_remove = str(sys.argv[0]) + '?' + "season=" + urllib.quote_plus(str(episode_season)) +"&episode="+ urllib.quote_plus(str(episode_no)) +"&mode=remove_watched_episode" + "&title="+urllib.quote_plus(url_title)
				cm_url_add = str(sys.argv[0]) + '?' + "season=" + urllib.quote_plus(str(episode_season)) +"&episode="+ urllib.quote_plus(str(episode_no)) +"&mode=add_watched_episode" + "&title="+urllib.quote_plus(url_title)
				listItem.addContextMenuItems([("Markera som visad", "XBMC.RunPlugin(%s)" % (cm_url_add),),("Markera som inte visad", "XBMC.RunPlugin(%s)" % (cm_url_remove),)],replaceItems=True)
				
				xbmcplugin.addDirectoryItem(thisPlugin,item_url,listItem)
				xbmcplugin.addSortMethod( thisPlugin, sortMethod=xbmcplugin.SORT_METHOD_LABEL )
		xbmcplugin.setContent(thisPlugin, 'episodes')
		xbmc.executebuiltin("Container.SetViewMode(504)")
	except Exception as ex:
		raise ex
		xbmc.log("Error in LoadEpisodes")
		xbmc.log("LoadEpisodes, URL: " + url)

def FormatValue(text):
	value=""
	try:
		value= unicode(text).encode('utf-8')
	except UnicodeDecodeError:
		try:
			value= str(text).decode('utf-8')
		except:
			value= text
	
	return value
		
def Get_FanArtUrl(value):
	list=value.split("\"")
	return str(list[3])

def GetFanArt(url):
    try:
        page=urllib2.urlopen(url)
        soup = BeautifulSoup(page.read())
        fanart = soup.findAll('img',attrs={'property':'image'})
        url_fan_art=str(fanart[0])
        list=url_fan_art.split("\"")
        return list[3]
    except:
        return ""
	
def GetTitleFromUrl(value):
	list=value.split("/")
	return str(list[2])
	
def GetSeason(value):
	list=value.split("/")
	for item in list:
		if item.find("season-") >-1:
			season = str(item).replace("season-","")
			return season

def GetEpisode(value):
	list=value.split("/")
	for item in list:
		if item.find("episode-") >-1:
			episode = str(item).replace("episode-","")
			if episode.find("-") > -1:
				episode=episode[:1]
			return episode

def LoadLiveSports(url):
    objs=GetJson(url)

    for block in objs['_embedded']['viaplay:blocks']:
        for product in block['_embedded']['viaplay:products']:
            title=unicode(product['content']['title']).encode('utf-8')
            image_url=str(product['content']['images']['landscape']['url'])
            item_url = str(product['_links']['self']['href'])
            producttime = iso8601.parse_date(str(product['epg']['start'])) + datetime.timedelta(hours=GetTimeDifference())
            starttime=producttime.strftime('%Y-%m-%d %H:%M')
            title = title + " (" + starttime +")"
            synopsis=unicode(product['content']['synopsis']).encode('utf-8')
            genre=unicode(product['_links']['viaplay:genres'][0]['title']).encode('utf-8')
            productId=str(product[u'system'][u'productId'])

            xbmc.log("Title: "  + title)
            xbmc.log("Genre: "  + genre)
            xbmc.log("Plot: "  + synopsis)
            xbmc.log("Date: "  + str(producttime))

            listItem = xbmcgui.ListItem(title)
            listItem.setThumbnailImage(image_url)
            listItem.setLabel2(starttime)
            infoLabels = { "Title": title,"Genre": genre,"Plot": synopsis,'Date': str(producttime) }#"Year": 0,"Director": "","Cast": "",
            listItem.setInfo(type="Video", infoLabels=infoLabels)
            cmd_url=str(sys.argv[0]) + '?' + "url=" + urllib.quote_plus(item_url) + "&mode=play&contenttype=sport&productid=" + productId
            xbmcplugin.addDirectoryItem(thisPlugin,cmd_url,listItem)
            xbmcplugin.addSortMethod( thisPlugin, sortMethod=xbmcplugin.SORT_METHOD_DATE )
            xbmcplugin.addSortMethod( thisPlugin, sortMethod=xbmcplugin.SORT_METHOD_TITLE )
    xbmc.executebuiltin("Container.SetViewMode(500)")
    xbmc.executebuiltin("Container.SetSortMethod(3)")    



def LoadLiveSportsOLD(url):
	xbmc.log("LoadLiveSports URL: " +url)
	page=urllib2.urlopen(url)
	soup = BeautifulSoup(page.read())
	sports=soup.findAll('ul', attrs={'class' : 'media-list sport clearfix'})
	for sport in sports:
		for item in sport.findAll('li'):
			sport_url = urlparse.urljoin(GetDomain() , str(item.contents[7].contents[1].contents[1].attrs[2][1]))
			sport_title = FixHtmlString(unicode(item.contents[1].contents[3].string).encode("utf-8"))
			sport_image = Get_PosterUrl(str(item.contents[1].contents[1]))
			xbmc.log("Sport_image: " + sport_image)
			sport_image=DownloadPoster(sport_image,"sports")
			sport_hd = str(item.contents[3].contents[7].string)
			sport_genre=unicode(item.contents[7].contents[3].contents[0].string).encode("utf-8")
			sport_starttime = str(item.contents[7].contents[7].contents[1].string)
			sport_startdate = Get_DateTime(unicode(item.contents[7].contents[1].contents[1].attrs[1][1]).encode("utf-8"))
			sport_desc = FixHtmlString(unicode(item.contents[7].contents[9].string).encode("utf-8"))
			if(IsHD("",sport_hd,"")):
				overlay=xbmcgui.ICON_OVERLAY_HD
			else:
				overlay=xbmcgui.ICON_OVERLAY_NONE
			sport_title = sport_title + " (" + sport_startdate + ")"
			listItem = xbmcgui.ListItem(sport_title)
			listItem.setThumbnailImage(sport_image)
			listItem.setLabel2(sport_startdate)
			infoLabels = { "Title": sport_title,"Genre": sport_genre,"Year": 0,"Director": "","Cast": "","Plot": sport_desc,'Date': Get_Date(sport_startdate),'overlay':overlay }
			listItem.setInfo(type="Video", infoLabels=infoLabels)
			cmd_url=str(sys.argv[0]) + '?' + "url=" + urllib.quote_plus(sport_url) + "&mode=play"
			xbmcplugin.addDirectoryItem(thisPlugin,cmd_url,listItem)
			xbmcplugin.addSortMethod( thisPlugin, sortMethod=xbmcplugin.SORT_METHOD_DATE )
			xbmcplugin.addSortMethod( thisPlugin, sortMethod=xbmcplugin.SORT_METHOD_TITLE )
	#xbmcplugin.setContent(thisPlugin, 'movies')
	xbmc.executebuiltin("Container.SetViewMode(500)")
	xbmc.executebuiltin("Container.SetSortMethod(3)")

def Get_DateTime(value):
    list=value.split(" ")
    return str(list[0]+ " " + list[1])

def Get_Date(value):
    list=value.split(" ")
    return str(list[0])

def LoadLiveSportScheduleGetDays(url):
    sportEvents=LoadSportScheduleJson(url)
    list =[]
    
    xbmc.log("LoadLiveSportScheduleGetDays url: " + url)

    locale.setlocale(locale.LC_ALL, '')
    for event in sportEvents:
        day = event.dayname + " " + event.starttime.strftime('%d %B')
        xbmc.log("Day: " + day)
        if day not in list:
            list.append(day)
            item_url =str(sys.argv[0]) + '?' + "mode=sport_schedule_day&url="+urllib.quote_plus(url)+"&id=" +urllib.quote_plus(day)
            AddListItem(day,item_url,True)

    xbmc.executebuiltin("Container.SetViewMode(50)")

def LoadLiveSportScheduleForSpecificDay(url,id):
    sportEvents = LoadSportScheduleJson(url)

    for event in sportEvents:
        day = event.dayname + " " + event.starttime.strftime('%d %B')
        if day == id:
            title = event.starttime.strftime('%H:%M') + " - " + event.title
            listItem = xbmcgui.ListItem(title)
            listItem.setThumbnailImage(event.image_url)
            cmd_url=str(sys.argv[0]) + '?' + "url=" + urllib.quote_plus(event.item_url) + "&mode=play&contenttype=sport&productid="+ str(event.productId)
            xbmcplugin.addDirectoryItem(thisPlugin,cmd_url,listItem)

def LoadMovieView(url):
	#url="http://viaplay.se/film/samtliga/250/most_popular"
	#url="http://viaplay.se/film/hd-filmer/8704"
	listing = []
	page=urllib2.urlopen(url)
	soup = BeautifulSoup(page.read())
	movies=soup.findAll('ul', attrs={'class' : 'media-list movies clearfix'})
	for eachmovie in movies:
		for tmp in eachmovie.findAll('li'):
			
			movie_devices = "" #str(tmp.attrs[2][1])
			Is_IosWeb= bool(movie_devices.find("iosweb") >0)
			
			if(SETTINGS_USE_IPAD==True):
				if(Is_IosWeb==False):
					continue
			
			movie_genre = str(tmp.contents[7].contents[3].contents[0].string).replace('/',',')
			try:
				movie_year = int(tmp.contents[7].contents[5].contents[1].string)
			except:
				movie_year=0
			movie_actors = str(tmp.contents[7].contents[9].string).replace('Skådespelare: ','').split(',')
			movie_director = str(tmp.contents[7].contents[11].string).replace('Regissör: ','')
			movie_url=urlparse.urljoin(GetDomain(),str(tmp.contents[1].attrs[2][1]))
			genre = tmp.contents[3].contents[1].contents[1]
			pushHD=tmp.contents[3].contents[7]
			if(IsHD(movie_url,genre,pushHD)):
				overlay=xbmcgui.ICON_OVERLAY_HD
			else:
				overlay=xbmcgui.ICON_OVERLAY_NONE
			
			title = unicode(tmp.contents[7].contents[1].contents[1].attrs[1][1]).encode("utf-8") + GetHDTag(movie_url,genre,pushHD)
			listItem = xbmcgui.ListItem(title)
			poster = Get_PosterUrl(str(tmp.contents[1].contents[1]))
			#xbmc.log('Poster: ' + poster)
			poster=DownloadPoster(poster,"movie")
			listItem.setThumbnailImage(poster)
			listItem.setLabel2(GetHDTag(movie_url,genre,pushHD))
			description =FixHtmlString(tmp.contents[7].contents[7].string).decode("utf-8")
			infoLabels = { "Title": title,"Genre": movie_genre,"Year": movie_year,"Director": movie_director,"Cast": movie_actors,"Plot": description,'videoresolution':'','overlay':overlay }
			listItem.setInfo(type="Video", infoLabels=infoLabels)
			url=str(sys.argv[0]) + '?' + "url=" + urllib.quote_plus(movie_url) + "&mode=play"
			xbmcplugin.addDirectoryItem(thisPlugin,url,listItem)
			#xbmcplugin.addSortMethod( thisPlugin, sortMethod=xbmcplugin.SORT_METHOD_LABEL )
			#print eachmovie['href']+","+eachmovie.string  tmp.contents[1].contents[1]
			#listing.append(unicode(tmp.contents[1].contents[3].string).encode("utf-8"))
	SortListItems()
	xbmcplugin.setContent(thisPlugin, 'movies')
	xbmc.executebuiltin("Container.SetViewMode(508)")
def FixHtmlString(value):
	string =str(value)
	string = string.replace('&aring;','å')
	string = string.replace('&auml;','ä')
	string = string.replace('&ouml;','ö')
	string = string.replace('&Aring;','Å')
	string = string.replace('&Auml;','Ä')
	string = string.replace('&Ouml;','Ö')
	string = string.replace('&hellip;','...')
	string = string.replace('&quot;','\"')
	string = string.replace('&amp;','&')
	string = string.replace('&oslash;','ø')
	string = string.replace('&Oslash;','Ø')
	string = string.replace('&aelig;','æ')
	string = string.replace('&AElig;','Æ')
	string = string.replace('&Eacute;','É')
	string = string.replace('&eacute;','é')
	return string
def unescape(s):
    p = htmllib.HTMLParser(None)
    p.save_bgn()
    p.feed(s)
    return p.save_end()
def GetHDTag(url,genre,pushHD):
	if str(url).find('hd-filmer') > -1:
		return ' (HD)'
	elif str(genre).find('HD-film') > -1:
		return ' (HD)'
	elif str(pushHD).find('push hd') > -1:
		return ' (HD)'
	else:
		return ''
def IsHD(url,genre,pushHD):
	if str(url).find('hd-filmer') > -1:
		return True
	elif str(genre).find('HD-film') > -1:
		return True
	elif str(pushHD).find('push hd') > -1:
		return True
	else:
		return False
def Get_PosterUrl(value):
	list=value.split("\"")
	list = str(list[1]).split("?")
	xbmc.log('URL: '+str(list[0]))
	return str(list[0])
def CreateHtmlFile(url):
	tmpdir=tempfile.gettempdir()
	path = os.path.join(tmpdir, "play.html")
	f = open(path, "w")
	content = '<html><head><title>Startar Viaplay</title><meta http-equiv=\"REFRESH\" content=\"0;url='+ url +'\"> </head><body bgcolor=\"black\"><p>Startar Viaplay...</p></body></html>'
	f.write(content)
	f.close()
	
	return path
def SetupMovieMenu():
	links = GetLinks('Movies')
	for link in links:
		#xbmc.log('SetupTvMenu, url: ' + urllib.quote_plus(link.url))
		url =str(sys.argv[0]) + '?' + "mode="+link.cmd+"&url="+urllib.quote_plus(link.url)
		AddListItem(link.name,url,True)
		xbmcplugin.addSortMethod( thisPlugin, sortMethod=xbmcplugin.SORT_METHOD_TITLE )
	xbmc.executebuiltin("Container.SetViewMode(50)")

def SetupChildrenMoviesMenu():
	links = GetLinks('Children_Movies')
	for link in links:
		#xbmc.log('SetupTvMenu, url: ' + urllib.quote_plus(link.url))
		url =str(sys.argv[0]) + '?' + "mode="+link.cmd+"&url="+urllib.quote_plus(link.url)
		AddListItem(link.name,url,True)
		xbmcplugin.addSortMethod( thisPlugin, sortMethod=xbmcplugin.SORT_METHOD_TITLE )
	xbmc.executebuiltin("Container.SetViewMode(50)")

def SetupChildrenTvMenu():
	links = GetLinks('Children_TV')
	for link in links:
		#xbmc.log('SetupTvMenu, url: ' + urllib.quote_plus(link.url))
		url =str(sys.argv[0]) + '?' + "mode="+link.cmd+"&url="+urllib.quote_plus(link.url)
		AddListItem(link.name,url,True)
	xbmc.executebuiltin("Container.SetViewMode(50)")
	
def SetupChildrenMenu():
	url=str(sys.argv[0]) + '?' + "mode=childrenmovies&url="
	AddListItem(unicode(__language__(4015)).encode('utf-8'),url,True) #Film
	
	url=str(sys.argv[0]) + '?' + "mode=childrentv&url="
	AddListItem(unicode(__language__(4016)).encode('utf-8'),url,True) #TV
	
	xbmc.executebuiltin("Container.SetViewMode(50)")

def SetupSportCategoryMenu(url):
    links = GetLinks('Sports_Category')
    for link in links:
        objs=GetJson(url)
        
        for category in objs[u'_links'][u'viaplay:categoryFilters']:
            title = unicode(category['title']).encode('utf-8')
            item_url=str(category['href'])

            url =str(sys.argv[0]) + '?' + "mode="+link.cmd+"&url="+urllib.quote_plus(item_url)
            AddListItem(title,url,True)
    
    xbmc.executebuiltin("Container.SetViewMode(50)")

def SetupSportMenu():
	links = GetLinks('Sports')
	for link in links:
		#xbmc.log('SetupTvMenu, url: ' + urllib.quote_plus(link.url))
		url =str(sys.argv[0]) + '?' + "mode="+link.cmd+"&url="+urllib.quote_plus(link.url)
		AddListItem(link.name,url,True)
	xbmc.executebuiltin("Container.SetViewMode(50)")
def SetupTvMenu():
	links = GetLinks('TV')
	for link in links:
		#xbmc.log('SetupTvMenu, url: ' + urllib.quote_plus(link.url))
		url =str(sys.argv[0]) + '?' + "mode="+link.cmd+"&url="+urllib.quote_plus(link.url)
		xbmc.log("TV menu, "+link.cmd + " URL: " + url)
		AddListItem(link.name,url,True)
	xbmc.executebuiltin("Container.SetViewMode(50)")
	
def SetupChannelsMenu():
    #links = GetLinks('Channels')
    channels = GetChannels(GetCountryFullname())

    for channel in channels:

        if channel.epg!=None:
            programName = unicode(channel.epg.program).encode('utf-8')
            title = unicode(channel.name).encode('utf-8') + " (" + channel.epg.starttime + " - " + programName +")"
        else:
            title = channel.name
            programName=""

        if SETTINGS_USE_ANDROID:
            url =str(sys.argv[0]) + '?' + "mode=play_live&url="+urllib.quote_plus(channel.url)+"&strmtitle=" + urllib.quote_plus(channel.name)+ "&productid="+ urllib.quote_plus(channel.url) +"&strmname="+urllib.quote_plus(channel.epg.starttime + " - " + programName)+"&strmimage="+urllib.quote_plus(unicode(channel.image).encode('utf-8'))
        else:
            url =str(sys.argv[0]) + '?' + "mode=play_live&url="+urllib.quote_plus(channel.url)

        xbmc.log("Channels menu, "+channel.url + " URL: " + url)

        AddListItemEx(title,url,False,unicode(channel.image).encode('utf-8'))

    #for link in links:
    #    #xbmc.log('SetupTvMenu, url: ' + urllib.quote_plus(link.url))
    #    url =str(sys.argv[0]) + '?' + "mode="+link.cmd+"&url="+urllib.quote_plus(link.url)
    #    xbmc.log("Channels menu, "+link.cmd + " URL: " + url)
        
    #    root = os.path.join(ROOT_FOLDER,"resources","channel_icons")
    #    #path1 = os.path.join(root,"MceRemoteHandler.exe")

    #    #root = os.path.join(ROOT_FOLDER,"resources")
        
    #    if(unicode(link.name).encode('utf-8').startswith("TV3")):
    #        channel_image =os.path.join(root.decode('utf-8'), link.name+' '+GetCountry()+'.png')
    #    else:
    #        channel_image = os.path.join(root.decode('utf-8'), link.name+'.png')
    #    xbmc.log("Channel_Image: " + unicode(channel_image).encode('utf-8'))
    #    #AddListItem(link.name,url,True)
    #    AddListItemEx(link.name,url,False,unicode(channel_image).encode('utf-8'))
    xbmc.executebuiltin("Container.SetViewMode(50)")

def SearchTitleOrPersonJson(url,search,type):
    url = url + urllib.quote_plus(search)

    objs= GetJson(url)

    for block in objs['_embedded']['viaplay:blocks']:
        count = int(block['totalProductCount'])

        if count > 0:
            for product in block['_embedded']['viaplay:products']:
                productType = str(product['type'])
                if productType==type:
                    title = unicode(product['content']['title']).encode('utf-8')
                    product_url = str(product['_links']['viaplay:page']['href'])
                    prodId=str(product['system']['productId'])
                    image_url=str(product['content']['images']['boxart']['url'])
                    synopsis= unicode(product['content']['synopsis']).encode('utf-8')

                    listItem = xbmcgui.ListItem(title)

                    if product_url.endswith('-hd'):
                        overlay=xbmcgui.ICON_OVERLAY_HD
                        listItem.setLabel2(" (HD)")
                    else:
                        overlay=xbmcgui.ICON_OVERLAY_NONE
                    
                    listItem.setThumbnailImage(image_url)

                    infoLabels = { "Title": title,"Genre": "","Year": "","Director": "","Cast": "","Plot": synopsis,'videoresolution':'','overlay':overlay }
                    listItem.setInfo(type="Video", infoLabels=infoLabels)

                    if type=='episode':
                        seasonNo = int(product['content']['series']['season']['seasonNumber'])
                        episodeNo=int(product['content']['series']['episodeNumber'])
                        prodId=str(product['system']['productId'])

                        title = title + " - " + unicode(product['content']['series']['season']['title']).encode('utf-8') + " - Avsnitt " + str(product['content']['series']['episodeNumber'])
                        infoLabels = { "Title": title,"tvshowtitle": title,"season": seasonNo,"episode": episodeNo,"plotoutline": synopsis,"plot": synopsis,"overlay":overlay,"playcount":0}
                        listItem.setInfo(type="Video", infoLabels=infoLabels)
                        item_url=str(sys.argv[0]) + '?' + "url=" + urllib.quote_plus(product_url+"?partial=true&block=1") + "&mode=play&productid=" + prodId+"&contenttype=tv"
                        
                    elif type=='movie':
                        item_url=str(sys.argv[0]) + '?' + "url=" + urllib.quote_plus(product_url) + "&mode=play&productid=" + prodId+"&contenttype=movie"

                    xbmcplugin.addDirectoryItem(thisPlugin,item_url,listItem)

def SearchForTV(url):
	keyboard = xbmc.Keyboard('')
	keyboard.setHeading('Sök efter serie, skådespelare eller regissör...')
	keyboard.doModal()
	if (keyboard.isConfirmed()):
		text = keyboard.getText()
        SearchTitleOrPersonJson(url,urllib.quote_plus(text),"episode")

        xbmcplugin.addSortMethod( thisPlugin, sortMethod=xbmcplugin.SORT_METHOD_LABEL )
        xbmcplugin.setContent(thisPlugin, 'episodes')
        xbmc.executebuiltin("Container.SetViewMode(504)")
		#LoadEpisodesView(search_url)
def SearchForMovie(url):
	keyboard = xbmc.Keyboard('')
	keyboard.setHeading('Sök efter titel på film, skådespelare eller regissör...')
	keyboard.doModal()
	if (keyboard.isConfirmed()):
		text = keyboard.getText()
		#text = text.replace(' ','+')
		#search_url = url + text
		#xbmc.log('Search url = ' + search_url)
        SearchTitleOrPersonJson(url,urllib.quote_plus(text),"movie")
		#LoadMovieView(search_url)
def LoadSeasons(url):
	page=urllib2.urlopen(url)
	soup = BeautifulSoup(page.read())
	seasons=soup.findAll('div', attrs={'class' : 'media-wrapper seasons'})
	for season in seasons:
		season_Name = unicode(season.contents[1].contents[0]).encode('utf-8')
		#xbmcgui.Dialog().ok( "LoadSeasons",season_Name)
		url=str(sys.argv[0]) + '?' + "mode=viewtvseason&url="+urllib.quote_plus(url)
		AddListItem(season_Name,url,True)
	xbmcplugin.setContent(thisPlugin, 'files')
	xbmc.executebuiltin("Container.SetViewMode(51)")
def SetupMainMenu():

    movies = os.path.join(RESOURCE_FOLDER, 'movies.jpg')
    sports = os.path.join(RESOURCE_FOLDER, 'sports.jpg')
    tv = os.path.join(RESOURCE_FOLDER, 'tv.jpg')
    children = os.path.join(RESOURCE_FOLDER, 'children.jpg')
    settings = os.path.join(RESOURCE_FOLDER, 'setting.png')
    starred = os.path.join(RESOURCE_FOLDER, 'starred.png')
    watched = os.path.join(RESOURCE_FOLDER, 'watched.png')
    
    url=str(sys.argv[0]) + '?' + "mode=children&url="
    AddListItemEx(unicode(__language__(4028)).encode('utf-8'),url,True,children) #Barn
    
    url=str(sys.argv[0]) + '?' + "mode=movies&url="
    AddListItemEx(unicode(__language__(4015)).encode('utf-8'),url,True,movies) #Film
    
    url=str(sys.argv[0]) + '?' + "mode=sport&url="
    AddListItemEx(unicode(__language__(4017)).encode('utf-8'),url,True,sports) #Sport
    
    url=str(sys.argv[0]) + '?' + "mode=tv&url="
    AddListItemEx(unicode(__language__(4016)).encode('utf-8'),url,True,tv) #TV
    
    url=str(sys.argv[0]) + '?' + "mode=channels&url="
    AddListItemEx(unicode(__language__(4033)).encode('utf-8'),url,True,"") #Kanaler
    
    url=str(sys.argv[0]) + '?' + "mode=watched&url="
    AddListItemEx(unicode(__language__(4047)).encode('utf-8'),url,True,watched) #Aktivitetslistan

    url=str(sys.argv[0]) + '?' + "mode=starred&url="
    AddListItemEx(unicode(__language__(4048)).encode('utf-8'),url,True,starred) #Stjärnmärkt
    
    url=str(sys.argv[0]) + '?' + "mode=settings&url="
    AddListItemEx(unicode(__language__(4018)).encode('utf-8'),url,False,settings) #Inställningar
    
    #url=str(sys.argv[0]) + '?' + "mode=password&url="
    #AddListItemEx("Password test",url,False,tv) #Streama

    #url=str(sys.argv[0]) + '?' + "mode=streamviaplay&url="
    #AddListItemEx("Stream Viaplay",url,False,tv) #Streama

	# url=str(sys.argv[0]) + '?' + "mode=checkupdate&url="
	# AddListItem("Check for update",url,False)

def SetupCategoriesTV():
    links = GetLinks('TV_Category')
    for link in links:
        
        objs = GetJson(link.url)

        # Gets all sections such as recently added,
        for o in objs["_links"]["viaplay:categoryFilters"]:
            title=unicode(o["title"]).encode('utf-8')
            content_url = str(o["href"])

            url =str(sys.argv[0]) + '?' + "mode="+link.cmd+"&url="+urllib.quote_plus(content_url)
            AddListItem(title,url,True)
    xbmc.executebuiltin("Container.SetViewMode(50)")

def SetupAdultCategories(url):
    objs = GetAdultContent(url)

    for category in objs['_links']['viaplay:categoryFilters']:
        title = unicode(category['title']).encode('utf-8')
        categoryUrl=str(category['href'])

        cmd_url =str(sys.argv[0]) + '?' + "mode=viewadult&url="+urllib.quote_plus(categoryUrl)
        AddListItem(title,cmd_url,True)
    xbmc.executebuiltin("Container.SetViewMode(50)")

def SetupCategories():
    links = GetLinks('Movies_Category')
    for link in links:
        
        objs = GetJson(link.url)

        # Gets all sections such as recently added,
        for o in objs["_links"]["viaplay:categoryFilters"]:
            title=unicode(o["title"]).encode('utf-8')
            content_url = str(o["href"])

            linkCmd = link.cmd

            adultName = GetAdultName()
            if adultName in content_url:
                linkCmd="adultcategories"

            url =str(sys.argv[0]) + '?' + "mode="+linkCmd+"&url="+urllib.quote_plus(content_url)
            AddListItem(title,url,True)
    xbmc.executebuiltin("Container.SetViewMode(50)")

def AddListItem(title,url,isFolder):
	listItem = xbmcgui.ListItem(title)
	xbmcplugin.addDirectoryItem(thisPlugin,url,listItem,isFolder=isFolder)
	#xbmcplugin.addSortMethod( thisPlugin, sortMethod=xbmcplugin.SORT_METHOD_LABEL )

def AddListItemEx(title,url,isFolder,thumbnail):
	listItem = xbmcgui.ListItem(title)
	listItem.setThumbnailImage(thumbnail)
	xbmcplugin.addDirectoryItem(thisPlugin,url,listItem,isFolder=isFolder)

def GetMovieParentRating(url):
    if SETTINGS_USE_PARENTAL_CONTROL:
        objs = GetAdultContent(url)
    else:
        objs = GetJson(url)

    if not 'viaplay:blocks' in objs['_embedded']:
        rating=objs['_embedded']['viaplay:product'][u'content'][u'parentalRating']
    else:
        rating=objs['_embedded']['viaplay:blocks'][0]['_embedded']['viaplay:product'][u'content'][u'parentalRating']

    return rating

def GetStreamUrl(url,type):
    objs=None

    xbmc.log("GetStreamUrl url: " + url)

    try:

        if not type=='channel':
            if SETTINGS_USE_PARENTAL_CONTROL:
                objs = GetAdultContent(url)
            else:
                objs = GetJson(url)

        if type=='tv':
            streamUrl=objs['_embedded']['viaplay:product']['_links']['viaplay:stream']['href']
        elif type=='sport':
            streamUrl=objs['_embedded']['viaplay:product']['_links']['viaplay:stream']['href']
        elif type=='movie':
            if not 'viaplay:blocks' in objs['_embedded']:
                streamUrl=objs['_embedded']['viaplay:product']['_links']['viaplay:stream']['href']
            else:
                streamUrl=objs['_embedded']['viaplay:blocks'][0]['_embedded']['viaplay:product']['_links']['viaplay:stream']['href']
        elif type=='channel':
            streamUrl=url

        xbmc.log("GetStreamUrl before: " + streamUrl)

        streamUrl = urllib.quote_plus(streamUrl)
        streamUrl = GetStreamUrlForCountry() + streamUrl

        xbmc.log("GetStreamUrl After: " + streamUrl)
        #return streamUrl

    except urllib2.URLError, e:
        if e.code==404:
            xbmc.log("GetStreamUrl: HTTP ERROR 404!")
            xbmc.log("")
            streamUrl=""
            xbmcgui.Dialog().ok( unicode(__language__(4009)).encode('utf-8'), unicode(__language__(4046)).encode('utf-8'))
            return streamUrl
        else:
            xbmc.log("GetStreamUrl Error: " + str(e.code))
            xbmc.log("Error message: "+e.msg)
            streamUrl=""
            xbmcgui.Dialog().ok( unicode(__language__(4009)).encode('utf-8'), str(e.code)+ " " + e.msg)
            return streamUrl
    else:
        return streamUrl


def PlayUrl(url,type,productid):
    xbmc.log("PlayUrl: " + url)
    xbmc.log('Platform is: ' + _platform)
    xbmc.log('Contenttype is: ' + type)

    if type=="movie":
        if SETTINGS_USE_PARENTAL_CONTROL:
            xbmc.log("PlayUrl get parental control from movie url")
            parentalrating = GetMovieParentRating(url)
            xbmc.log("PlayUrl Check Parental control")
            if not CheckForParentalControl(parentalrating):
                xbmcgui.Dialog().ok( unicode(__language__(4049)).encode('utf-8'), unicode(__language__(4052)).encode('utf-8'))
                xbmc.executebuiltin( "Dialog.Close(busydialog)" )
                return
            else:
                pin="%26pgPin%3D" + urllib.quote_plus(SETTINGS_PINCODE)
        else:
            pin=""
    else:
        pin=""

    streamUrl = GetStreamUrl(url,type)

    if len(streamUrl)==0:
        xbmc.executebuiltin( "Dialog.Close(busydialog)" )
        return 
    
    if len(pin) > 0:
        streamUrl=streamUrl+pin

    xbmc.log("New Play URL: "+streamUrl)

    if(_platform=='win32'):
        xbmc.log("Send jsonrpc message NotifyAll")
        xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"JSONRPC.NotifyAll","params":{"sender":"Viaplay","message":"Starting playback"},"id":"1"}')
        xbmc.log("Jsonrpc:Message sent")

        path = os.path.join(os.environ.get("PROGRAMFILES", "C:\\Program Files"), "Internet Explorer\\IEXPLORE.EXE")
        xbmc.log("Path to Internet Explorer: " + path)

        xbmc.log("Launching MceRemoteControl")
        root = os.path.join(ROOT_FOLDER,"resources","lib") #xbmc.translatePath(os.path.join('special://home','plugin.video.hbonordic','resources','lib'))
        path1 = os.path.join(root,"MceRemoteHandler.exe")
        path2 = os.path.join(root,"StopMusic.exe")
        
        ##Stop any music playback
        ##os.startfile(unicode(path2,'utf-8'))

        ##sp.Popen([unicode(AUTOHOTKEY_PATH).encode('utf-8')])
        os.startfile(unicode(path1,'utf-8'))

        #p=sp.Popen('"'+path+'" -k '+ streamUrl)

        # FOR NOW WE USE THE streamUrl VARIABLE SET IT TO THE URL OF THE SELECTED MOVIE/EPISODE
        url = url.replace(GetContentDomain(),GetDomain())
        url = url.replace("?partial=true&block=1","")
        streamUrl=url

        StartChromePlayback(streamUrl)

        #xbmc.executebuiltin("plugin://plugin.program.chrome.launcher/?url="+urllib.quote_plus(streamUrl)+"&mode=showSite&stopPlayback=no")

        ##xbmc.log("Send jsonrpc message NotifyAll")
        ##xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"JSONRPC.NotifyAll","params":{"sender":"Viaplay","message":"Closing Viaplaylauncher"},"id":"1"}')
        ##xbmc.log("Jsonrpc:Message sent")
    elif _platform=='darwin':
        sp.Popen('open -a "/Applications/Safari.app/" '+streamUrl, shell=True)
    else:
        webbrowser.open(streamUrl)

    xbmc.executebuiltin( "Dialog.Close(busydialog)" )

	#if(os.name=='nt'):
	#	xbmc.log("Send jsonrpc message NotifyAll")
	#	xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"JSONRPC.NotifyAll","params":{"sender":"Viaplay","message":"Starting Viaplaylauncher"},"id":"1"}')
	#	xbmc.log("Message sent")
		
	#	xbmc.log("Launching MceRemoteControl")
	#	sp.Popen([AUTOHOTKEY_PATH])
	#	xbmc.log("Launching Viaplaylauncher")
	#	p=sp.Popen([VIAPLAYER_PATH, "-k",url])
	#	p.wait()
		
	#	xbmc.log("Send jsonrpc message NotifyAll")
	#	xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"JSONRPC.NotifyAll","params":{"sender":"Viaplay","message":"Closing Viaplaylauncher"},"id":"1"}')
	#	xbmc.log("Message sent")
		
	#else:
	#	xbmc.log("Launching Webbrowser")
	#	webbrowser.open(url)

#def GetViaplayStream(playUrl):
	

#	xbmc.log("ROOT PATH: " + ROOT_FOLDER)
#	xbmc.log("Chromedriver path WIN: " + CHROMEDRIVER_PATH_WIN)
#	xbmc.log("Autohotkey xbmc: " + AUTOHOTKEY_XBMC_PATH)
	
#	options = webdriver.ChromeOptions()
#	# Hide the Chrome browser window by positioning it far to the left.
#	xbmc.log("Setting Chrome options Windows position")
#	options.add_argument('--window-position=-1000,-1000')
	
#	# Set user agent for IPAD.
#	xbmc.log("Adding options for IPAD User Agent")
#	options.add_argument('--user-agent=Mozilla/5.0 (iPad; U; CPU OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B334b Safari/531.21.10')
	
#	# Start webdriver with Chrome.
#	if(os.name=='nt'): # Windows
#		xbmc.log("Using Chromedriver for Windows")
#		driver = webdriver.Chrome(CHROMEDRIVER_PATH_WIN,chrome_options=options)
#	else: # Mac
#		xbmc.log("Using Chromedriver for MAC")
#		driver = webdriver.Chrome(CHROMEDRIVER_PATH_MAC,chrome_options=options)
	
#	# Run AHK script to shift focus back to xbmc.
#	xbmc.log("Start chromedriver")
#	sp.Popen([AUTOHOTKEY_XBMC_PATH])
	
#	# Open the play url.
#	xbmc.log("Open url")
#	driver.get(playUrl)
#	xbmc.log("Show wait dialog")
#	xbmc.executebuiltin( "ActivateWindow(busydialog)" )
	
#	# Wait for login controls to load
#	xbmc.log("Wait for login-name")
#	WebDriverWait(driver, 6).until(EC.presence_of_element_located((By.ID, "login-name")))
	
#	# Set login credentials by using javascript.
#	xbmc.log("Set login credentials using javascript")
#	driver.execute_script("document.getElementById('login-name').value = '"+SETTINGS_USERNAME+"';")
#	driver.execute_script("document.getElementById('login-pass').value = '"+SETTINGS_PASSWORD+"';")
#	driver.execute_script("document.getElementById('header.main-menu.not-logged-in.submit-button').click();")
	
#	try:
#		xbmc.log("Wait for my viaplay to appear")
#		WebDriverWait(driver, 15).until(lambda s: s.find_element(By.ID, 'header.main-menu.my-viaplay-link').is_displayed())
#	except:
#		xbmc.log('did not find "header.main-menu.my-viaplay-link"!')

#	# Start playback.
#	xbmc.log("Trigger playback")
#	driver.execute_script("document.getElementById('play-movie').click();")
	
#	try:
#		xbmc.log("Wait for Player to appear")
#		element = WebDriverWait(driver, 6).until(EC.presence_of_element_located((By.ID, "Player")))
#	except:
#		xbmc.log("did not find player!")
	
#	# Get the html source.
#	xbmc.log("Get source from viaplay website")
#	html_source = driver.page_source
	
#	# Close the Chrome browser
#	xbmc.log("Shutdown chromedriver")
#	driver.quit()
	
#	xbmc.log("Parse the source")
#	soup = BeautifulSoup(html_source)
	
#	xbmc.log("Look for autoplay")
#	result = soup.findAll('video',attrs={'autoplay':'autoplay'})
#	url_m3u8=""
	
#	if(len(result)>0):
#		url_m3u8=str(result[0].contents[0].attrs[0][1])
#	xbmc.log("M3U8: "+url_m3u8)
#	return url_m3u8

def GetChromePath():

    path_tpl = 'AppData\Local\Google\Chrome\Application'
    userPath = os.environ['USERPROFILE']
    xbmc.log("UserProfile: " + userPath)

    chrome_root = os.path.join(userPath,path_tpl)
    xbmc.log("Chrome_root: " + chrome_root)

    chrome_path = os.path.join(chrome_root,"chrome.exe")

    if(os.path.exists(chrome_path)):
        return chrome_path

    chrome_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"

    if(os.path.exists(chrome_path)):
        return chrome_path

    chrome_path = os.path.join(os.environ.get("PROGRAMFILES", "C:\\Program Files"), "Google\\Chrome\\Application\\chrome.exe")

    if(os.path.exists(chrome_path)):
        return chrome_path

    chrome_path = os.path.join(os.environ.get("PROGRAMFILES", "C:\\Program Files"), "Google\\Chrome\\chrome.exe")

    if(os.path.exists(chrome_path)):
        return chrome_path
    
    chrome_path = os.path.join(os.environ.get("ProgramFiles(x86)","C:\\Program Files (x86)"),"Google\\Chrome\\Application\\chrome.exe")

    if(os.path.exists(chrome_path)):
        return chrome_path
            
    chrome_path = os.path.join(os.environ.get("ProgramFiles(x86)","C:\\Program Files (x86)"),"Google\\Chrome\\chrome.exe")

    if(os.path.exists(chrome_path)):
        return chrome_path
    #C:\Program Files (x86)\Google\Application\Chrome.exe
    chrome_path = os.path.join(os.environ.get("ProgramFiles(x86)","C:\\Program Files (x86)"),"Google\\Application\\chrome.exe")

    if(os.path.exists(chrome_path)):
        return chrome_path

    return ""

def StartChromePlayback(url):
    xbmc.log("StartChromePlayback url: " + url)

    chrome_path = GetChromePath()

    if(chrome_path==""):
        return

    sp.Popen('"'+chrome_path+'" -new-window --start-fullscreen '+ url )

def GetPosterFilename(url):
    list = url.split("/")
    return str(list[len(list)-2])

def GetMoviePosterFilename(url):
    list = url.split("/")
    return str(list[len(list)-1])
	
def DownloadPoster(url,posterType):
	
	tmp_dir = xbmc.translatePath('special://profile/addon_data/plugin.video.viaplay/posters')
	
	if not os.path.exists(tmp_dir):
		os.makedirs(tmp_dir)
	
	if(posterType=="tv"):
		filename=GetPosterFilename(url)+".jpg"
	if(posterType=="movie"):
		filename=GetMoviePosterFilename(url)
	if(posterType=="sports"):
		filename=GetMoviePosterFilename(url)
	if(posterType=="fanart"):
		filename=GetPosterFilename(url)
		filename=filename+"fanart.jpg"
		
	local_poster_path = os.path.join(tmp_dir, filename)
	xbmc.log("DownloadPoster url: " + url)
	xbmc.log("DownloadPoster local path: " + local_poster_path)
	
	if(os.path.exists(local_poster_path)==False):
		xbmc.log("The poster does not exist, downloading the poster...")
		try:
			DownloadFile(url,local_poster_path)
		except:
			default_image = os.path.join(RESOURCE_FOLDER, 'viaplay.png')
			return default_image
	else:
		xbmc.log("The poster already exist, no need to download it again")
	
	return local_poster_path

def GetUrlFromManifest(data=""):
    posStart = str(data).find("<Url>")
    posEnd = str(data).find("</Url>")
    url = data[posStart+5:posEnd]
    return url

#def GetProductStreamUrl(productId):
#    #http://viaplay.se/player?stream=https%3A%2F%2Fplay.viaplay.se%2Fapi%2Fstream%2Fv1%257B%3FdeviceId%2CdeviceName%2CdeviceType%2CuserAgent%7D%26deviceKey%3Dandroidnodrm-se%26productId%3D"+productId
#    if SETTINGS_COUNTRY=="0":
#        return "http://viaplay.se/player?stream=https%3A%2F%2Fplay.viaplay.se%2Fapi%2Fstream%2Fv1%257B%3FdeviceId%2CdeviceName%2CdeviceType%2CuserAgent%7D%26deviceKey%3Dandroidnodrm-se%26productId%3D"+productId
#    elif SETTINGS_COUNTRY=="1":
#        return "http://viaplay.dk/player?stream=https%3A%2F%2Fplay.viaplay.dk%2Fapi%2Fstream%2Fv1%257B%3FdeviceId%2CdeviceName%2CdeviceType%2CuserAgent%7D%26deviceKey%3Dandroidnodrm-dk%26productId%3D"+productId
#    elif SETTINGS_COUNTRY=="2":
#        return "http://viaplay.no/player?stream=https%3A%2F%2Fplay.viaplay.no%2Fapi%2Fstream%2Fv1%257B%3FdeviceId%2CdeviceName%2CdeviceType%2CuserAgent%7D%26deviceKey%3Dandroidnodrm-no%26productId%3D"+productId
#    elif SETTINGS_COUNTRY=="3":
#        return "http://viaplay.fi/player?stream=https%3A%2F%2Fplay.viaplay.fi%2Fapi%2Fstream%2Fv1%257B%3FdeviceId%2CdeviceName%2CdeviceType%2CuserAgent%7D%26deviceKey%3Dandroidnodrm-fi%26productId%3D"+productId

#    return "http://viaplay.se/player?stream=https%3A%2F%2Fplay.viaplay.se%2Fapi%2Fstream%2Fv1%257B%3FdeviceId%2CdeviceName%2CdeviceType%2CuserAgent%7D%26deviceKey%3Dandroidnodrm-se%26productId%3D"+productId

def GetProductStreamUrl(productId):
    if SETTINGS_COUNTRY=="0":   
        return "http://viaplay.se/player?stream=https%3A%2F%2Fplay.viaplay.se%2Fapi%2Fstream%2Fv1%257B%3FdeviceId%2CdeviceName%2CdeviceType%2CuserAgent%7D%26deviceKey%3Dandroidnodrmv2-se%26productId%3D"+productId
    elif SETTINGS_COUNTRY=="1":
        return "http://viaplay.dk/player?stream=https%3A%2F%2Fplay.viaplay.dk%2Fapi%2Fstream%2Fv1%257B%3FdeviceId%2CdeviceName%2CdeviceType%2CuserAgent%7D%26deviceKey%3Dandroidnodrmv2-dk%26productId%3D"+productId
    elif SETTINGS_COUNTRY=="2":
        return "http://viaplay.no/player?stream=https%3A%2F%2Fplay.viaplay.no%2Fapi%2Fstream%2Fv1%257B%3FdeviceId%2CdeviceName%2CdeviceType%2CuserAgent%7D%26deviceKey%3Dandroidnodrmv2-no%26productId%3D"+productId
    elif SETTINGS_COUNTRY=="3":
        return "http://viaplay.fi/player?stream=https%3A%2F%2Fplay.viaplay.fi%2Fapi%2Fstream%2Fv1%257B%3FdeviceId%2CdeviceName%2CdeviceType%2CuserAgent%7D%26deviceKey%3Dandroidnodrmv2-fi%26productId%3D"+productId

    return "http://viaplay.se/player?stream=https%3A%2F%2Fplay.viaplay.se%2Fapi%2Fstream%2Fv1%257B%3FdeviceId%2CdeviceName%2CdeviceType%2CuserAgent%7D%26deviceKey%3Dandroidnodrmv2-se%26productId%3D"+productId

#def GetPlaylistUrl(productId):
#    #"http://play.viaplay.se/api/playlist/v1?deviceKey=androidnodrm-se&productId=" + productId
#    if SETTINGS_COUNTRY=="0":
#        return "http://play.viaplay.se/api/playlist/v1?deviceKey=androidnodrm-se&productId=" + productId
#    elif SETTINGS_COUNTRY=="1":
#        return "http://play.viaplay.dk/api/playlist/v1?deviceKey=androidnodrm-dk&productId=" + productId
#    elif SETTINGS_COUNTRY=="2":
#        return "http://play.viaplay.no/api/playlist/v1?deviceKey=androidnodrm-no&productId=" + productId
#    elif SETTINGS_COUNTRY=="3":
#        return "http://play.viaplay.fi/api/playlist/v1?deviceKey=androidnodrm-fi&productId=" + productId

#    return "http://play.viaplay.se/api/playlist/v1?deviceKey=androidnodrm-se&productId=" + productId


def GetPlaylistUrl(productId):
    
    if SETTINGS_COUNTRY=="0":
        return "http://play.viaplay.se/api/playlist/v1?deviceKey=androidnodrmv2-se&productId=" + productId
    elif SETTINGS_COUNTRY=="1":
        return "http://play.viaplay.dk/api/playlist/v1?deviceKey=androidnodrmv2-dk&productId=" + productId
    elif SETTINGS_COUNTRY=="2":
        return "http://play.viaplay.no/api/playlist/v1?deviceKey=androidnodrmv2-no&productId=" + productId
    elif SETTINGS_COUNTRY=="3":
        return "http://play.viaplay.fi/api/playlist/v1?deviceKey=androidnodrmv2-fi&productId=" + productId

    return "http://play.viaplay.se/api/playlist/v1?deviceKey=androidnodrmv2-se&productId=" + productId

def GetSecureStreamUrl(productId):
    try:
        username = urllib.quote_plus(SETTINGS_USERNAME)
        password=urllib.quote_plus(SETTINGS_PASSWORD)
        
        mech = mechanize.Browser()
        mech.set_handle_robots(False)
        #loginUrl = GetLoginUrl("androidnodrm")+username+"&password="+password
        loginUrl = GetLoginUrl("androidnodrmv2")+username+"&password="+password
        playUrl = GetProductStreamUrl(productId)
        playListUrl=GetPlaylistUrl(productId)

        xbmc.log("GetSecureStreamUrl PlayUrl: " + playUrl)
        xbmc.log("GetSecureStreamUrl PlayListUrl: " + playListUrl)

        #mech.open(GetLoginUrl('androidnodrm-se') +username+"&password="+password)
        #mech.open("https://login.viaplay.se/api/login/v1?deviceKey=androidnodrm-se&returnurl=https%3A%2F%2Fcontent.viaplay.se%2Fandroidnodrm-se%2Fstarred&username="+username+"&password="+password)
        mech.open(loginUrl)

        xbmc.log("GetSecureStreamUrl, loginprocess done!")

        #"http://viaplay.se/player?stream=https%3A%2F%2Fplay.viaplay.se%2Fapi%2Fstream%2Fv1%257B%3FdeviceId%2CdeviceName%2CdeviceType%2CuserAgent%7D%26deviceKey%3Dandroidnodrm-se%26productId%3D"+productId
        mech.open(playUrl)
        xbmc.log("GetSecureStreamUrl, play done!")

        #mech.open("http://play.viaplay.se/api/playlist/v1?deviceKey=androidnodrm-se&productId=" + productId)
        mech.open(playListUrl)
        xbmc.log("GetSecureStreamUrl, playlist done!")

        data = mech.response().get_data()
    
        data = str(data).replace("<![CDATA[","")
        data = str(data).replace("]>","")

        raw_url=GetUrlFromManifest(data)

        #dom = parseString(data)
        #test=dom.getElementsByTagName('Url')
        #test=dom.getElementsByTagName('FallbackUrl')
    
        #raw_url = str(test[0].childNodes[0].nodeValue)
        #url = raw_url.split('?')
        url = raw_url.split('&sami=')

        #test2 = dom.getElementsByTagName('Subtitle')
        subtitleUrl=GetSubtitleUrl(raw_url)#str(test2[0].childNodes[0].childNodes[0].nodeValue)

        #streamUrl = url[0].replace('.prdy','')
        streamUrl=url[0]#GetStreamQaulity(url[0],'1280x720','Layer4')

        info = StreamInfoEx(streamUrl,subtitleUrl,raw_url)

        return info
    except urllib2.URLError, e:
        xbmc.log("GetSecureStreamUrl ERROR:")
        xbmc.log("Message: " + e.message)
        #if e.code==403:
        #    return None
        #else:
        return None
    except socket.timeout, e:
        xbmc.log("Timeout exception")
        return None
    else:
        return None

def GetSubtitleUrl(data):
    values = data.split('&')

    for value in values:
        if 'sami=' in value:
            return value.replace("sami=","")

    return ""
#def GetStreamQaulity(url,streamQuality):

#    tmp_dir = xbmc.translatePath('special://profile/addon_data/plugin.video.viaplay/tmp')
#    local_m3u8=os.path.join(tmp_dir, 'stream.m3u8')
     
#    DownloadFile(url,local_m3u8)

#    with open(local_m3u8, 'r') as content_file:
#        content = content_file.read()
#    quality = content.split('\n')
    
#    list=[]
#    streamItem=None

#    for item in quality:
#        if item=='#EXTM3U' or len(item)==0:
#            continue
#        if item.startswith('#EXT-X-STREAM-INF'):
#            values = item.split(', ')
#            streamItem=StreamQuality(str(values[1]).replace('BANDWIDTH=',''),"")
#        else:
#            streamItem.filename=str(item)
#            list.append(streamItem)

#    new_filename=''
#    for item in list:
#        if streamQuality in item.filename:
#            new_filename = item.filename
    
#    path = urlparse.urlsplit(url).path
#    old_filename = posixpath.basename(path)

#    stream_url = url.replace(old_filename,new_filename)

#    return stream_url

def SaveImageToDisk(url,productId):

    if len(url)==0:
        return ""

    xbmc.log("SaveImageToDisk URL: " + url)
    xbmc.log("SaveImageToDisk ProductId: " + productId)

    tmp_dir = xbmc.translatePath('special://profile/addon_data/plugin.video.viaplay/tmp')
    filename = productId+'.jpg'
    local_image=os.path.join(tmp_dir, filename)

    xbmc.log("SaveImageToDisk local_image: " + local_image)

    DownloadFile(url,local_image)

    return local_image

def GetStreamQaulity(url,streamQuality1,streamQuality2):

    tmp_dir = xbmc.translatePath('special://profile/addon_data/plugin.video.viaplay/tmp')
    local_m3u8=os.path.join(tmp_dir, 'stream.m3u8')

    DownloadFile(url,local_m3u8)

    with open(local_m3u8, 'r') as content_file:
        content = content_file.read()
    quality = content.split('\n')
    
    list=[]
    streamItem=None

    for item in quality:
        if item=='#EXTM3U' or len(item)==0 or item=='#EXT-X-VERSION:3':
            continue
        if item.startswith('#EXT-X-STREAM-INF'):
            values = item.split(',')
            if 'RESOLUTION=' in item:
                streamItem=StreamQuality(str(values[1]).replace('BANDWIDTH=',''),"",str(values[4]).replace("RESOLUTION=",""))
            else:
                streamItem=StreamQuality(str(values[1]).replace('BANDWIDTH=',''),"","")
        else:
            streamItem.filename=str(item)
            list.append(streamItem)

    new_filename=''
    for item in list:
        if streamQuality1 in item.resolution:
            new_filename = item.filename
        elif streamQuality2 in item.filename:
            new_filename = item.filename
    
    path = urlparse.urlsplit(url).path
    old_filename = posixpath.basename(path)

    stream_url = url.replace(old_filename,new_filename)

    return stream_url

def StreamViaplay(url,productid,title,name,imageurl):
    xbmc.executebuiltin("ActivateWindow(busydialog)")

    xbmc.log("StreamViaplay URL: " + url)
    xbmc.log("StreamViaplay ProductId: " + productid)
    xbmc.log("StreamViaplay ImageUrl: " + imageurl)
    xbmc.log("StreamViaplay Title: " + title)
    xbmc.log("StreamViaplay Name: " + name)

    if '{&dtg}' in url:
        url=url.replace("{&dtg}","")
    
    #imageFile = SaveImageToDisk(imageurl,productid)
    #if len(imageurl)==0:
    #imageurl=GetInternalPlaybackImage(url)
    #xbmc.log("StreamViaplay GetInternalPlaybackImage: " + imageurl)
    if imageurl.startswith("http"):
        imageurl= SaveImageToDisk(imageurl,productid)

    listitem = xbmcgui.ListItem(title,iconImage="", thumbnailImage="")
    listitem.setThumbnailImage(imageurl)
    listitem.setInfo('video', {'Title': title +" - " +  name})#, 'plotoutline ':'21:00 - BBC World news London live'
    listitem.setInfo('video', {'studio': title})
    #listitem.setInfo('video', {'TVShowTitle': title})
    
    info= GetSecureStreamUrl(productid)
    if info!=None:
        xbmc.log("Info.StreamUrl: " + info.streamUrl)
        subtitlePath = GetSubtitle(info.subtitleUrl,productid)
        stream_url = info.streamUrl #GetStreamQaulity(info.streamUrl,'Layer4')

        xbmc.executebuiltin( "Dialog.Close(busydialog)" )

        if(len(stream_url)==0):
            xbmc.executebuiltin('XBMC.Notification("'+"Error"+'","Playback failed, url was empty!",3500,"'+'")')
        else:
            xbmc.Player().play(stream_url, listitem)
        
            startTime = time.time()

            while not xbmc.Player().isPlaying() and time.time() - startTime < 10:
                time.sleep(1.)

            xbmc.Player().setSubtitles(subtitlePath)
            xbmc.Player().showSubtitles(True)
    else:
        xbmc.executebuiltin( "Dialog.Close(busydialog)" )
        #xbmc.executebuiltin('XBMC.Notification("'+"Error"+'","Could not play selected content.",3500,"'+'")')
        xbmcgui.Dialog().ok("Problem","Could not play selected content.")

def GetTotalPageCount(url):
    objs = GetJson(url)

    count = int(objs['_embedded']['viaplay:blocks'][0]['pageCount'])

    return count

def LookForAgeVerification(url):
    try:
        objs = GetJson(url)
        print ""
    except urllib2.URLError, e:
        if e.code==403:
            return True
        else:
            return False
    else:
        return False

def GetSubtitle(url,productId):

	local_subtitle_path=""
	try:

		subname = str(productId)+".smi"
		
		tmp_dir = xbmc.translatePath('special://profile/addon_data/plugin.video.viaplay/tmp')
		local_subtitle_path = os.path.join(tmp_dir, subname)
		xbmc.log("Subtitle local path: " + local_subtitle_path)
		
		DownloadFile(url,local_subtitle_path)
		
		with open(local_subtitle_path, 'r') as content_file:
			content = content_file.read()
		
		content = FixHtmlString(content)
		
		with open(local_subtitle_path, "w") as text_file:
			text_file.write(content)
		
	except Exception, e:
		xbmc.log("Error when calling GetSubtitle: " + str(e))
	finally:
		return local_subtitle_path

def get_input(title, default='', hidden=False):
	#Show a virtual keyboard and return the entered text.

	ret = None

	keyboard = xbmc.Keyboard(default, title)
	keyboard.setHiddenInput(hidden)
	keyboard.doModal()

	if keyboard.isConfirmed():
		ret = keyboard.getText()

	return ret
		
def GetXbmcVersion():
	#rev_re = re.compile(' r(\d+)') 
	#xbmc_rev = int(rev_re.search(xbmc.getInfoLabel( "System.BuildVersion" )).group(1))
	return xbmc.getInfoLabel( "System.BuildVersion" )

def CheckForUpdate():

    xbmc.log("Checking For update...")
    currentVersion= xbmcaddon.Addon().getAddonInfo('version')
    xbmc.log("Current version is: " + currentVersion)
    page=urllib2.urlopen("http://www.dsd.se/viaplay/latestversion.txt")
    newVersion=page.read()
    xbmc.log("New version is: "+newVersion)
    
    if(newVersion > currentVersion):
        icon=os.path.join(ROOT_FOLDER,"icon.png")
        xbmc.log("Path to icon: " + icon)
        xbmc.executebuiltin('xbmc.Notification('+unicode(__language__(4009)).encode('utf-8')+','+unicode(__language__(4045)).encode('utf-8')+',9000,'+icon+')')

def HandleURL(url):
    url = url.replace("{?dtg}","")
    return url
    
params = parameters_string_to_dict(sys.argv[2])
mode = params.get("mode", None)
url = urllib.unquote_plus(params.get("url",  ""))
title = urllib.unquote_plus(params.get("title",  ""))
episodetitle = urllib.unquote_plus(params.get("episodetitle",  ""))
id = urllib.unquote_plus(params.get("id",  ""))
poster = urllib.unquote_plus(params.get("poster",  ""))
season = urllib.unquote_plus(params.get("season",  ""))
episode  = urllib.unquote_plus(params.get("episode",  ""))
image  = urllib.unquote_plus(params.get("image",  ""))
fanart  = urllib.unquote_plus(params.get("fanart",  ""))
productid  = urllib.unquote_plus(params.get("productid",  ""))
contenttype  = urllib.unquote_plus(params.get("contenttype",  ""))
parentalrating = urllib.unquote_plus(params.get("parentalrating",  ""))
strmtitle=urllib.unquote_plus(params.get("strmtitle",  ""))
strmname=urllib.unquote_plus(params.get("strmname",  ""))
strmimage=urllib.unquote_plus(params.get("strmimage",  ""))

if SETTINGS_USE_ANDROID:
    url=HandleURL(url)

if not sys.argv[2] or not mode:
	
	#xbmc.log("XBMC_Version: " + GetXbmcVersion())
    xbmc.log("Language : " + xbmc.getLanguage(1,True))

    SetupMainMenu()
    CreateDatabase()
    UpgradeDatabase()
    xbmc.log("Database Version: " + DatabaseVersion())
    #Check if username and password are set, if not then notify user
    if(len(SETTINGS_USERNAME)==0):
        xbmc.executebuiltin('xbmc.Notification('+unicode(__language__(4009)).encode('utf-8')+','+unicode(__language__(4010)).encode('utf-8')+',8000)')
    #else:
    if(SETTING_CHECKVERSION):
        CheckForUpdate()
        
elif mode=="view_sports":
	LoadLiveSports(url)
elif mode=="checkupdate":
	CheckForUpdate()
elif mode=="password":
    get_input("PIN Code","",True)
elif mode=="starred_tv":
	GetStarredContent(url,ContentTypeTV)
elif mode=="starred_movie":
	GetStarredContent(url,ContentTypeMovie)
elif mode=="starred_sport":
	GetStarredContent(url,ContentTypeSport)
elif mode=="starred":
    GetAllStarredContent()
elif mode=="watched":
    GetAllWatchedContent()
elif mode=="add_tv_favorite":
	AddFavorite(str(title).decode('utf-8'),"tv",url,poster,0,"","")
	xbmc.executebuiltin("xbmc.Notification(Information,"+ unicode(__language__(4022)).encode('utf-8') +",4000)")
elif mode=="remove_tv_favorite":
	dialog = xbmcgui.Dialog()
	ret = dialog.yesno('Viaplay',unicode(__language__(4021)).encode('utf-8') +" '"+ title +"'?") #Do you want to remove favorite
	if ret:
		RemoveFavorite(id)
		xbmc.executebuiltin("Container.Refresh")
elif mode=="remove_starred":
	RemoveStarredContent(productid)
	xbmc.executebuiltin("Container.Refresh")
elif mode=="add_starred":
	AddStarredContent(productid)
	xbmc.executebuiltin("Container.Refresh")
elif mode=="remove_watched":
	RemoveWatchedProduct(productid)
	xbmc.executebuiltin("Container.Refresh")
elif mode=="add_watched":
	AddWatchedProduct(productid)
	xbmc.executebuiltin("Container.Refresh")
elif mode=="view_sport_schedule":
	LoadLiveSportScheduleGetDays(url)
elif mode =="sport_schedule_day":
    xbmc.log("sport_schedule_day URL: " + url)
    LoadLiveSportScheduleForSpecificDay(url,id)
elif mode=="view_sport_live":
	SetupSportCategoryMenu(url)
elif mode=="sport":
	SetupSportMenu()
	xbmcplugin.addSortMethod( thisPlugin, sortMethod=xbmcplugin.SORT_METHOD_LABEL )
elif mode=='search_movie':
	SearchForMovie(url)
elif mode=='search_tv':
	SearchForTV(url)
elif mode=='view_tv_alphabet':
	#LoadTvByAlphabet(url)
    LoadTvAlphabeticalJson(url)
elif mode=='view_movie_alphabet':
	#LoadMoviesByAlphabet(url)
    LoadMoviesAlphabeticalJson(url)
elif mode=='view_tv_episodes':
	LoadEpisodesView(url)
elif mode=='episodes':
	#LoadSeasons(url)
	#showData=GetShowData('Lost')
	#xbmc.log("TV-Series title: " + title)
	#LoadEpisodes(url,title)
    GetEpisodesJson(url,fanart)
elif mode=='viewadult':
    LoadMoviesAdultJson(url)
elif mode=='adultcategories':

    value=""

    if SETTINGS_USE_PARENTAL_CONTROL:
        value = get_input(unicode(__language__(4053)).encode('utf-8'),"",True)
    else:
        heading=unicode(__language__(4054)).encode('utf-8')
        line1=unicode(__language__(4055)).encode('utf-8')
        line2=unicode(__language__(4056)).encode('utf-8')
        yesLabel=unicode(__language__(4057)).encode('utf-8')
        noLabel=unicode(__language__(4058)).encode('utf-8')

        result = xbmcgui.Dialog().yesno(heading,line1,line2,"",noLabel,yesLabel)
        if result:
            value = SETTINGS_PINCODE
            

    if value==SETTINGS_PINCODE:
        Valid = True
        xbmc.log("Pin-code was correct")
        xbmc.log("Sending Age verification to Viaplay")
        SetupAdultCategories(url)
    else:
        xbmc.log("Pin-code was incorrect!")
        xbmcgui.Dialog().ok( unicode(__language__(4049)).encode('utf-8'), unicode(__language__(4052)).encode('utf-8')) 

    
elif mode=='viewtv':
    xbmc.log("Viewtv url: " + url)

    if '?' in url:
        divider="&"
    else:
        divider="?"

    # Try and load as much as five pages which equals 50 series
    # Get total number of pages that are available
    maxCount = GetTotalPageCount(url)

    if maxCount > 5:
        maxCount=5

    index=0
    while index < maxCount:
        index =index+1
        new_url = url + divider +"block=1&partial=1&pageNumber="+str(index)
        xbmc.log("Viewtv new url: " + new_url)
        LoadTvSeriesJson(new_url)
        
    SortListItems()
    xbmc.executebuiltin("Container.SetViewMode(500)")
    #LoadTvSeries(url)
elif mode=='seasons':
    GetSeasonsJson(url)
elif mode=='channels':
	SetupChannelsMenu()
elif mode=='tv':
	SetupTvMenu()
	xbmcplugin.addSortMethod( thisPlugin, sortMethod=xbmcplugin.SORT_METHOD_LABEL )
elif mode=="childrentv":
	SetupChildrenTvMenu()
elif mode=="childrenmovies":
	SetupChildrenMoviesMenu()
elif mode=="children":
	SetupChildrenMenu()
elif mode=='movies':
	SetupMovieMenu()
	xbmcplugin.addSortMethod( thisPlugin, sortMethod=xbmcplugin.SORT_METHOD_LABEL )
elif mode=='view':

    #Valid = True

    #adultName = GetAdultName()
    #if adultName in url:

    #    Valid=False
    #    xbmc.log("URL contains Adult content")
    #    value=""

    #    if SETTINGS_USE_PARENTAL_CONTROL:
    #        value = get_input("Pin-code","",True)
    #    else:
    #        heading=unicode(__language__(4054)).encode('utf-8')
    #        line1=unicode(__language__(4055)).encode('utf-8')
    #        line2=unicode(__language__(4056)).encode('utf-8')
    #        yesLabel=unicode(__language__(4057)).encode('utf-8')
    #        noLabel=unicode(__language__(4058)).encode('utf-8')

    #        result = xbmcgui.Dialog().yesno(heading,line1,line2,"",noLabel,yesLabel)
    #        if result:
    #            value = SETTINGS_PINCODE
            

    #    if value==SETTINGS_PINCODE:
    #        Valid = True
    #        xbmc.log("Pin-code was correct")
    #        xbmc.log("Sending Age verification to Viaplay")
    #    else:
    #        xbmc.log("Pin-code was incorrect!")
    #        xbmcgui.Dialog().ok( unicode(__language__(4049)).encode('utf-8'), unicode(__language__(4052)).encode('utf-8')) 
    #        url = GetAgeVerificationUrl() + urllib.quote_plus(url)
    #if Valid:
    if '?' in url:
        divider="&"
    else:
        divider="?"

    # Try and load as much as five pages which equals 50 series
    # Get total number of pages that are available
    maxCount = GetTotalPageCount(url)

    if maxCount > 5:
        maxCount=5

    index=0
    while index < maxCount:
        index =index+1
        new_url = url + divider +"block=1&partial=1&pageNumber="+str(index)
        xbmc.log("View new url: " + new_url)
        LoadMoviesJson(new_url)

    
    SortListItems()
    xbmcplugin.setContent(thisPlugin, 'movies')
    xbmc.executebuiltin("Container.SetViewMode(508)")

elif mode=='categoriestv':
	SetupCategoriesTV()
elif mode=='streamviaplay':
    #StreamViaplay("","168763","","","")
    #xbmcgui.Dialog().ok( "Platform", os.name )
    

    listitem = xbmcgui.ListItem("",iconImage="", thumbnailImage="")
    #listitem.setThumbnailImage(imageurl)
    listitem.setInfo('video', {'Title': ""})#, 'plotoutline ':'21:00 - BBC World news London live'
    listitem.setInfo('video', {'studio': ""})
    test=""
    xbmc.Player().play(test, listitem)

elif mode=='settings':
	__settings__.openSettings()
	ReloadSettings()
	#response = xbmc.executeJSONRPC ( '{"jsonrpc":"2.0", "method":"Player.GetItem", "params":{"playerid":0, "properties":["artist","musicbrainzartistid"]},"id":1}' )
	# xbmc.log("Send jsonrpc broadcast NotifyAll")
	# xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"JSONRPC.NotifyAll","params":{"sender":"Viaplay","message":"Starting Viaplaylauncher"},"id":"1"}')
	#{"jsonrpc":"2.0","method":"System.OnQuit","params":{"data":0,"sender":"xbmc"}}
	#JSONRPC.Ping
	# xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "JSONRPC.Ping"}')
	# xbmc.log("Broadcast sent")
elif mode=='categories':
	SetupCategories()
elif mode=='play_live':
    if SETTINGS_USE_ANDROID:
        StreamViaplay(url,productid,strmtitle,strmname,strmimage)
    else:
        PlayUrl(url,"channel","")
elif mode == 'play':
	#path=CreateHtmlFile(url)
	#webplayer = xbmc.Player()
	#webplayer.play(path)
	#if url.find("tv") > 0:
	#	short_url = url.replace(GetDomain(),"")
	#	xbmc.log("Title from url: " + GetTitleFromUrl(short_url))
	#	xbmc.log("Episode from URL: " + GetEpisode(short_url))
	#	xbmc.log("Season from URL: " + GetSeason(short_url))
	#	AddWatchedEpisode(GetTitleFromUrl(short_url),GetSeason(short_url),GetEpisode(short_url))
	#	xbmc.executebuiltin("Container.Refresh")

	#xbmc.log("Play URL: " + url)
	#if(SETTINGS_USE_IPAD==True):
	#	if url.find("tv") > 0:
	#		info=GetEpisodeInfo(url)
	#		StreamViaplay(url,info.title,info.episodeTitle,season,episode,image)
	#	else:
	#		info=GetMovieInfo(url)
	#		movieTitle = FixHtmlString(info.title).decode("utf-8")
	#		StreamViaplay(url,movieTitle,"","","",info.image)
	#else:
	#	PlayUrl(url)
    xbmc.executebuiltin("ActivateWindow(busydialog)")
    
    if SETTINGS_USE_ANDROID:
        StreamViaplay(url,productid,strmtitle,strmname,strmimage)
    else:
        if not productid=="0":
            AddWatchedProduct(productid)
        PlayUrl(url,contenttype,productid)
    #StreamViaplay(url,productid)
    #xbmcgui.Dialog().ok( "Play", url )
#xbmcplugin.addSortMethod( thisPlugin, sortMethod=xbmcplugin.SORT_METHOD_LABEL )
xbmcplugin.endOfDirectory(thisPlugin)