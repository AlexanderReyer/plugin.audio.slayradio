#
# import web_pdb; web_pdb.set_trace()
# <import addon="script.module.web-pdb" />
#


import urlparse                         # base64 encoding
import sys,urllib                       # Argumenten-Vektor
#from urllib.request import urlopen
import xbmc, xbmcgui, xbmcaddon, xbmcplugin
import requests                         # url lesen
import traceback
#import urlresolver
from bs4 import BeautifulSoup           # seriennamen
import re                               # regulaere Ausdruecke

#sys.setdefaultencoding('utf-8')

addon_url       = sys.argv[0]
addon_handle    = int(sys.argv[1])
addon_args      = urlparse.parse_qs(sys.argv[2][1:])
siteurl         = "https://www.slayradio.org"
streamlinks     = list()
usemono         = True

dialog          = xbmcgui.Dialog()
menuemode       = addon_args.get('menuemode', None)


def build_url(query):
    return addon_url + '?' + urllib.urlencode(query)

def get_m3u(link):
    global streamlinks
    try:
        m3ulinks = list()
        r = requests.get(link)
        soup = BeautifulSoup(r.content, "html.parser")
        tag = soup.find("div", {"class":"item", "id":"sidebar-tunein"})
        tag = tag.find("p", {"class":"center"})
        for anchor in tag.findAll("a"):
            m3ulinks.append(anchor["href"])
        #response = urlopen(link + m3ulinks[0]) # Python 3
        #xbmcgui.Dialog().textviewer(str(soup.title.getText()), str(m3ulinks))
        #dialog.notification("m3u high", str(link + m3ulinks[0]), xbmcgui.NOTIFICATION_INFO, 1000)    
        #xbmc.log("m3u high link: " + str(link + m3ulinks[0]),level=xbmc.LOGNOTICE)
        #response = urllib.urlopen(link + m3ulinks[0]) # Python 2
        response = requests.get(link + m3ulinks[0]) # Python 2
        #xbmcgui.Dialog().textviewer(str(soup.title.getText()), str(response.content))
        #bytedata = response.read()
        response = response.content.replace("#EXTM3U\n\n","")
        #xbmcgui.Dialog().textviewer("nach replace", response)
        bytedata = response.encode("utf-8")
        # m3u content
        #extm3u \n\n
        streamlinkstemp = str(bytedata.decode("utf-8")).split("\r\n")
        streamlinkstemp.remove("")
        #xbmcgui.Dialog().textviewer(str(soup.title.getText()), str(streamlinks).encode())

        l = list()
        d = dict()
        for entry in streamlinkstemp:
            if entry.startswith("#EXT"):
                d["name"] = entry[11:]
            if entry.startswith("http"):
                d["url"] = entry
                streamlinks.append(d)
                d = dict()      # neu fuer den Nachfolger
        #xbmcgui.Dialog().textviewer("Liste aus dict", str(streamlinks))

        d = dict()
        d["name"] = "Darthradio"
        d["url"] = "http://www.darthradio.tk:8001/dstream"
        streamlinks.append(d)
        d = dict()
        d["name"] = "Radio Paralax"
        d["url"] = "http://radio-paralax.de:8000"
        streamlinks.append(d)
        d = dict()
        d["name"] = "UK Demo Scene"
        d["url"] = "http://cgm-stream.noip.me:8000/mpd"
        streamlinks.append(d)

        return
        # -- debug
        i = 0
        for url in streamlinks:
            i = i + 1
            dialog.notification(str(i), str(url), xbmcgui.NOTIFICATION_INFO, 1000)    
    except Exception as e:
        xbmcgui.Dialog().textviewer("Ausnahme", str(traceback.format_exc()))


#def menue_atart():
def startmenue():
    #global addon_handle
    global streamlinks

    get_m3u(siteurl)

    #xbmcgui.Dialog().textviewer("startmenue Liste ", str(streamlinks))
    for link in streamlinks:
        #if not link is None: #!= "":
            # extinf
            # http
        url = build_url({"menuemode":"play", "url":link["url"]})
        #url = link["url"]
        dialog.notification(str(link["name"]), str(link["url"]), xbmcgui.NOTIFICATION_INFO, 1000)    
        li = xbmcgui.ListItem(link["name"], iconImage='DefaultAudio.png')
        li.setProperty('IsPlayable', 'True')
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)
        
    xbmcplugin.setContent(addon_handle, 'songs')
    xbmcplugin.endOfDirectory(addon_handle)

def getKeyboardInput():
	kb = xbmc.Keyboard("default", "heading")
	kb.setDefault("Batman")
	kb.setHeading("Bitte Serienname eingeben")
	kb.setHiddenInput(False)
	kb.doModal()
	if(kb.isConfirmed()):
		search_term = kb.getText()
		return(search_term)
	else:
		return("")

def liste_episoden(link):
    global episodelist
    global episodelistdetail
    seriesdetails = dict()
    #del resultlistalpha[1:]     # liste loeschen zum Neuladen
    find_staffellist(link) #"/serie/stream/penny-dreadful")
    find_episodenames(staffellist)
    dialog.notification("gefundene Elemente", str(len(staffellist)), xbmcgui.NOTIFICATION_INFO, 2000)
    dialog.notification(str(staffellist[0]), str(episodelistdetail[episodelist[0]]).strip("[]").replace("'",""), xbmcgui.NOTIFICATION_INFO, 2000)
    #plot = get_seriesplot(link)	#li.setInfo(type='video', infoLabels={"plot":get_seriesplot(str(dictseries[serelement]["href"])) } )
    seriesdetails = get_seriesdetails(link)

    for serelement in episodelist:
	video_play_url 	= "http://www.vidsplay.com/wp-content/uploads/2017/04/alligator.mp4"
	#"https://delivery--rsc-1.vivo.sx/vod/nqqatRvDY7dqGZxm6uavkg/1552272854/0070800044"
	#https://vivo.sx/4c02c75dee"
	#http://www.vidsplay.com/wp-content/uploads/2017/04/alligator.mp4"
	url 			= build_url({'menuemode' :'showhoster', 'name':serelement, 'href':str(episodelistdetail[serelement]["href"]).strip("[]").replace("'",""), 'playlink' : video_play_url})
	#url 			= build_url({'menuemode' :'showhoster', 'name':serelement, 'href':str(episodelistdetail[episodelist[0]]["href"]).strip("[]").replace("'",""), 'playlink' : video_play_url})
	#url 			= build_url({'menuemode' :'showhoster', 'name':serelement, 'href':str(episodelistdetail[serelement]["href"]), 'playlink' : video_play_url})
	li 			= xbmcgui.ListItem(serelement, iconImage='DefaultVideo.png')
	li.setProperty('IsPlayable' , 'true')
	li.setInfo(type='video', infoLabels={'genre': 'genre', 'plot': seriesdetails["plot"], 'writer':'Robert D. Siegel', 'director':'S.Spielberg' })
	li.setArt({"thumb":seriesdetails["thumb"]})
	is_folder = True
	xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=is_folder)
    
    #dialog.notification(str(dictseries[0]), str(dictseries[resultlistalpha[0]]).strip("[]").replace("'",""), xbmcgui.NOTIFICATION_INFO, 2000)
    xbmc.log("liste_episoden. episodelist[0] ist " + str(episodelist[0]) + " Details:" + str(episodelistdetail[episodelist[0]]["href"]).strip("[]").replace("'",""), level=xbmc.LOGNOTICE)
    #xbmc.log("seriesalphab. dictseries[0] ist " + str(dictseries[resultlistalpha[0]]).strip("[]").replace("'",""),level=xbmc.LOGNOTICE)
    #dialog.notification("listitem", "ende suchen", xbmcgui.NOTIFICATION_INFO, 5000)
    xbmcplugin.endOfDirectory(addon_handle)


def resolve_url(url):
    duration=7500   #in milliseconds
    message = "Cannot Play URL"
    #stream_url = urlresolver.HostedMediaFile(url=url).resolve()
    stream_url = ""
    # If urlresolver returns false then the video url was not resolved.
    if not stream_url:
        dialog = xbmcgui.Dialog()
        dialog.notification("URL Resolver Error", message, xbmcgui.NOTIFICATION_INFO, duration)
        return False
    else:        
        return stream_url    

def playstream(streamlink):
    #streamlink = "http://relay1.slayradio.org:8300/" # AAC
    #streamlink = "http://www.darthradio.tk:8001/dstream"
    #streamlink = "http://radio-paralax.de:8000"
    #streamlink = "http://cgm-stream.noip.me:8000/mpd"
    streamurl = str(streamlink).strip("[]").replace("'","")
    #xbmcgui.Dialog().textviewer("playstream", streamurl)
    li = xbmcgui.ListItem(path=streamurl)
    li.setProperty('mimetype', "audio/mpeg")
    li.setProperty("IsPlayable", "True")
    #xbmcgui.Dialog().textviewer("filename li", str(li.getfilename()))
    #li.setPath(streamurl)
    xbmcplugin.setResolvedUrl(addon_handle, True, listitem=li)
    #dialog.notification("playstream", str(streamlink).strip("[]").replace("'",""), xbmcgui.NOTIFICATION_INFO, 2000)


if menuemode is None:
    startmenue()
elif menuemode[0] == "play":
    #xbmcgui.Dialog().textviewer("play", str(addon_args).encode())
    playstream(addon_args.get("url"))
