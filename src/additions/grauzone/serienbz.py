# -*- coding: utf-8 -*-
from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.simpleplayer import SimplePlayer
from Plugins.Extensions.MediaPortal.resources.coverhelper import CoverHelper

def SerienEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 20, 0, 860, 25, 0, RT_HALIGN_CENTER | RT_VALIGN_CENTER, entry[0])
		]

def SerienListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 20, 0, 860, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry[0])
		]


class SerienFirstScreen(Screen):

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

		self['title'] = Label("Serien.bz")
		self['ContentTitle'] = Label("Genre:")
		self['name'] = Label("v0.1-beta")
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
		url = "http://serien.bz"
		getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.parseData).addErrback(self.dataError)

	def parseData(self, data):
		raw = re.findall('<a class="LetterMode " href="(.*?)">(.*?)<', data, re.S)
		if raw:
			self.filmliste = []
			for (serienUrl, serienTitle) in raw:
				self.filmliste.append((decodeHtml(serienTitle), serienUrl))
			self.chooseMenuList.setList(map(SerienEntry, self.filmliste))
			self.keyLocked = False

	def dataError(self, error):
		printl(error,self,"E")
		
	def keyOK(self):
		serienName = self['genreList'].getCurrent()[0][0]
		serienLink = self['genreList'].getCurrent()[0][1]
		self.session.open(SerienSecondScreen, serienLink, serienName)

	def keyCancel(self):
		self.close()
		
class SerienSecondScreen(Screen):

	def __init__(self, session, serienLink, serienName):
		self.session = session
		self.serienLink = serienLink
		self.serienName = serienName

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
		"left" : self.keyLeft
		}, -1)

		self['title'] = Label("Serien.bz")
		self['ContentTitle'] = Label("Auswahl: %s" % self.serienName)
		self['name'] = Label("")
		self['F1'] = Label("Exit")
		self['F2'] = Label("")
		self['F3'] = Label("")
		self['F4'] = Label("")
		self['F2'].hide()
		self['F3'].hide()
		self['F4'].hide()
		self['coverArt'] = Pixmap()
		self['Page'] = Label("")
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
		url = self.serienLink
		getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.parseData).addErrback(self.dataError)

	def parseData(self, data):
		raw = re.findall('<li><a href="(.*?)">(.*?)</a>', data, re.S)
		if raw:
			self.filmliste = []
			for (serienUrl, serienTitle) in raw:
				self.filmliste.append((decodeHtml(serienTitle), serienUrl))
			self.chooseMenuList.setList(map(SerienListEntry, self.filmliste))
			self.keyLocked = False
			self.loadInfos()

	def dataError(self, error):
		printl(error,self,"E")

	def loadInfos(self):
		serienUrl = self['liste'].getCurrent()[0][1]
		getPage(serienUrl, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.showInfos).addErrback(self.dataError)

	def showInfos(self, data):
		serienTitle = self['liste'].getCurrent()[0][0]
		if re.match('.*?Sorry, but there.*?category yet.</h2>', data, re.S):
			self['handlung'].setText("Kein Stream vorhanden!")
			self['name'].setText("Kein Stream vorhanden!")
		else:
			self['name'].setText(decodeHtml(serienTitle))
			sbzdescription = re.findall('<div class="entry">.*?<p.*?</p>.*?<p.*?</p>.*?<p style="text-align: left;">(.*?)</p>', data, re.S)
			if sbzdescription:
				self['handlung'].setText(decodeHtml(sbzdescription[0]))
			else:
				self['handlung'].setText("Keine Infos gefunden.")
		sbzCover = re.findall('<div class="entry">.*?<p.*?src="(.*?)".*?</p>.*?<p.*?</p>.*?<p.*?</p>', data, re.S)
		if sbzCover:
			self.ImageUrl = "http://serien.bz%s" % sbzCover[0]
			CoverHelper(self['coverArt']).getCover(self.ImageUrl)
		else:
			self.ImageUrl = ""

	def keyLeft(self):
		if self.keyLocked:
			return
		self['liste'].pageUp()
		self.loadInfos()

	def keyRight(self):
		if self.keyLocked:
			return
		self['liste'].pageDown()
		self.loadInfos()

	def keyUp(self):
		if self.keyLocked:
			return
		self['liste'].up()
		self.loadInfos()

	def keyDown(self):
		if self.keyLocked:
			return
		self['liste'].down()
		self.loadInfos()

	def keyOK(self):
		serienName = self['liste'].getCurrent()[0][0]
		serienLink = self['liste'].getCurrent()[0][1]
		
		print serienName, serienLink
		
		self.session.open(SerienEpListingScreen, serienLink, serienName, self.ImageUrl)

	def keyCancel(self):
		self.close()

class SerienEpListingScreen(Screen):

	def __init__(self, session, serienLink, serienName, serienPic):
		self.session = session
		self.serienLink = serienLink
		self.serienName = serienName
		self.serienPic = serienPic

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
		"cancel": self.keyCancel
		}, -1)

		self['title'] = Label("Serien.bz")
		self['ContentTitle'] = Label("Serie: %s" % self.serienName)
		self['name'] = Label("")
		self['F1'] = Label("Exit")
		self['F2'] = Label("")
		self['F3'] = Label("")
		self['F4'] = Label("")
		self['F2'].hide()
		self['F3'].hide()
		self['F4'].hide()
		self['coverArt'] = Pixmap()
		self['Page'] = Label("")
		self['page'] = Label("")
		self['handlung'] = Label("")

		self.keyLocked = True
		self.filmliste = []
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['liste'] = self.chooseMenuList
		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		url = self.serienLink
		CoverHelper(self['coverArt']).getCover(self.serienPic)
		print url
		getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.parseData).addErrback(self.dataError)

	def parseData(self, data):
		streams_raw = re.findall('>Staffel:.(.*?)</th>(.*?)</table>', data, re.S)
		if streams_raw:
			self.filmliste = []
			for staffel,ep_raw in streams_raw:
				ep_raw2 = re.findall('<strong>Episode.(.*?)</strong>(.*?</p>)', ep_raw,)
				if ep_raw2:
					for episode,ep_rawData in ep_raw2:
						streams = re.findall('<strong>Stream:</strong> <a href="(.*?)".*?\| (.*?)<', ep_rawData, re.S)
						if streams:
							if int(staffel) < 10:
								s = "S0%s" % str(staffel)
							else:
								s = "S%s" % str(staffel)
								
							if int(episode) < 10:
								e = "E0%s" % str(episode)
							else:
								e = "E%s" % str(episode)
								
							title = "%s%s" % (s, e)
							
							self.filmliste.append((title, streams))
					self.chooseMenuList.setList(map(SerienListEntry, self.filmliste))
					self.keyLocked = False

	def dataError(self, error):
		printl(error,self,"E")

	def keyOK(self):
		serienName = self['liste'].getCurrent()[0][0]
		serienLink = self['liste'].getCurrent()[0][1]
		
		print serienName, serienLink
		
		self.session.open(SerienStreamListingScreen, serienLink, serienName, self.serienPic)

	def keyCancel(self):
		self.close()

class SerienStreamListingScreen(Screen):

	def __init__(self, session, serienLink, serienName, serienPic):
		self.session = session
		self.serienLink = serienLink
		self.serienName = serienName
		self.serienPic = serienPic

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
		"cancel": self.keyCancel
		}, -1)

		self['title'] = Label("Serien.bz")
		self['ContentTitle'] = Label("Streams: %s" % self.serienName)
		self['name'] = Label("")
		self['F1'] = Label("Exit")
		self['F2'] = Label("")
		self['F3'] = Label("")
		self['F4'] = Label("")
		self['F2'].hide()
		self['F3'].hide()
		self['F4'].hide()
		self['coverArt'] = Pixmap()
		self['Page'] = Label("")
		self['page'] = Label("")
		self['handlung'] = Label("")

		self.keyLocked = True
		self.filmliste = []
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['liste'] = self.chooseMenuList
		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		CoverHelper(self['coverArt']).getCover(self.serienPic)
		for hoster,hostrname in self.serienLink:
			self.filmliste.append((hostrname, hoster))
		self.chooseMenuList.setList(map(SerienListEntry, self.filmliste))
		self.keyLocked = False

	def dataError(self, error):
		printl(error,self,"E")

	def keyOK(self):
		hostername = self['liste'].getCurrent()[0][0]
		hoster = self['liste'].getCurrent()[0][1]
		
		print hostername, hoster
		get_stream_link(self.session).check_link(hoster, self.playfile)

	def playfile(self, stream_url):
		if stream_url != None:
			self.session.open(SimplePlayer, [(self.serienName, stream_url, self.serienPic)], showPlaylist=False, ltype='serien.bz', cover=True)

	def keyCancel(self):
		self.close()