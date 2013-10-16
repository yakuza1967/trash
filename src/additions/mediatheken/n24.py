# -*- coding: utf-8 -*-
from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.simpleplayer import SimplePlayer
from Plugins.Extensions.MediaPortal.resources.coverhelper import CoverHelper

def n24Entry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 20, 0, 860, 25, 0, RT_HALIGN_CENTER | RT_VALIGN_CENTER, entry[0])
		]

def n24Entry1(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 20, 0, 860, 25, 0, RT_HALIGN_LEFT| RT_VALIGN_CENTER, entry[0])
		]

class n24GenreScreen(Screen):

	def __init__(self, session):
		self.session = session
		path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/%s/defaultGenreScreen.xml" % config.mediaportal.skin.value
		if not fileExists(path):
			path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/original/defaultGenreScreen.xml"
		print path
		with open(path, "r") as f:
			self.skin = f.read()
			f.close()

		Screen.__init__(self, session)

		self["actions"]  = ActionMap(["OkCancelActions", "ShortcutActions", "WizardActions", "ColorActions", "SetupActions", "NumberActions", "MenuActions"], {
			"ok"	: self.keyOK,
			"cancel": self.keyCancel
		}, -1)

		self['title'] = Label("N24 Mediathek")
		self['ContentTitle'] = Label("Genre:")
		self['name'] = Label("Auswahl:")
		self['F1'] = Label("Exit")
		self['F2'] = Label("")
		self['F3'] = Label("")
		self['F4'] = Label("")
		self['F2'].hide()
		self['F3'].hide()
		self['F4'].hide()

		self.keyLocked = True
		self.filmliste = []

		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['genreList'] = self.chooseMenuList

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.keyLocked = True
		self.filmliste = []
		url = "http://www.n24.de/n24/Mediathek/videos/"
		getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.parseData).addErrback(self.dataError)

	def parseData(self, data):
		raw = re.findall('<li><a.*?data-filter_rubric="(.*?)">(.*?)</a></li>', data, re.S)
		if raw:
			for (Url, Title) in raw:
				self.filmliste.append((decodeHtml(Title), Url))
				self.chooseMenuList.setList(map(n24Entry, self.filmliste))
			self.keyLocked = False

	def dataError(self, error):
		printl(error,self,"E")

	def keyOK(self):
		if self.keyLocked:
			return
		Name = self['genreList'].getCurrent()[0][0]
		Link = self['genreList'].getCurrent()[0][1].replace(' ','+')
		self.session.open(n24ListScreen, Link, Name)

	def keyCancel(self):
		self.close()

class n24ListScreen(Screen):

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

		self['title'] = Label("N24 Mediathek")
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
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['liste'] = self.chooseMenuList
		self.page = 1
		self.lastpage = 1
		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.keyLocked = True
		self.filmliste = []
		url = "http://www.n24.de/n24/Mediathek/videos/q?query=&hitsPerPage=50&pageNum=" + str(self.page) + "&recent=0&docType=CMVideo&category=" + self.Link + "&from=&to=&taxonomy=&type=&sort=new"
		getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.parseData).addErrback(self.dataError)

	def parseData(self, data):
		lastpage = re.search('<li><span\sclass="pages">.*?\s/\s(.*?)</span></li>', data, re.S)
		if lastpage:
			self.lastpage = int(lastpage.group(1))
			self['page'].setText("%s / %s" % (str(self.page), str(self.lastpage)))
		else:
			self.lastpage = 1
			self['page'].setText("%s / 1" % str(self.page))

		raw = re.findall('<div class="result_media">.*?href="(.*?)".*?class="image">.*?src=&#034;(.*?)&#034;.*?<h4>.*?href.*?>(.*?)</a>', data, re.S)
		if raw:
			for (Link, Image, Title) in raw:
				Title = Title.strip()
				self.filmliste.append((decodeHtml(Title), Link, Image))
			self.chooseMenuList.setList(map(n24Entry1, self.filmliste))
			self.chooseMenuList.moveToIndex(0)
		self.keyLocked = False
		self.showInfos()

	def dataError(self, error):
		printl(error,self,"E")

	def showInfos(self):
		coverUrl = self['liste'].getCurrent()[0][2]
		CoverHelper(self['coverArt']).getCover(coverUrl)
		link = "http://www.n24.de" + self['liste'].getCurrent()[0][1]
		getPage(link, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.getHandlung).addErrback(self.dataError)

	def getHandlung(self, data):
		handlung = re.search('<div\sclass="text">.*?<p>(.*?)</p>.*?<div\sclass="related">', data, re.S)
		if handlung:
			self['handlung'].setText(decodeHtml(handlung.group(1).strip()))
		else:
			self['handlung'].setText("Keine Infos gefunden.")

	def keyPageDown(self):
		print "PageDown"
		if self.keyLocked:
			return
		if not self.page < 2:
			self.page -= 1
			self.loadPage()

	def keyPageUp(self):
		print "PageUP"
		if self.keyLocked:
			return
		if self.page < self.lastpage:
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
		Link = "http://www.n24.de" + self['liste'].getCurrent()[0][1]
		getPage(Link, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.getStreamData).addErrback(self.dataError)

	def getStreamData(self, data):
		self.title = self['liste'].getCurrent()[0][0]
		host = re.search('videoFlashconnectionUrl\s=\s["|\'](.*?)["|\'];', data, re.S)
		playpath = re.search('videoFlashSource\s=\s["|\'](.*?)["|\'];', data, re.S)
		final = "%s playpath=%s" % (host.group(1), playpath.group(1))
		self.session.open(SimplePlayer, [(self.title, final)], showPlaylist=False, ltype='n24')

	def keyCancel(self):
		self.close()