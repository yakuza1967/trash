# -*- coding: utf-8 -*-
from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.simpleplayer import SimplePlayer
from Plugins.Extensions.MediaPortal.resources.coverhelper import CoverHelper
from Plugins.Extensions.MediaPortal.resources.twagenthelper import TwAgentHelper

def arteEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 20, 0, 860, 25, 0, RT_HALIGN_CENTER | RT_VALIGN_CENTER, entry[0])
		]

def arteEntry1(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 20, 0, 860, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry[0])
		]

class arteFirstScreen(Screen):

	def __init__(self, session):
		self.session = session
		path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/%s/defaultGenreScreen.xml" % config.mediaportal.skin.value
		if not fileExists(path):
			path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/defaultGenreScreen.xml"
		print path
		with open(path, "r") as f:
			self.skin = f.read()
			f.close()

		Screen.__init__(self, session)

		self["actions"]  = ActionMap(["OkCancelActions", "ShortcutActions", "WizardActions", "ColorActions", "SetupActions", "NumberActions", "MenuActions"], {
			"ok"	: self.keyOK,
			"cancel": self.keyCancel
		}, -1)

		self['title'] = Label("Arte Mediathek")
		self['ContentTitle'] = Label("Genre:")
		self['name'] = Label("v0.1")
		self['F1'] = Label("Exit")
		self['F2'] = Label("")
		self['F3'] = Label("")
		self['F4'] = Label("")
		self['F2'].hide()
		self['F3'].hide()
		self['F4'].hide()
		self['coverArt'] = Pixmap()
		self.keyLocked = True
		self.filmliste = []
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['genreList'] = self.chooseMenuList

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		url = "http://videos.arte.tv/de/videos/sendungen"
		getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.parseData).addErrback(self.dataError)

	def parseData(self, data):
		sendungen = re.findall('<li><a href="(.*?)">(.*?)<span id="(.*?)"></span></a></li>', data)
		if sendungen:
			self.filmliste = []
			for link,title,id in sendungen:
				print title,link,id
				link = "http://videos.arte.tv%s" % link
				self.filmliste.append((decodeHtml(title), link))
			self.chooseMenuList.setList(map(arteEntry, self.filmliste))
			self.keyLocked = False

	def dataError(self, error):
		printl(error,self,"E")

	def keyOK(self):
		if self.keyLocked:
			return

		Name = self['genreList'].getCurrent()[0][0]
		Link = self['genreList'].getCurrent()[0][1]
		self.session.open(arteSecondScreen, Link, Name)

	def keyCancel(self):
		self.close()

class arteSecondScreen(Screen):

	def __init__(self, session, Link, Name):
		self.session = session
		self.Link = Link
		self.Name = Name

		path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/%s/defaultListScreen.xml" % config.mediaportal.skin.value
		if not fileExists(path):
			path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/original/defaultListScreen.xml"
		print path
		with open(path, "r") as f:
			self.skin = f.read()
			f.close()

		Screen.__init__(self, session)

		self["actions"] = ActionMap(["OkCancelActions", "ShortcutActions", "WizardActions", "ColorActions", "SetupActions", "NumberActions", "MenuActions", "EPGSelectActions"], {
		"ok"	: self.keyOK,
		"cancel": self.keyCancel,
		"up" : self.keyUp,
		"down" : self.keyDown,
		"right" : self.keyRight,
		"left" : self.keyLeft,
		"nextBouquet" : self.keyPageUp,
		"prevBouquet" : self.keyPageDown
		}, -1)

		self['title'] = Label("Arte Mediathek")
		self['ContentTitle'] = Label("Auswahl: %s" % self.Name)
		self['name'] = Label("")
		self['F1'] = Label("Exit")
		self['F2'] = Label("")
		self['F3'] = Label("")
		self['F4'] = Label("")
		self['F2'].hide()
		self['F3'].hide()
		self['F4'].hide()
		self['coverArt'] = Pixmap()
		self['Page'] = Label("Page: ")
		self['page'] = Label("")
		self['handlung'] = Label("")

		self.keyLocked = True
		self.filmliste = []
		self.tw_agent_hlp = TwAgentHelper()
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['liste'] = self.chooseMenuList
		self.page = 0
		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		getPage(self.Link, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.parseData).addErrback(self.dataError)

	def parseData(self, data):
		videos = re.findall('<div class="video">.*?<a href="(.*?)"><img alt=.*?" class=.*?" width=.*?" height=.*?" src="(.*?)".*?<p class="teaserText">(.*?)</p>.*?<h2><a href=".*?">(.*?)</a></h2>.*?<p>(.*?)</p>', data, re.S)
		if videos:
			self.filmliste = []
			for (link, image, handlung, title, datum) in videos:
				title = "%s - %s" % (datum ,decodeHtml(title))
				link = "http://videos.arte.tv%s" % link
				image = "http://videos.arte.tv%s" % image
				self.filmliste.append((title, link, image, handlung))
			self.chooseMenuList.setList(map(arteEntry1, self.filmliste))
			self.keyLocked = False
			self.showInfos()

	def dataError(self, error):
		printl(error,self,"E")

	def showInfos(self):
		self.ImageUrl = self['liste'].getCurrent()[0][2]
		handlung = self['liste'].getCurrent()[0][3]
		self['handlung'].setText(decodeHtml(handlung))
		CoverHelper(self['coverArt']).getCover(self.ImageUrl)

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

	def keyLeft(self):
		if self.keyLocked:
			return
		self['liste'].pageUp()
		self.showInfos()

	def keyRight(self):
		if self.keyLocked:
			return
		self['liste'].pageDown()
		self.showInfos()

	def keyUp(self):
		if self.keyLocked:
			return
		self['liste'].up()
		self.showInfos()

	def keyDown(self):
		if self.keyLocked:
			return
		self['liste'].down()
		self.showInfos()

	def keyOK(self):
		if self.keyLocked:
			return

		self.title = self['liste'].getCurrent()[0][0]
		link = self['liste'].getCurrent()[0][1].replace('&amp;','&')

		print self.title, link
		api_url = "http://www.arte.tv/player/v2//index.php?json_url=http://arte.tv/papi/tvguide/videos/stream/player/D/049880-014_PLUS7-D/ALL/ALL.json&lang=de_DE&config=arte_tvguide&rendering_place=" + str(link)
		print api_url
		getPage(api_url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.getDataStream).addErrback(self.dataError)

	def getDataStream(self, data):
		guide_url = '<link rel="alternate" hreflang="de" href="(.*?)" />'
		if guide_url:
			print guide_url
			getPage(guide_url[0], headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.getStream).addErrback(self.dataError)

	def getDataStream(self, data):
		stream_url = re.findall('<meta name="twitter:player:stream" content="(.*?)">', data)
		if stream_url:
			self.tw_agent_hlp.getRedirectedUrl(self.playStream, self.dataError, stream_url[0])

	def playStream(self, url):
		print url
		self.session.open(SimplePlayer, [(self.title, url, self.ImageUrl)], showPlaylist=False, ltype='Arte', cover=True)

	def keyCancel(self):
		self.close()