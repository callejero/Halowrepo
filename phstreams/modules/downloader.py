# -*- coding: utf-8 -*-

'''
    Phoenix Add-on
    Copyright (C) 2015 Blazetamer
    Copyright (C) 2015 lambda
    Copyright (C) 2015 crzen

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

import urllib,urllib2,re,os,sys,threading,time
import xbmc,xbmcgui,xbmcaddon,xbmcplugin
import pyxbmct.addonwindow as pyxbmct

try:
    import StorageServer
except:
    import storageserverdummy as StorageServer


addonName = xbmcaddon.Addon().getAddonInfo('name')
addonFanart = xbmcaddon.Addon().getAddonInfo('fanart')
addonIcon = xbmcaddon.Addon().getAddonInfo('icon')
addonDownloads = xbmcaddon.Addon().getSetting('download_folder')
addonPath = xbmcaddon.Addon().getAddonInfo('path')

cache = StorageServer.StorageServer(addonName, 0)



def DOWNLOADER():

    item = xbmcgui.ListItem('[COLOR blue]Start Downloads[/COLOR]', iconImage=addonIcon, thumbnailImage=addonIcon)
    item.addContextMenuItems([], replaceItems=True)
    item.setProperty('fanart_image', addonFanart)
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=sys.argv[0]+'?mode=downloader_start',listitem=item)

    queue = cache.get('queue')
    try: queue = sorted(eval(queue), key=lambda item: item[1])
    except: queue = []

    for i in queue:
        try:
            cm = []
            cm.append(('[COLOR red]Remove From Queue[/COLOR]', 'RunPlugin(%s?mode=downloader_remove&url=%s)' % (sys.argv[0], urllib.quote_plus(i[1]))))
            item = xbmcgui.ListItem(i[0], iconImage=i[2], thumbnailImage=i[2])
            item.addContextMenuItems(cm, replaceItems=True)
            item.setProperty('fanart_image', addonFanart)
            xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=i[1],listitem=item)
        except:
            pass

    infoqueue = cache.get('infoqueue')

    if infoqueue:
        item = xbmcgui.ListItem('[COLOR gold]Download Status[/COLOR]', iconImage=addonIcon, thumbnailImage=addonIcon)
        item.addContextMenuItems([], replaceItems=True)
        item.setProperty('fanart_image', addonFanart)
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=sys.argv[0]+'?mode=downloader_status',listitem=item)


def DOWNLOADER_ADD(name,url,image):

    try: queue = eval(cache.get('queue'))
    except: queue = []

    if name in [i[0] for i in queue]:
        return xbmc.executebuiltin("Notification(%s,%s, %s, %s)" % (name, '[COLOR red]Item Already In Your Queue[/COLOR]', 3000, addonIcon))

    import commonresolvers
    url = commonresolvers.get(url).result

    if type(url) == list:
        url = sorted(url, key=lambda k: k['quality'])
        url = url[0]['url']

    url = url.split('|')[0]

    import urlparse
    ext = os.path.splitext(urlparse.urlparse(url).path)[1][1:]
    if not ext in ['mp4', 'mkv', 'flv', 'avi', 'mpg']: ext = 'mp4'

    xbmc.sleep(1000)

    queue.append((name,url,image,ext,addonName))
    cache.set('queue', str(queue))

    xbmc.executebuiltin("Notification(%s,%s, %s, %s)" % (name, '[COLOR gold]Item Added To Your Queue[/COLOR]', 3000, addonIcon))


def DOWNLOADER_REMOVE(url):
    try:
        queue = cache.get('queue')
        queue = sorted(eval(queue), key=lambda item: item[1])
        queue = [i for i in queue if not i[1] == url]

        cache.set('queue', str(queue))
        xbmc.executebuiltin('Container.Refresh')
    except:
        xbmc.executebuiltin("Notification(%s,%s, %s, %s)" % ('Can not remove from Queue', 'You need to remove file manually', 3000, addonIcon))


def DOWNLOADER_START():

    if addonDownloads == '':
        return xbmc.executebuiltin("Notification(%s,%s, %s, %s)" % ('File Not Downloadable', 'You need to set your download folder in addon settings first', 3000, addonIcon))

    dlThread = downloadThread()
    dlThread.start()


def DOWNLOADER_STATUS():

    window = MyDownloads('Download Status/Information')
    window.doModal()
    del window


class MyDownloads(pyxbmct.AddonDialogWindow):

    def __init__(self, title='downloadThread'):
        super(MyDownloads, self).__init__(title)
        self.setGeometry(700, 450, 9, 3)
        self.set_info_controls()
        self.set_active_controls()
        #self.set_navigation()
        # Connect a key action (Backspace) to close the window.
        self.connect(pyxbmct.ACTION_NAV_BACK, self.close)
        #self.connect(pyxbmct.ACTION_NAV_BACK, self.stop)
        #print "FILE NAME IS = "+file_name
        
    def set_info_controls(self):
        infoqueue = cache.get('infoqueue')
        #print "HERE IS THE INFO Q = "+infoqueue
        if infoqueue:
          infoqueue_items = sorted(eval(infoqueue), key=lambda item: item[1])
          #print infoqueue_items
          for item in infoqueue_items:
                     
                self.name = item[0]
                self.percent = item[1]
                self.thumb = item[3]
                self.totalsize = item[4]
                self.dlspeed = item[2]
                if self.thumb == '':
                        self.thumb ='http://mecca.watchkodi.com/images/phoenix_icon.png'
                #file_name = dlvars.basename
                file_name = self.name 
                percent = self.percent 
                file_thumb = self.thumb 
                file_total_size = self.totalsize 
                dlspeed = self.dlspeed 
        # Demo for PyXBMCt UI controls.
        no_int_label = pyxbmct.Label('[B][COLOR gold]'+file_name+'[/COLOR][/B]', alignment=pyxbmct.ALIGN_CENTER)
        self.placeControl(no_int_label, 0, 1, 1, 1)
        #
        label_label = pyxbmct.Label('Total File Size', alignment=pyxbmct.ALIGN_CENTER)
        self.placeControl(label_label, 1, 0)
        totalsize_label = pyxbmct.Label(file_total_size, alignment=pyxbmct.ALIGN_CENTER)
        self.placeControl(totalsize_label, 2, 0)
        # Label
        dld_label = pyxbmct.Label('Downloaded', alignment=pyxbmct.ALIGN_CENTER)
        self.placeControl(dld_label, 1, 1)
        dld_label = pyxbmct.Label(str(percent) +"%", alignment=pyxbmct.ALIGN_CENTER)
        self.placeControl(dld_label, 2, 1)
        #
        #
        dlSpeed_label = pyxbmct.Label('Download Speed', alignment=pyxbmct.ALIGN_CENTER)
        self.placeControl(dlSpeed_label, 1, 2)
        speed_label = pyxbmct.Label(str(dlspeed), alignment=pyxbmct.ALIGN_CENTER)
        self.placeControl(speed_label, 2, 2)
        # TextBox
        #
        #image_label = pyxbmct.Label('Cover Art>>')
        #self.placeControl(image_label, 5, 0)
        self.image = pyxbmct.Image(file_thumb)
        self.placeControl(self.image, 3, 1, 6, 1)
        

    def set_active_controls(self):
        '''int_label = pyxbmct.Label(file_name, alignment=pyxbmct.ALIGN_CENTER)
        self.placeControl(int_label, 0, 2, 1, 2)'''
        
        # Close Button
        self.button = pyxbmct.Button('Close')
        self.placeControl(self.button, 8, 2)
        # Connect control to close the window.
        self.connect(self.button, self.close)
        
        #Stop DL Button
        #self.button = pyxbmct.Button('Stop DL')
        #self.placeControl(self.button, 8, 0)
        # Connect control to stop the download.
        #self.connect(self.button, self.close)

    

    def radio_update(self):
        # Update radiobutton caption on toggle
        if self.radiobutton.isSelected():
            self.radiobutton.setLabel('On')
        else:
            self.radiobutton.setLabel('Off')

    def list_update(self):
        # Update list_item label when navigating through the list.
        try:
            if self.getFocus() == self.list:
                self.list_item_label.setLabel(self.list.getListItem(self.list.getSelectedPosition()).getLabel())
            else:
                self.list_item_label.setLabel('')
        except (RuntimeError, SystemError):
            pass

    def setAnimation(self, control):
        # Set fade animation for all add-on window controls
        control.setAnimations([('WindowOpen', 'effect=fade start=0 end=100 time=500',),
                                ('WindowClose', 'effect=fade start=100 end=0 time=500',)])


class downloadThread (threading.Thread):
    '''
    def __init__(self, name, url, thumb, console, ext):
        threading.Thread.__init__(self)
        self.thumb = thumb
        self.kill = False
        #self.kill = threading.Event()
        basename = 'TEST NAME'
    '''
    
    def __init__(self):
        threading.Thread.__init__(self)
        self.kill = False
        #self.kill = threading.Event()
        basename = 'TEST NAME'
        
    def kill(self):
        self.kill = True

    def stop(self):
        print ('killing queue ') + str(self.kill)
        self.kill = True
        print ('killing queue ') + str(self.kill)

#NEW INFO Q==============

    def addInfoQueue(self,file_name,percent,dlspeed,file_thumb,file_total_size):
             infoqueue = cache.get('infoqueue')
             infoqueue_items = []
             if infoqueue:
                  cache.delete('infoqueue')

             infoqueue_items.append((file_name,percent,dlspeed,file_thumb,file_total_size))
             cache.set('infoqueue', str(infoqueue_items))
             #xbmc.executebuiltin("Notification(%s,%s, %s, %s)" % ('[COLOR gold]Item Added To Your Queue [/COLOR]', name + ' Was Added To Your Download Queue', 5000, thumb))

    def run(self):
        print '\t\t\t Begin phoenix downloader method'
        #dialog=xbmcgui.Dialog(); dialog.ok("DEBUG ", "Begin phoenix downloader method")
        queue = cache.get('queue')
        if queue:
            # Reset failed and success files by removing them
            dlsuccess_list = os.path.join(addonPath,'DLsuccesslist.txt')
            if os.path.exists(dlsuccess_list):
                os.remove(dlsuccess_list)
            dlfailed_list = os.path.join(addonPath,'DLfailedlist.txt')
            #failed = open(dlfailed_list, 'wb'); failed.close()
            if os.path.exists(dlfailed_list):
                os.remove(dlfailed_list)

            queue_items = sorted(eval(queue), key=lambda item: item[1])
            print '\t\t\t queue_items' ; print '\t\t\t' + str(queue_items)
            for item in queue_items:
                self.name = item[0]
                self.url = item[1]
                self.ext = item[3]
                self.console = item[4]
                thumb = item[2]
                #global file_name
                #basename = 'TEST NAME'

                #print queue_items
                self.path = addonDownloads + self.console
                if not os.path.exists(self.path):
                    os.makedirs(self.path)

                self.file_name = '%s.%s' % (self.name, self.ext)

                xbmc.executebuiltin("Notification(%s,%s, %s, %s)" % ('[COLOR gold]Downloads Started[/COLOR]', self.name + ' Is Downloading', 7000, thumb))
                try:
                    u = urllib2.urlopen(self.url) # might need a timeout added
                except Exception,e:
                    print'\t\t\t Name= '+ str(self.name), '\t\t\t Url= ' + str(self.url), '\t\t\t ERROR - File Failed To Open' + str(e)
                    xbmc.executebuiltin("Notification(%s,%s, %s, %s)" % ('Error', self.name + ' Failed To Open File', 5000, thumb))
                    # Add failed download name to dlfailed_list
                    dlfailed = open(dlfailed_list, 'ab')
                    dlfailed.write(self.name +'\n')
                    dlfailed.close()
                    DOWNLOADER_REMOVE(self.url)
                    #dialog=xbmcgui.Dialog(); dialog.ok("DEBUG ", "Failed To Open File", str(self.name))
                    continue

                meta = u.info()
                #print meta
                if 'Content-Length' not in meta:
                    file_size_string = 'Unknown'
                    file_size = 1  #
                else:
                    file_size_string = ''
                    file_size =  int(meta.getheaders("Content-Length")[0])
                    #print file_size

                # todo: Check for total disk size and free space of DL location.
                #       Cancel downloads if not enough free space.
                #       If unknown file size download until 10% of total disk size is free

                f = open(os.path.join(self.path,self.file_name), 'ab')
                existSize = os.path.getsize(os.path.join(self.path,self.file_name))
                if file_size_string != 'Unknown':
                    # only download the remaining bytes using byte range
                    for RangeEntry in 'Ranges','Range','':
                        headers = u.info()
                        if RangeEntry != '':
                            #print "TRYING BYTE SIZES"
                            try:
                                # this request sets the pointer to where you want to start reading
                                req = urllib2.Request(self.url)
                                # reopen url with preset byte range in header
                                req.headers["Range"] = 'bytes=%s-' %existSize
                                u = urllib2.urlopen(req)
                                # Set the begining write point
                                file_size_dl = existSize
                                break
                            except Exception, e:
                                file_size_dl = 0
                                print '\t\t error byte range not supported ' + str(e)  # Expected error: HTTP Error 416: Requested Range Not Satisfiable'
                else:
                    print ('\t\t\t Remote file size is unknown')
                    file_size_dl = 0  # byte range not supported continue as usual

                # Number of bytes to read at a time
                block_sz = 500 * 1024

                # Download init
                starttime = time.time()
                startSize = file_size_dl

                # Main Download engine
                while (file_size_string == 'Unknown' or (existSize <= file_size and file_size >= 1)) \
                            and queue and not self.kill:
                        #print ('\t\t\t checking kill ') + str(self.kill)
                        # keep from adding empty bytes after end of file
                        if (existSize + block_sz) > file_size and file_size > 1:
                            block_sz = file_size - existSize  # only read the remainder
                        buffer = u.read(block_sz)
                        if buffer == '':  # end of file
                            break
                        # dont overwrite existing data
                        if file_size_dl >= existSize:
                                f.write(buffer)
                        file_size_dl += block_sz

                        # calculate the percentage downloaded
                        try:
                            deltatime = time.time() - starttime
                            if file_size <= 1 or file_size_string == 'Unknown' :
                                if deltatime >= 150:  # in seconds. update display every 2.5 min
                                    xbmc.executebuiltin("Notification(%s,%s, %s, %s)" % (self.name, str(percent) + 'Downloading...', 10, thumb))
                            else:
                                percent = file_size_dl * 100 / file_size
                                #if percent in range(10,101,10):

                                #Actual size info
                                totalsize = file_size /1000000
                                if totalsize < 1000:
                                    full_size = str(totalsize) +"MB"
                                else:
                                    totalgbsize = totalsize /float(1000)
                                    full_size =str(totalgbsize) +"GB"
                                truesize = file_size_dl /1000000
                                if truesize < 1000:
                                    dl_size = str(truesize) +"MB"
                                else:
                                    truegbsize = truesize /float(1000)
                                    dl_size =str(truegbsize) +"GB"
                                #Actual Size Info

                                #xbmc.executebuiltin("Notification(%s,%s, %s, %s)" % (self.name, str(percent) + '% Complete of '+ full_size, 10, addonIcon))
                                #calculate the download speed
                                deltasize = file_size_dl - startSize
                                dlspeed = (deltasize / 1024) / deltatime

                                starttime = time.time()
                                startSize = file_size_dl
                                #print ('\t\t\t Download Speed= ' + str(dlspeed) + ' kbs')
                                #START INFO Q APPEND==========

                                self.addInfoQueue(self.name,percent,dlspeed,thumb,full_size)
                        except Exception,e:
                           print('\t\t\t ERROR DISPLAY ' + str(e))

                f.close()
                xbmc.executebuiltin("Notification(%s,%s, %s, %s)" % ('[COLOR gold]Download Complete[/COLOR]', self.name + ' Completed', 5000, addonIcon))
                # Add successful download name to dlsuccess_list
                dlsuccess = open(dlsuccess_list, 'ab')
                dlsuccess.write(self.name +'\n')
                dlsuccess.close()
                cache.delete('infoqueue')
                DOWNLOADER_REMOVE(self.url)

        xbmc.executebuiltin("Notification(%s,%s, %s, %s)" % ('[COLOR gold]Process Complete[/COLOR]', self.name + ' is in your downloads folder', 5000, addonIcon))
        # todo: display the results of the dl queue process for failed and or successful
        print '\t\t\tthread is done'
        #dialog=xbmcgui.Dialog(); dialog.ok("DEBUG ", "thread is done")


