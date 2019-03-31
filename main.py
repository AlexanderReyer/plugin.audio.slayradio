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
        xbmcgui.Dialog().textviewer("nach replace", response)
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

    xbmcgui.Dialog().textviewer("startmenue Liste ", str(streamlinks))
    for link in streamlinks:
        #if not link is None: #!= "":
            # extinf
            # http
        #url = build_url({"menuemode":"play", "streamurl":link["url"]})
        url = link["url"]
        dialog.notification(str(link["name"]), str(url), xbmcgui.NOTIFICATION_INFO, 1000)    
        li = xbmcgui.ListItem(link["name"], iconImage='DefaultVideo.png')
        li.setProperty('IsPlayable', 'True')
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)
        

    xbmcplugin.endOfDirectory(addon_handle)
    return

    # suchen
    video_play_url 	= "nothing"
    url 			= build_url({'menuemode' :'search', 'playlink' : video_play_url})
    li 				= xbmcgui.ListItem("Suchen", iconImage='DefaultVideo.png')
    li.setProperty('IsPlayable' , 'false')
    is_folder = True
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=is_folder)
    
    # alphabetisch
    video_play_url 	= "nothing"
    url 			= build_url({'menuemode' :'alphabetical', 'playlink' : video_play_url})
    li 				= xbmcgui.ListItem("Liste alphabetisch", iconImage='DefaultVideo.png')
    li.setProperty('IsPlayable' , 'false')
    is_folder = True
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=is_folder)
    
    # Genre
    video_play_url 	= "nothing"
    url 			= build_url({'menuemode' :'genre', 'playlink' : video_play_url})
    li 				= xbmcgui.ListItem("Liste Genres", iconImage='DefaultVideo.png')
    li.setProperty('IsPlayable' , 'false')
    is_folder = True
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=is_folder)
    
    xbmcplugin.endOfDirectory(addon_handle)
    #exit(0)

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


def get_seriesplot(link):
    r       = requests.get(siteurl + link)
    soup    = BeautifulSoup(r.content, "html.parser")
    tag = soup.find("p", {"class":"seri_des"})
    #xbmc.log("get_seriesplot " + link + str(tag.get_text().encode("utf-8")),level=xbmc.LOGNOTICE)
    plottext = tag.attrs["data-full-description"].encode("utf-8")
    #xbmc.log("get_seriesplot full: " + str(tag.attrs["data-full-description"].encode("utf-8")),level=xbmc.LOGNOTICE)
    return plottext

def get_seriesdetails(link):
    seriesdetails = dict()
    r       = requests.get(siteurl + link)
    soup    = BeautifulSoup(r.content, "html.parser")
    # plot    
    tag = soup.find("p", {"class":"seri_des"})
    #xbmc.log("get_seriesplot " + link + str(tag.get_text().encode("utf-8")),level=xbmc.LOGNOTICE)
    seriesdetails["plot"] = tag.attrs["data-full-description"].encode("utf-8")
    # thumb
    tag = soup.find("div", {"class":"seriesCoverBox"})
    tag = tag.img
    seriesdetails["thumb"] = siteurl + tag.attrs["src"]    
    return seriesdetails


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
    xbmcgui.Dialog().textviewer("playstream", str(streamlink).strip("[]").replace("'",""))
    li = xbmcgui.ListItem(url=str(streamlink).strip("[]").replace("'",""))
    li.setProperty("IsPlayable","True")
    li.setPath(str(streamlink).strip("[]").replace("'",""))
    xbmcplugin.setResolvedUrl(addon_handle, True, listitem=li)
    #dialog.notification("playstream", str(streamlink).strip("[]").replace("'",""), xbmcgui.NOTIFICATION_INFO, 2000)

def play_hosterfile(link):
    options = webdriver.ChromeOptions()
    #options.add_argument("headless")
    options.add_argument(
            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36')
    #options.add_argument(r'user-data-dir=C:\Users\mycomputer\AppData\Local\Google\Chrome\User Data')
    driver = webdriver.Chrome(executable_path='Z:\\downlds_orbit\\chromedriver_win32\\chromedriver.exe', chrome_options=options)

    driver.get(siteurl + link)

    wait    = WebDriverWait(driver, 1000)
    driver.implicitly_wait(0)

    h1tag = driver.find_element_by_tag_name("h1")
    dialog.notification(link, str(h1tag.text.encode("utf-8")), xbmcgui.NOTIFICATION_INFO, 2000)

    #waitel  =wait.until(ec.invisibility_of_element_located((By.XPATH, "//h1[text()='Deine Anfrage wird']" )))
    waitel  =wait.until(ec.invisibility_of_element_located((By.XPATH, "//h1[contains(text(),'Deine Anfrage wird')]" )))

    driver.implicitly_wait(30)
    #print("\r\n " + driver.page_source + " \r\n")
    path = driver.current_url
    xbmc.log("play_hosterfile url " + str(path), level=xbmc.LOGNOTICE)
    #print(driver.current_url)
    #driver.quit()
    # Create a playable item with a path to play.
    play_item = xbmcgui.ListItem(path=path)
    play_item.setProperty('IsPlayable' , 'true')
    # Pass the item to the Kodi player.
    #xbmcplugin.setResolvedUrl(_handle, True, listitem=play_item)
    # -----------
    vid_url = play_item.getfilename()
    stream_url = resolve_url(vid_url)
    if stream_url:
        play_item.setPath(stream_url)
    # Pass the item to the Kodi player.
    xbmcplugin.setResolvedUrl(addon_handle, True, listitem=play_item)
    return

def play_testlink():
    try:
	#path 	= "http://www.vidsplay.com/wp-content/uploads/2017/04/alligator.mp4"
        #path = "https://openload.co/f/bYrQpQt2NTg"
        path = "https://openload.co/embed/bYrQpQt2NTg"
        # path = "https://vivo.sx/2cb470e492"       # z - beginning
        xbmc.log("play_hosterfile url " + str(path), level=xbmc.LOGNOTICE)
        #print(driver.current_url)
        #driver.quit()
        # Create a playable item with a path to play.
        play_item = xbmcgui.ListItem(path=path)
        play_item.setProperty('IsPlayable' , 'true')
        # Pass the item to the Kodi player.
        #xbmcplugin.setResolvedUrl(_handle, True, listitem=play_item)
        # -----------
        vid_url = play_item.getfilename()
        xbmc.log("play_item.getfilename() url " + str(vid_url), level=xbmc.LOGNOTICE)
        stream_url = resolve_url(vid_url)
        xbmc.log("resolve_url(vid_url) stream_url " + str(stream_url), level=xbmc.LOGNOTICE)
        if stream_url:
            play_item.setPath(stream_url)
        else:
            play_item.setPath(path)
            dialog.notification(str("resolve_url = False"), str(path), xbmcgui.NOTIFICATION_INFO, 2000)
        # Pass the item to the Kodi player.
        xbmcplugin.setResolvedUrl(addon_handle, True, listitem=play_item)
    except Exception as e:
        xbmc.log(str(traceback.format_exc().encode("utf-8")), level=xbmc.LOGNOTICE)
        dialog.notification(str(traceback.format_exc().encode("utf-8")), str(path), xbmcgui.NOTIFICATION_INFO, 2000)
    return

if menuemode is None:
    startmenue()
elif menuemode[0] == "play":
    xbmcgui.Dialog().textviewer("play", str(addon_args).encode())
    playstream(addon_args.get("streamurl"))
    pass
#elif menuemode[0] == "search":
