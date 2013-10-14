# -*- coding: utf-8 -*-
from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.simpleplayer import SimplePlayer
from Plugins.Extensions.MediaPortal.resources.playrtmpmovie import PlayRtmpMovie
from Plugins.Extensions.MediaPortal.resources.coverhelper import CoverHelper

def dreisatEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 20, 0, 860, 25, 0, RT_HALIGN_CENTER | RT_VALIGN_CENTER, entry[0])
		]

def dreisatEntry1(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 20, 0, 860, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry[0])
		]

class dreisatFirstScreen(Screen):

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

		self['title'] = Label("3sat Mediathek")
		self['ContentTitle'] = Label("Genre:")
		self['name'] = Label("Auswahl:")
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
		url = "http://www.3sat.de/mediathek/"
		getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.parseData).addErrback(self.dataError)

	def parseData(self, data):
		raw = re.findall('<li class="SubMenu.*?href="(.*?)red=(.*?)">(.*?)</a></li>', data, re.S)
		if raw:
			self.filmliste = []
			for (dump, Url, Title) in raw:
				self.filmliste.append((decodeHtml(Title), Url, dump))
			self.chooseMenuList.setList(map(dreisatEntry, self.filmliste))
			self.keyLocked = False

	def dataError(self, error):
		printl(error,self,"E")

	def keyOK(self):
		Name = self['genreList'].getCurrent()[0][0]
		Link = self['genreList'].getCurrent()[0][1]
		bildLink = "http://www.bild.de" + Link
		self.session.open(dreisatSecondScreen, Link, Name)

	def keyCancel(self):
		self.close()

class dreisatSecondScreen(Screen):

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

		self['title'] = Label("3sat Mediathek")
		self['ContentTitle'] = Label("Genre: %s" % self.Name)
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
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['liste'] = self.chooseMenuList
		self.page = 0
		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		url = "http://www.3sat.de/mediathek/?mode=verpasst" + str(self.page) + "&red=" + self.Link
		getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.parseData).addErrback(self.dataError)

	def parseData(self, data):
		raw = re.findall('BoxPicture.*?src="(.*?)".*?BoxHeadline.*?href="(.*?)">(.*?)<.*?FloatText.*?href=".*?">(.*?)</a>', data, re.S)
		if raw:
			self.filmliste = []
			for (Image, Link, Title, Handlung) in raw:
				self.filmliste.append((decodeHtml(Title), Link, Image, Handlung))
			self.chooseMenuList.setList(map(dreisatEntry1, self.filmliste))
			self.keyLocked = False
			self.showInfos()

	def dataError(self, error):
		printl(error,self,"E")

	def showInfos(self):
		coverUrl = self['liste'].getCurrent()[0][2]
		handlung = self['liste'].getCurrent()[0][3]
		self['handlung'].setText(decodeHtml(handlung))
		self.ImageUrl = "http://www.3sat.de%s" % coverUrl
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
		self.title = self['liste'].getCurrent()[0][0]
		link = self['liste'].getCurrent()[0][1].replace('&amp;','&')

		(dump, id) = link.split('obj=')
		url = "http://www.3sat.de/mediathek/xmlservice/web/beitragsDetails?ak=web&id=%s" % id
		print url
		getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.getDataStream).addErrback(self.dataError)

	def getDataStream(self, data):
		urls = re.findall('<url>(.*?zdf.de.*?\.mp4)</url>', data) # mp4
		urls = re.findall('<quality>(.*?)</quality.*?<url>(.*?zdf.de.*?\.smil)</url>', data, re.S)
		print urls
		if urls:
			getPage(urls[-1][1], headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.getStream).addErrback(self.dataError)

	def getStream(self, data):
		print data
		host = re.findall('<param name="host" value="(.*?)" />', data)
		if host:
			print host
			playpath = re.findall('<video dur=".*?" paramGroup=".*?" src="(.*?)" system-bitrate=".*?">', data, re.S)
			if playpath:
				print playpath
				if config.mediaportal.useRtmpDump.value:
					final = "rtmp://%s/ondemand/' --playpath=%s'" % (host[0], playpath[-1])
					print final
					movieinfo = [final,self.title]
					self.session.open(PlayRtmpMovie, movieinfo, self.title)
				else:
					final = "rtmp://%s/ondemand/ playpath=%s" % (host[0], playpath[-1])
					print final
					self.session.open(SimplePlayer, [(self.title, final, self.ImageUrl)], showPlaylist=False, ltype='3sat')

	def keyCancel(self):
		self.close()