from Plugins.Extensions.MediaPortal.resources.imports import *

ck = {}

def chListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 20, 0, 860, 25, 0, RT_HALIGN_LEFT, entry[0])
		]
def chStreamListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 20, 0, 860, 25, 0, RT_HALIGN_CENTER, entry[0])
		]
def chMainListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 20, 0, 860, 25, 0, RT_HALIGN_CENTER, entry[0])
		]
		
class chMain(Screen):
	
	def __init__(self, session):
		self.session = session
		path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/%s/chMain.xml" % config.mediaportal.skin.value
		if not fileExists(path):
			path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/original/chMain.xml"
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
		self['leftContentTitle'] = Label("M e n u")
		self['stationIcon'] = Pixmap()
		
		self.streamList = []
		self.streamMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.streamMenuList.l.setFont(0, gFont('mediaportal', 24))
		self.streamMenuList.l.setItemHeight(25)
		self['streamlist'] = self.streamMenuList
		
		self.keyLocked = False
		self.onLayoutFinish.append(self.layoutFinished)
		
	def layoutFinished(self):
		self.keyLocked = True
		self.streamList.append(("Featured Movies", "http://www.primewire.ag/index.php?sort=featured&page="))
		self.streamList.append(("TV Shows","http://www.primewire.ag/index.php?tv=&sort=views&page="))
		self.streamMenuList.setList(map(chMainListEntry, self.streamList))
		self.keyLocked = False
			
	def keyOK(self):
		exist = self['streamlist'].getCurrent()
		if self.keyLocked or exist == None:
			return
		auswahl = self['streamlist'].getCurrent()[0][0]
		url = self['streamlist'].getCurrent()[0][1]
		print auswahl
		if auswahl == "Featured Movies":
			self.session.open(chFeatured, url)
		elif auswahl == "TV Shows":
			self.session.open(chTVshows, url)
			
	def keyCancel(self):
		self.close()

class chFeatured(Screen):
	
	def __init__(self, session, chGotLink):
		self.chGotLink = chGotLink
		self.session = session
		path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/%s/chFeatured.xml" % config.mediaportal.skin.value
		if not fileExists(path):
			path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/original/chFeatured.xml"
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
		self['leftContentTitle'] = Label("Featured Movies")
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
		print error
			
	def keyOK(self):
		exist = self['streamlist'].getCurrent()
		if self.keyLocked or exist == None:
			return
		titel = self['streamlist'].getCurrent()[0][0]
		auswahl = self['streamlist'].getCurrent()[0][1]
		print auswahl
		self.session.open(chStreams, auswahl, titel)

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

class chTVshows(Screen):
	
	def __init__(self, session, chGotLink):
		self.chGotLink = chGotLink
		self.session = session
		path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/%s/chTVshows.xml" % config.mediaportal.skin.value
		if not fileExists(path):
			path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/original/chTVshows.xml"
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
		self['leftContentTitle'] = Label("TV Shows")
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
		print error
			
	def keyOK(self):
		exist = self['streamlist'].getCurrent()
		if self.keyLocked or exist == None:
			return
		auswahl = self['streamlist'].getCurrent()[0][1]
		print auswahl
		self.session.open(chTVshowsEpisode, auswahl)

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
		
class chTVshowsEpisode(Screen):
		
	def __init__(self, session, chGotLink):
		self.chGotLink = chGotLink
		self.session = session
		path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/%s/chTVshowsEpisode.xml" % config.mediaportal.skin.value
		if not fileExists(path):
			path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/original/chTVshowsEpisode.xml"
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
		self['leftContentTitle'] = Label("Season Episode")
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
		episoden = re.findall('class="tv_episode_item.*?">.*?<a\shref="(.*?)"\stitle="Watch.*?Episode\s[0-9]+(.*?)"', data, re.S|re.I)
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
		print error
			
	def keyOK(self):
		exist = self['streamlist'].getCurrent()
		if self.keyLocked or exist == None:
			return
		titel = self['streamlist'].getCurrent()[0][0]
		auswahl = self['streamlist'].getCurrent()[0][1]
		print auswahl
		self.session.open(chStreams, auswahl, titel)

	def keyCancel(self):
		self.close()
		
class chStreams(Screen):
	
	def __init__(self, session, movielink, name):
		self.session = session
		self.movielink = movielink
		self.titel = name
		path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/%s/chStreams.xml" % config.mediaportal.skin.value
		if not fileExists(path):
			path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/original/chStreams.xml"
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
		streams = re.findall('<a\shref="/external.php\?gd=(.*?)&.*?document.writeln\(\'(.*?)\'\)',data, re.S)
		if streams:
			for (chCode, chStreamHoster) in streams:
				chUrl = 'http://www.primewire.ag/external.php?gd=%s&%s' % (chCode, chStreamHoster)
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
		print error
		
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
		req = urllib2.Request(auswahl)
		res = urllib2.urlopen(req)
		url = res.geturl()
		get_stream_link(self.session).check_link(url, self.got_link)
		
	def got_link(self, stream_url):
		print stream_url
		sref = eServiceReference(0x1001, 0, stream_url)
		sref.setName(self.titel)
		self.session.open(MoviePlayer, sref)
		
	def keyCancel(self):
		self.close()