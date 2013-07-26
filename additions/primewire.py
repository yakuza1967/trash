from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.simpleplayer import SimplePlayer

def chListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 20, 0, 860, 25, 0, RT_HALIGN_LEFT, entry[0])
		]

def chStreamListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 20, 0, 860, 25, 0, RT_HALIGN_CENTER, entry[0])
		]

def chGenreListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 20, 0, 860, 25, 0, RT_HALIGN_CENTER, entry[0])
		]

class PrimeWireGenreScreen(Screen):

	def __init__(self, session):
		self.session = session
		path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/%s/PrimeWireGenreScreen.xml" % config.mediaportal.skin.value
		if not fileExists(path):
			path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/original/PrimeWireGenreScreen.xml"
		print path
		with open(path, "r") as f:
			self.skin = f.read()
			f.close()

		Screen.__init__(self, session)

		self["actions"]  = ActionMap(["OkCancelActions", "ShortcutActions", "EPGSelectActions", "WizardActions", "ColorActions", "NumberActions", "MenuActions", "MoviePlayerActions", "InfobarSeekActions"], {
			"ok"    : self.keyOK,
			"cancel": self.keyCancel
		}, -1)

		self['title'] = Label("PrimeWire.ag")
		self['leftContentTitle'] = Label("Genres")
		self['stationIcon'] = Pixmap()
		self.keyLocked = True

		self.genreliste = []
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 24))
		self.chooseMenuList.l.setItemHeight(25)
		self['streamlist'] = self.chooseMenuList

		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.keyLocked = True
		url = "http://www.primewire.ag/"
		getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.genreData).addErrback(self.dataError)

	def genreData(self, data):
		parse = re.search('class="opener-menu-genre">(.*)class="opener-menu-section', data, re.S)
		phCats = re.findall('<a\shref="(.*?)">(.*?)</a>', parse.group(1), re.S)
		if phCats:
			for (phUrl, phTitle) in phCats:
				phUrl = "http://www.primewire.ag" + phUrl + "&page="
				self.genreliste.append((phTitle, phUrl))
			self.genreliste.sort()
			self.genreliste.insert(0, ("TV Shows", "http://www.primewire.ag/?tv=&sort=views&page="))
			self.chooseMenuList.setList(map(chGenreListEntry, self.genreliste))
			self.chooseMenuList.moveToIndex(0)
			self.keyLocked = False

	def dataError(self, error):
		printl(error,self,"E")

	def keyOK(self):
		exist = self['streamlist'].getCurrent()
		if self.keyLocked or exist == None:
			return
		auswahl = self['streamlist'].getCurrent()[0][0]
		url = self['streamlist'].getCurrent()[0][1]
		self.session.open(PrimeWireFilmlisteScreen, url, auswahl)

	def keyCancel(self):
		self.close()

class PrimeWireFilmlisteScreen(Screen):

	def __init__(self, session, chGotLink, Genre):
		self.chGotLink = chGotLink
		self.Genre = Genre
		self.session = session
		path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/%s/PrimeWireFilmlisteScreen.xml" % config.mediaportal.skin.value
		if not fileExists(path):
			path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/original/PrimeWireFilmlisteScreen.xml"
		print path
		with open(path, "r") as f:
			self.skin = f.read()
			f.close()

		Screen.__init__(self, session)

		self["actions"]  = ActionMap(["OkCancelActions", "ShortcutActions", "EPGSelectActions", "WizardActions", "ColorActions", "NumberActions", "MenuActions", "MoviePlayerActions", "InfobarSeekActions"], {
			"ok"    : self.keyOK,
			"cancel": self.keyCancel,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft,
			"nextBouquet" : self.keyPageUp,
			"prevBouquet" : self.keyPageDown
		}, -1)

		self['title'] = Label("PrimeWire.ag")
		self['leftContentTitle'] = Label(self.Genre)
		self['stationIcon'] = Pixmap()

		self.streamList = []
		self.streamMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.streamMenuList.l.setFont(0, gFont('mediaportal', 24))
		self.streamMenuList.l.setItemHeight(25)
		self['streamlist'] = self.streamMenuList

		self.keyLocked = True
		self.page = 1
		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.streamList = []
		url = "%s%s" % (self.chGotLink, str(self.page))
		getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.parseData).addErrback(self.dataError)

	def parseData(self, data):
		chMovies = re.findall('<div\sclass="index_item\sindex_item_ie">.*?<a\shref="(.*?)"\stitle="Watch.(.*?)"><img\ssrc="(.*?)"', data, re.S)
		if chMovies:
			for (chUrl,chTitle,chImage) in chMovies:
				chUrl = "http://www.primewire.ag" + chUrl
				self.streamList.append((decodeHtml(chTitle),chUrl,chImage))
				self.streamMenuList.setList(map(chListEntry, self.streamList))
			self.keyLocked = False
			self.showInfos()

	def showInfos(self):
		coverUrl = self['streamlist'].getCurrent()[0][2]
		if coverUrl:
			downloadPage(coverUrl, "/tmp/chIcon.jpg").addCallback(self.showCover)

	def showCover(self, picData):
		if fileExists("/tmp/chIcon.jpg"):
			self['stationIcon'].instance.setPixmap(gPixmapPtr())
			self.scale = AVSwitch().getFramebufferScale()
			self.picload = ePicLoad()
			size = self['stationIcon'].instance.size()
			self.picload.setPara((size.width(), size.height(), self.scale[0], self.scale[1], False, 1, "#FF000000"))
			if self.picload.startDecode("/tmp/chIcon.jpg", 0, 0, False) == 0:
				ptr = self.picload.getData()
				if ptr != None:
					self['stationIcon'].instance.setPixmap(ptr)
					self['stationIcon'].show()
					del self.picload

	def dataError(self, error):
		printl(error,self,"E")

	def keyOK(self):
		exist = self['streamlist'].getCurrent()
		if self.keyLocked or exist == None:
			return
		titel = self['streamlist'].getCurrent()[0][0]
		auswahl = self['streamlist'].getCurrent()[0][1]
		if self.Genre == "TV Shows":
			self.session.open(PrimeWireEpisodeScreen, auswahl)
		else:
			self.session.open(PrimeWireStreamsScreen, auswahl, titel)

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
		self.page += 1
		self.loadPage()

	def keyLeft(self):
		if self.keyLocked:
			return
		self['streamlist'].pageUp()
		self.showInfos()

	def keyRight(self):
		if self.keyLocked:
			return
		self['streamlist'].pageDown()
		self.showInfos()

	def keyUp(self):
		if self.keyLocked:
			return
		self['streamlist'].up()
		self.showInfos()

	def keyDown(self):
		if self.keyLocked:
			return
		self['streamlist'].down()
		self.showInfos()

	def keyCancel(self):
		self.close()

class PrimeWireEpisodeScreen(Screen):

	def __init__(self, session, chGotLink):
		self.chGotLink = chGotLink
		self.session = session
		path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/%s/PrimeWireStreamsScreen.xml" % config.mediaportal.skin.value
		if not fileExists(path):
			path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/original/PrimeWireStreamsScreen.xml"
		print path
		with open(path, "r") as f:
			self.skin = f.read()
			f.close()

		Screen.__init__(self, session)

		self["actions"]  = ActionMap(["OkCancelActions", "ShortcutActions", "EPGSelectActions", "WizardActions", "ColorActions", "NumberActions", "MenuActions", "MoviePlayerActions", "InfobarSeekActions"], {
			"ok"    : self.keyOK,
			"cancel": self.keyCancel,
		}, -1)

		self['title'] = Label("PrimeWire.ag")
		self['leftContentTitle'] = Label("Episoden")
		self['stationIcon'] = Pixmap()
		self['handlung'] = Label("")

		self.streamList = []
		self.streamMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.streamMenuList.l.setFont(0, gFont('mediaportal', 24))
		self.streamMenuList.l.setItemHeight(25)
		self['streamlist'] = self.streamMenuList

		self.keyLocked = True
		self.page = 1
		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.streamList = []
		url = "%s%s" % (self.chGotLink, str(self.page))
		getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.parseData).addErrback(self.dataError)

	def parseData(self, data):
		episoden = re.findall('class="tv_episode_item.*?">.*?<a\shref="(.*?)">.*?episode_name">\s{0,2}-\s{0,2}(.*?)</span', data, re.S|re.I)
		if episoden:
			for (url,title) in episoden:
				episode = re.findall('season-(.*?)-episode-(.*?)$', url, re.S)
				season_episode_label = "Season %s Episode %s %s" % (episode[0][0], episode[0][1], title)
				self.streamList.append((decodeHtml(season_episode_label),url))
			self.streamMenuList.setList(map(chListEntry, self.streamList))
			self.keyLocked = False
		details = re.findall('<meta\sname="description"\scontent="Watch.(.*?)">.*?<meta\sproperty="og:image"\scontent="(.*?)"/>', data, re.S)
		if details:
			(handlung,image) = details[0]
			self['handlung'].setText(decodeHtml(handlung))
			self.showInfos(image)

	def showInfos(self, coverUrl):
		downloadPage(coverUrl, "/tmp/chIcon.jpg").addCallback(self.showCover)

	def showCover(self, picData):
		if fileExists("/tmp/chIcon.jpg"):
			self['stationIcon'].instance.setPixmap(gPixmapPtr())
			self.scale = AVSwitch().getFramebufferScale()
			self.picload = ePicLoad()
			size = self['stationIcon'].instance.size()
			self.picload.setPara((size.width(), size.height(), self.scale[0], self.scale[1], False, 1, "#FF000000"))
			if self.picload.startDecode("/tmp/chIcon.jpg", 0, 0, False) == 0:
				ptr = self.picload.getData()
				if ptr != None:
					self['stationIcon'].instance.setPixmap(ptr)
					self['stationIcon'].show()
					del self.picload

	def dataError(self, error):
		printl(error,self,"E")

	def keyOK(self):
		exist = self['streamlist'].getCurrent()
		if self.keyLocked or exist == None:
			return
		titel = self['streamlist'].getCurrent()[0][0]
		auswahl = self['streamlist'].getCurrent()[0][1]
		print auswahl
		url = "http://www.primewire.ag" + auswahl
		self.session.open(PrimeWireStreamsScreen, url, titel)

	def keyCancel(self):
		self.close()

class PrimeWireStreamsScreen(Screen):

	def __init__(self, session, movielink, name):
		self.session = session
		self.movielink = movielink
		self.titel = name
		path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/%s/PrimeWireStreamsScreen.xml" % config.mediaportal.skin.value
		if not fileExists(path):
			path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/original/PrimeWireStreamsScreen.xml"
		print path
		with open(path, "r") as f:
			self.skin = f.read()
			f.close()

		Screen.__init__(self, session)

		self["actions"]  = ActionMap(["OkCancelActions", "ShortcutActions", "EPGSelectActions", "WizardActions", "ColorActions", "NumberActions", "MenuActions", "MoviePlayerActions", "InfobarSeekActions"], {
			"ok"    : self.keyOK,
			"cancel": self.keyCancel,
		}, -1)

		self['title'] = Label("PrimeWire.ag")
		self['leftContentTitle'] = Label("Streams")
		self['stationIcon'] = Pixmap()
		self['handlung'] = Label("")

		self.streamList = []
		self.streamMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.streamMenuList.l.setFont(0, gFont('mediaportal', 24))
		self.streamMenuList.l.setItemHeight(25)
		self['streamlist'] = self.streamMenuList

		self.keyLocked = True
		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		print self.movielink
		getPage(self.movielink, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.parseData).addErrback(self.dataError)

	def parseData(self, data):
		streams = re.findall('<a\shref="/external.php\?gd=(.*?)&.*?&url=(.*?)&.*?document.writeln\(\'(.*?)\'\)',data, re.S)
		if streams:
			for (chCode, chUrl, chStreamHoster) in streams:
				chUrl = 'http://www.primewire.ag/external.php?gd=%s&url=%s&%s' % (chCode, chUrl, chStreamHoster)
				print chStreamHoster, chUrl
				if re.match('.*?(putme|limevideo|stream2k|played|putlocker|sockshare|streamclou|xvidstage|filenuke|movreel|nowvideo|xvidstream|uploadc|vreer|MonsterUploads|Novamov|Videoweed|Divxstage|Ginbig|Flashstrea|Movshare|yesload|faststream|Vidstream|PrimeShare|flashx|Divxmov|Zooupload|Wupfile|BitShare|Userporn|sharesix)', chStreamHoster, re.S):
					self.streamList.append((chStreamHoster, chUrl))
			self.streamMenuList.setList(map(chStreamListEntry, self.streamList))
			self.keyLocked = False
		details = re.findall('<meta\sname="description"\scontent="Watch.(.*?)">.*?<meta\sproperty="og:image"\scontent="(.*?)"/>', data, re.S)
		if details:
			(handlung,image) = details[0]
			self['handlung'].setText(decodeHtml(handlung))
			self.showInfos(image)

	def dataError(self, error):
		printl(error,self,"E")

	def showInfos(self,coverUrl):
		print coverUrl
		downloadPage(coverUrl, "/tmp/chIcon.jpg").addCallback(self.showCover)

	def showCover(self, picData):
		if fileExists("/tmp/chIcon.jpg"):
			self['stationIcon'].instance.setPixmap(gPixmapPtr())
			self.scale = AVSwitch().getFramebufferScale()
			self.picload = ePicLoad()
			size = self['stationIcon'].instance.size()
			self.picload.setPara((size.width(), size.height(), self.scale[0], self.scale[1], False, 1, "#FF000000"))
			if self.picload.startDecode("/tmp/chIcon.jpg", 0, 0, False) == 0:
				ptr = self.picload.getData()
				if ptr != None:
					self['stationIcon'].instance.setPixmap(ptr)
					self['stationIcon'].show()
					del self.picload

	def keyOK(self):
		exist = self['streamlist'].getCurrent()
		if self.keyLocked or exist == None:
			return
		auswahl = self['streamlist'].getCurrent()[0][1]
		print auswahl
		getPage(auswahl, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.get_link).addErrback(self.dataError)

	def get_link(self, data):
		hoster = re.findall('<noframes>(.*?)</noframes>',data, re.S)
		if hoster:
			get_stream_link(self.session).check_link(hoster[0], self.got_link)

	def got_link(self, stream_url):
		print stream_url
		self.session.open(SimplePlayer, [(self.titel, stream_url)], showPlaylist=False, ltype='primewire')

	def keyCancel(self):
		self.close()