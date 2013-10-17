	# -*- coding: utf-8 -*-
from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.simpleplayer import SimplePlayer
from Plugins.Extensions.MediaPortal.resources.playrtmpmovie import PlayRtmpMovie
from Plugins.Extensions.MediaPortal.resources.coverhelper import CoverHelper

def wissensthekGenreEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 20, 0, 860, 25, 0, RT_HALIGN_CENTER | RT_VALIGN_CENTER, entry[0])
		]

def wissensthekEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 20, 0, 860, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry[0])
		]

class wissensthekGenreScreen(Screen):

	def __init__(self, session):
		self.session = session
		self.plugin_path = mp_globals.pluginPath
		self.skin_path =  mp_globals.pluginPath + "/skins"

		path = "%s/%s/defaultGenreScreen.xml" % (self.skin_path, config.mediaportal.skin.value)
		if not fileExists(path):
			path = self.skin_path + "/original/defaultGenreScreen.xml"

		with open(path, "r") as f:
			self.skin = f.read()
			f.close()

		Screen.__init__(self, session)

		self["actions"]  = ActionMap(["OkCancelActions", "ShortcutActions", "WizardActions", "ColorActions", "SetupActions", "NumberActions", "MenuActions"], {
			"ok"	: self.keyOK,
			"cancel": self.keyCancel
		}, -1)

		self['title'] = Label("Welt der Wunder - Wissensthek")
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
		url = "http://www.wissensthek.de/"
		getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.parseData).addErrback(self.dataError)

	def parseData(self, data):
		raw = re.findall('<li>.*?id="menu.*?href="(.*?)".*?>(.*?)<', data, re.S)
		if raw:
			for (Url, Title) in raw:
				self.filmliste.append((decodeHtml(Title), Url))
			if config.mediaportal.useRtmpDump.value:
				self.filmliste.sort()
				self.filmliste.insert(0, ("Live TV", "DUMP", None))
			self.chooseMenuList.setList(map(wissensthekGenreEntry, self.filmliste))
			self.chooseMenuList.moveToIndex(0)
			self.keyLocked = False

	def dataError(self, error):
		printl(error,self,"E")

	def LiveStream(self, data):
		raw = re.findall('class="pionteve_title">(.*?)</td>.*?</span>(.*?)</i>.*?<i>(.*?)</i>', data, re.S)
		if raw:
			title = raw[1][0] + raw[1][1] + raw[1][2]
		else:
			title = "Live TV"
		host = "rtmp://mf.weltderwunder.c.nmdn.net:1935/wdw_pc"
		playpath = "wdwpc.sdp"
		final = "%s' --playpath=%s'" % (host, playpath)
		movieinfo = [final,title]
		self.session.open(PlayRtmpMovie, movieinfo, title)
		
	def keyOK(self):
		if self.keyLocked:
			return
		if self['genreList'].getCurrent()[0][0] == "Live TV":
			url = "http://www.weltderwunder.tv/index.php?id=133"
			getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.LiveStream).addErrback(self.dataError)
		else:
			Name = self['genreList'].getCurrent()[0][0]
			Link = "http://www.wissensthek.de/" + self['genreList'].getCurrent()[0][1]
			self.session.open(wissensthekListScreen, Link, Name)



	def keyCancel(self):
		self.close()

class wissensthekListScreen(Screen):

	def __init__(self, session, Link, Name):
		self.session = session
		self.Link = Link
		self.Name = Name
		self.plugin_path = mp_globals.pluginPath
		self.skin_path =  mp_globals.pluginPath + "/skins"

		path = "%s/%s/defaultListScreen.xml" % (self.skin_path, config.mediaportal.skin.value)
		if not fileExists(path):
			path = self.skin_path + "/original/defaultListScreen.xml"

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

		self['title'] = Label("Welt der Wunder - Wissensthek")
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
		url = self.Link + "?tx_kaltura_pi1[pag]=" + str(self.page)
		getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.parseData).addErrback(self.dataError)

	def parseData(self, data):
		lastpage = re.search('target="_self"\s.*target=\'_self\'>(.*?)</a></li>', data, re.S)
		if self.lastpage:
			self.lastpage = int(lastpage.group(1))
			self['page'].setText("%s / %s" % (str(self.page), str(self.lastpage)))

		raw = re.findall('description-box".*?href="(.*?)%5Bclipid%5D=(.*?)&amp;cHash=(.*?)".*?src="(.*?)".*?time-video">(.*?)<.*?<h5>.*?class="test">(.*?)</a>.*?<span>(.*?)</span>.*?<p>(.*?)</p>   ', data, re.S)
		if raw:
			for (Player, ClipId, Hash, Image, Time, Title, Added, Handlung) in raw:
				self.filmliste.append((decodeHtml(Title), Player, ClipId, Hash, Image, Time, Title, Added, Handlung))
			self.chooseMenuList.setList(map(wissensthekEntry, self.filmliste))
			self.chooseMenuList.moveToIndex(0)
		self.keyLocked = False
		self.showInfos()

	def dataError(self, error):
		printl(error,self,"E")

	def showInfos(self):
		coverUrl = self['liste'].getCurrent()[0][4]
		handlung = self['liste'].getCurrent()[0][8]
		self['handlung'].setText(decodeHtml(handlung))
		CoverHelper(self['coverArt']).getCover(coverUrl)

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
		title = self['liste'].getCurrent()[0][0]
		ClipId = self['liste'].getCurrent()[0][2]
		url = "http://medianac.nacamar.de/p/249/sp/24900/raw/entry_id/%s" % ClipId + "/version/0"
		if url:
			playlist = []
			playlist.append((title, url))
			self.session.open(SimplePlayer, playlist, showPlaylist=False, ltype='wissensthek')

	def keyCancel(self):
		self.close()