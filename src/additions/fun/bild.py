# -*- coding: utf-8 -*-
from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.simpleplayer import SimplePlayer
from Plugins.Extensions.MediaPortal.resources.coverhelper import CoverHelper

def bildEntry(entry):
    return [entry,
        (eListboxPythonMultiContent.TYPE_TEXT, 20, 0, 860, 25, 0, RT_HALIGN_CENTER | RT_VALIGN_CENTER, entry[0])
        ]

def bildEntry1(entry):
    return [entry,
        (eListboxPythonMultiContent.TYPE_TEXT, 20, 0, 860, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry[0])
        ]
    
class bildFirstScreen(Screen):

    def __init__(self, session):
        self.session = session
        path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/%s/oldGenreScreen.xml" % config.mediaportal.skin.value
        if not fileExists(path):
            path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/original/oldGenreScreen.xml"
        print path
        with open(path, "r") as f:
            self.skin = f.read()
            f.close()

        Screen.__init__(self, session)

        self["actions"]  = ActionMap(["OkCancelActions", "ShortcutActions", "WizardActions", "ColorActions", "SetupActions", "NumberActions", "MenuActions"], {
            "ok"    : self.keyOK,
            "cancel": self.keyCancel
        }, -1)

        self['title'] = Label("v0.1-beta")
        self['name'] = Label("Bild.de")
        self['coverArt'] = Pixmap()

        self.keyLocked = True
        self.filmliste = []
        self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
        self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
        self.chooseMenuList.l.setItemHeight(25)
        self['genreList'] = self.chooseMenuList

        self.onLayoutFinish.append(self.loadPage)

    def loadPage(self):
        url = "http://www.bild.de/video/startseite/bildchannel-home/video-home-15713248.bild.html"
        getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.parseData).addErrback(self.dataError)

    def parseData(self, data):
        raw = re.findall('<h2>Top-Videos</h2>(.*?)</ol>', data, re.S)
        if raw:
            categorys = re.findall('<li><a href="(.*?)">(.*?)</a></li>', raw[0], re.S)
            self.filmliste = []
            for (bildUrl, bildTitle) in categorys:
                self.filmliste.append((decodeHtml(bildTitle), bildUrl))
            self.chooseMenuList.setList(map(bildEntry, self.filmliste))
            self.keyLocked = False

    def dataError(self, error):
        printl(error,self,"E")
        
    def keyOK(self):
        Link = self['genreList'].getCurrent()[0][1]
        bildLink = "http://www.bild.de" + Link
        self.session.open(bildSecondScreen, bildLink)

    def keyCancel(self):
        self.close()
        
class bildSecondScreen(Screen):

	def __init__(self, session, bildLink):
		self.session = session
		self.bildLink = bildLink
		
		path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/%s/kinokisteFilmLetterScreen.xml" % config.mediaportal.skin.value
		if not fileExists(path):
			path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/original/kinokisteFilmLetterScreen.xml"
		print path
		with open(path, "r") as f:
			self.skin = f.read()
			f.close()

		Screen.__init__(self, session)

		self["actions"] = ActionMap(["OkCancelActions", "ShortcutActions", "WizardActions", "ColorActions", "SetupActions", "NumberActions", "MenuActions", "EPGSelectActions"], {
		"ok"    : self.keyOK,
		"cancel": self.keyCancel,
		"up" : self.keyUp,
		"down" : self.keyDown,
		"right" : self.keyRight,
		"left" : self.keyLeft,
		"nextBouquet" : self.keyPageUp,
		"prevBouquet" : self.keyPageDown
		}, -1)

		self['title'] = Label("Bild.de")
		self['name'] = Label("")
		self['page'] = Label("")
		self['handlung'] = Label("")
		self['coverArt'] = Pixmap()

		self.keyLocked = True
		self.filmliste = []
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['genreList'] = self.chooseMenuList
		self.page = 0
		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		url = self.bildLink
		getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.parseData).addErrback(self.dataError)

	def parseData(self, data):
		lastpage = re.findall('<li class="pagLast">.*?page=(.*?),isVideoStartseite', data)
		if lastpage:
			self['page'].setText("%s / %s" % (str(self.page), str(lastpage[0])))
		else:
			self['page'].setText(str(self.page))
	
		raw = re.findall('Neueste Videos</h2>(.*?)class="pagLast">', data, re.S)
		if raw:
			seasons = re.findall('class="active">.*?data-ajax-href="/video/clip/tb-neueste-videos-(.*?),zeigeTSLink=true,page=0,isVideoStartseite=true,view=ajax,contentContextId=(.*?).bild.html"', raw[0], re.S)
			vid_id1 = seasons[0][0]
			vid_id2 = seasons[0][1]
			nexturl = "http://www.bild.de/video/clip/tb-neueste-videos-" + vid_id1 + ",zeigeTSLink=true,page=" + str(self.page) + ",isVideoStartseite=true,view=ajax,contentContextId=" + vid_id2 + ".bild.html"
			data2 = urllib.urlopen(nexturl).read()
			categorys =  re.findall('<div class="hentry.*?href="(.*?)".*?src="(.*?)".*?class="kicker">(.*?)</span>', data2, re.S)
# Fix Me
#           categorys =  re.findall('<div class="hentry.*?href="(.*?)".*?src="(.*?)".*?class="kicker">(.*?)</span>.*?<span class="headline"><span>(.*?)</h3>', data2, re.S)
			self.filmliste = []
			for (bildUrl, bildImage, bildTitle) in categorys:
				self.filmliste.append((decodeHtml(bildTitle), bildUrl, bildImage))
			self.chooseMenuList.setList(map(bildEntry1, self.filmliste))
			self.keyLocked = False
			self.showInfos()

	def dataError(self, error):
		printl(error,self,"E")

	def showInfos(self):
		coverUrl = self['genreList'].getCurrent()[0][2]
#FIXME        
#        handlung = self['genreList'].getCurrent()[0][3].replace('</span>','').replace('<span>',' ')
#        handlung = self['genreList'].getCurrent()[0][3]
#        self['handlung'].setText(decodeHtml(handlung))
		ImageUrl = "%s" % coverUrl
		CoverHelper(self['coverArt']).getCover(ImageUrl)

	def keyLeft(self):
		if self.keyLocked:
			return
		self['genreList'].pageUp()
		self.showInfos()

	def keyRight(self):
		if self.keyLocked:
			return
		self['genreList'].pageDown()
		self.showInfos()

	def keyUp(self):
		if self.keyLocked:
			return
		self['genreList'].up()
		self.showInfos()

	def keyDown(self):
		if self.keyLocked:
			return
		self['genreList'].down()
		self.showInfos()

	def keyPageDown(self):
		print "PageDown"
		if self.keyLocked:
			return
		if not self.page < 1:
			self.page -= 1
			self.loadPage()

	def keyPageUp(self):
		print "PageUP"
		if self.keyLocked:
			return
		self.page += 1
		self.loadPage()

	def keyOK(self):
		bildName = self['genreList'].getCurrent()[0][0]
		bildLink = self['genreList'].getCurrent()[0][1]
		self.bildLink = "http://www.bild.de" + bildLink
		self.bildName = bildName
		data = urllib.urlopen(self.bildLink).read()
		xmllink = re.findall('longdesc="(.*?)"', data, re.S)
		if xmllink:
			getxml = "http://www.bild.de" + xmllink[0]
			data2 = urllib.urlopen(getxml).read()
			streamlink = re.findall('<video.*?src="(.*?)" ', data2, re.S)
			if streamlink:
				self.session.open(SimplePlayer, [(self.bildName, streamlink[0])], showPlaylist=False, ltype='bildde')

	def keyCancel(self):
		self.close()