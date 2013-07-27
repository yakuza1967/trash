#	-*-	coding:	utf-8	-*-
from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.simpleplayer import SimplePlayer

kekse = {}

def MEHDGenreListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 20, 0, 900, 25, 0, RT_HALIGN_CENTER | RT_VALIGN_CENTER, entry[0])
		]
class showMEHDGenre(Screen):

	def __init__(self, session):
		self.session = session
		path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/%s/showMEHDGenre.xml" % config.mediaportal.skin.value
		if not fileExists(path):
			path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/original/showMEHDGenre.xml"
		print path
		with open(path, "r") as f:
			self.skin = f.read()
			f.close()

		Screen.__init__(self, session)

		self["actions"] = ActionMap(["OkCancelActions", "ShortcutActions", "WizardActions", "ColorActions", "SetupActions", "NumberActions", "MenuActions", "EPGSelectActions"], {
			"ok"    : self.keyOK,
			"cancel": self.keyCancel
		}, -1)

		self['title'] = Label("My-Entertainment.biz")
		self['name'] = Label("Genre Auswahl")
		self['handlung'] = Label("")
		self['coverArt'] = Pixmap()

		self.keyLocked = True
		self.filmliste = []
		self.searchTxt = ""
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['filmList'] = self.chooseMenuList

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		filmliste = []
		Genre = [("Suche", "suche"),
			("Neueinsteiger", "http://my-entertainment.biz/forum/content.php?r=1969-Aktuelle-HD-Filme&page="),
			("Cineline", "http://my-entertainment.biz/forum/list.php?r=category/169-Cineline&page="),
			("Collection", "http://my-entertainment.biz/forum/content.php?r=3501-hd-collection&page="),
			("Abenteuer", "http://my-entertainment.biz/forum/list.php?r=category/65-HD-Abenteuer&page="),
			("Action", "http://my-entertainment.biz/forum/list.php?r=category/35-HD-Action&page="),
			("Biografie", "http://my-entertainment.biz/forum/list.php?r=category/70-HD-Biografie&page="),
			("Doku", "http://my-entertainment.biz/forum/list.php?r=category/64-HD-Doku&page="),
			("Drama", "http://my-entertainment.biz/forum/list.php?r=category/36-HD-Drama&page="),
			("Fantasy", "http://my-entertainment.biz/forum/list.php?r=category/37-HD-Fantasy&page="),
			("Horror", "http://my-entertainment.biz/forum/list.php?r=category/38-HD-Horror&page="),
			("Komödie", "http://my-entertainment.biz/forum/list.php?r=category/39-HD-Kom%F6die&page="),
			("Kriegsfilm", "http://my-entertainment.biz/forum/list.php?r=category/66-HD-Kriegsfilm&page="),
			("Krimi", "http://my-entertainment.biz/forum/list.php?r=category/56-HD-Krimi&page="),
			("Musik", "http://my-entertainment.biz/forum/list.php?r=category/63-HD-Musik&page="),
			("Mystery", "http://my-entertainment.biz/forum/list.php?r=category/62-HD-Mystery&page="),
			("Romanze", "http://my-entertainment.biz/forum/list.php?r=category/40-HD-Romanze&page="),
			("SciFi", "http://my-entertainment.biz/forum/list.php?r=category/41-HD-SciFi&page="),
			("Serien", "http://my-entertainment.biz/forum/content.php?r=1072-Serien&page="),
			("Thriller", "http://my-entertainment.biz/forum/list.php?r=category/42-HD-Thriller&page="),
			("Zeichentrick", "http://my-entertainment.biz/forum/list.php?r=category/43-HD-Zeichentrick&page=")]

		for (Name,Url) in Genre:
			self.filmliste.append((Name,Url))
			self.chooseMenuList.setList(map(MEHDGenreListEntry, self.filmliste))
		self.keyLocked = False

	def keyOK(self):
		if self.keyLocked:
			return
		genreName = self['filmList'].getCurrent()[0][0]
		genreLink = self['filmList'].getCurrent()[0][1]
		print genreLink
		if genreName == "Suche":
			print 'suchen'
			self.session.openWithCallback(self.mySearch, VirtualKeyBoard, title = (_("Suche.....")), text = self.searchTxt)
		else:
			self.session.open(MEHDFilmListeScreen, genreLink, genreName)


	def mySearch(self, callback = None):
		print 'mySearch'
		if callback != None:
			self.searchTxt = callback.replace(' ', "%20")
			print self.searchTxt
			tmpEnterPre = "http://my-entertainment.biz/forum/search.php?query='%s'" % self.searchTxt
			enterAuswahlLink = tmpEnterPre + "&titleonly=0&beforeafter=after&contenttypeid=18&sortby=dateline&order=descending&sortorder=descending&searchfromtype=vBForum%3ASearchCommon&type[]=18&do=process"
			self.session.open(MEHDFilmListeScreen, enterAuswahlLink, "Suche")

	def keyCancel(self):
		self.close()

def MEHDFilmListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 20, 0, 900, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry[0])
		]

class MEHDFilmListeScreen(Screen):

	def __init__(self, session, genreLink, genreName):
		self.session = session
		self.genreLink = genreLink
		self.genreName = genreName
		path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/%s/MEHDFilmListeScreen.xml" % config.mediaportal.skin.value
		if not fileExists(path):
			path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/original/MEHDFilmListeScreen.xml"
		print path
		with open(path, "r") as f:
			self.skin = f.read()
			f.close()

		Screen.__init__(self, session)

		self["actions"]  = ActionMap(["OkCancelActions", "ShortcutActions", "WizardActions", "ColorActions", "SetupActions", "NumberActions", "MenuActions", "EPGSelectActions"], {
			"ok"    : self.keyOK,
			"cancel": self.keyCancel,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft,
			"nextBouquet" : self.keyPageUp,
			"prevBouquet" : self.keyPageDown,
			"blue" : self.keyBlue
		}, -1)

		self['title'] = Label("My-Entertainment.biz")
		self['name'] = Label(self.genreName)
		self['handlung'] = Label("")
		self['coverArt'] = Pixmap()
		self['page'] = Label("1")

		self.keyLocked = True
		self.filmliste = []
		self.page = 1
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['filmList'] = self.chooseMenuList

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		if self.genreName == "Suche":
			url = self.genreLink
			print url
			getPage(url, cookies=kekse, agent=std_headers, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.loadPageData).addErrback(self.dataError)
		else:
			url = "%s%s" % (self.genreLink, str(self.page))
			print url
			getPage(url, cookies=kekse, agent=std_headers, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.loadPageData).addErrback(self.dataError)

	def dataError(self, error):
		printl(error,self,"E")

	def loadPageData(self, data):
		print "daten bekommen"
		if self.genreName == "Suche":
			links = re.findall('<h3 class="searchtitle">.*?<a href="(.*?)".*?title="">(.*?)</a>', data, re.S)
			for enterLink, enterName in links:
				self.filmliste.append((decodeHtml2(enterName), enterLink, ""))
			self.chooseMenuList.setList(map(MEHDFilmListEntry, self.filmliste))
			self.keyLocked = False
		else:
			filme = re.findall('<div class="article_preview">.*?<a href="(.*?)"><span>(.*?)</span>.*?<img.*?src="(.*?)"', data, re.S)
			if filme:
				self.filmliste = []
				for (url,name,image) in filme:
					name = name.replace("HD: ","")
					self.filmliste.append((decodeHtml2(name), url, image))
				self.chooseMenuList.setList(map(MEHDFilmListEntry, self.filmliste))
				self.keyLocked = False
				self.loadPic()

	def loadPic(self):
		self['page'].setText(str(self.page))
		streamName = self['filmList'].getCurrent()[0][0]
		streamUrl = self['filmList'].getCurrent()[0][1]
		self.getHandlung(streamUrl)
		self['name'].setText(streamName)
		streamPic = self['filmList'].getCurrent()[0][2]
		downloadPage(streamPic, "/tmp/Icon.jpg").addCallback(self.ShowCover)

	def getHandlung(self, url):
		getPage(url, cookies=kekse, agent=std_headers, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.setHandlung).addErrback(self.dataError)

	def setHandlung(self, data):
		handlung = re.findall('<div class="bbcode_quote_container"></div>(.*?)<', data, re.S)
		if handlung:
			self['handlung'].setText(decodeHtml2(handlung[0]))
		else:
			self['handlung'].setText("Keine Infos gefunden.")

	def ShowCover(self, picData):
		if fileExists("/tmp/Icon.jpg"):
			self['coverArt'].instance.setPixmap(gPixmapPtr())
			self.scale = AVSwitch().getFramebufferScale()
			self.picload = ePicLoad()
			size = self['coverArt'].instance.size()
			self.picload.setPara((size.width(), size.height(), self.scale[0], self.scale[1], False, 1, "#FF000000"))
			if self.picload.startDecode("/tmp/Icon.jpg", 0, 0, False) == 0:
				ptr = self.picload.getData()
				if ptr != None:
					self['coverArt'].instance.setPixmap(ptr)
					self['coverArt'].show()
					del self.picload

	def keyOK(self):
		if self.keyLocked:
			return
		streamLink = self['filmList'].getCurrent()[0][1]
		getPage(streamLink, cookies=kekse, agent=std_headers, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.getStream).addErrback(self.dataError)

	def getStream(self, data):
		if self.genreName == 'Serien':
			print 'getStream__serien'
			streamPic = self['filmList'].getCurrent()[0][2]
			folgen = re.findall('<a href="(http://streamcloud.*?)".*?target="_blank">(.*?).avi',data,re.S)
			self.session.open(enterSerienListScreen, folgen, streamPic)
		else:
			stream = re.findall('href="(http://my-entertainment.biz/.*?/Free-Membe.*?.php\?mov=.*?)"', data)
			if len(stream) == 1:
				print 'Ein Free Stream....',stream
				getPage(stream[0], cookies=kekse, agent=std_headers, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.getStreamLink).addErrback(self.dataError)
			else:
				searchTitle = re.findall('>*\s*\r*\n<.*?>*\r*\n*\s(.*?)<.*?>*\r*\n*\s*<*>*\r*\n*<div style="margin: 5px;">', decodeHtml(data))
				searchCol = re.findall('<img src="(http://my-entertainment.biz.*?)".*?href="(http://my-entertainment.biz/server/Free-Member.php\\?mov=.*?)"', data, re.S)
				self.session.open(enterColListScreen, searchCol, searchTitle)

	def getStreamLink(self, data):
			print data
			#print 'streamdata...:', data
			streamName = self['filmList'].getCurrent()[0][0]
			stream_url = re.findall('(http://free.+.my-entertainment.biz.*?)"', data, re.S)
			print stream_url
			if stream_url:
				streamName = self['filmList'].getCurrent()[0][0]
				self.session.open(SimplePlayer, [(streamName, stream_url[0])], showPlaylist=False, ltype='myentertainment')

	def keyUp(self):
		if self.keyLocked:
			return
		self['filmList'].up()
		self.loadPic()

	def keyDown(self):
		if self.keyLocked:
			return
		self['filmList'].down()
		self.loadPic()

	def keyLeft(self):
		if self.keyLocked:
			return
		self['filmList'].pageUp()
		self.loadPic()

	def keyRight(self):
		if self.keyLocked:
			return
		self['filmList'].pageDown()
		self.loadPic()

	def keyPageDown(self):
		print "PageDown"
		if self.keyLocked:
			return
		if not self.page < 1:
			self.page -= 1
			self.loadPage()

	def keyPageUp(self):
		print "PageUp"
		if self.keyLocked:
			return
		self.page += 1
		self.loadPage()

	def keyBlue(self):
		streamLink = self['filmList'].getCurrent()[0][1]
		getPage(streamLink, cookies=kekse, agent=std_headers, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.getYTrailer).addErrback(self.dataError)

	def getYTrailer(self, data):
		print "getYTrailer..."
		ytLinkIds = re.findall('<param name="movie" value="http://www.youtube.com/v/(.*?)\;', data, re.S)
		if ytLinkIds:
			ytLinkId = str(ytLinkIds[0].replace('&amp', ''))
			y = youtubeUrl(self.session)
			y.addErrback(self.dataError)
			ytLink = y.getVideoUrl(ytLinkId, "2")
			if ytLink:
				streamName = self['filmList'].getCurrent()[0][0]
				self.session.open(SimplePlayer, [(streamName, ytLink)], showPlaylist=False, ltype='myentertainment')
			else:
				sText = 'Kein Trailer verfuegbar'
				self.session.open(MessageBox,_(sText), MessageBox.TYPE_INFO)
		else:
			sText = 'Kein Trailer verfuegbar'
			self.session.open(MessageBox,_(sText), MessageBox.TYPE_INFO)

	def keyCancel(self):
		self.close()

def enterColListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 20, 0, 900, 25, 0, RT_HALIGN_CENTER | RT_VALIGN_CENTER, entry[0])
		]

class enterColListScreen(Screen):

	def __init__(self, session, pageCol, pageTitle,):
		self.session = session
		self.pageCol = pageCol
		self.pageTitle = pageTitle
		path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/%s/focus.xml" % config.mediaportal.skin.value
		if not fileExists(path):
			path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/original/focus.xml"
		print path
		with open(path, "r") as f:
			self.skin = f.read()
			f.close()

		Screen.__init__(self, session)

		self["actions"]  = ActionMap(["OkCancelActions", "ShortcutActions", "WizardActions", "ColorActions", "SetupActions", "NumberActions", "MenuActions"], {
			"ok"    : self.keyOK,
			"cancel": self.keyCancel,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft,
		}, -1)

		self['title'] = Label("My-Entertainment.biz")
		self['name'] = Label("Auswahl")
		self['handlung'] = Label("")
		self['coverArt'] = Pixmap()

		self.keyLocked = True
		self.streamliste = []
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['streamlist'] = self.chooseMenuList
		self.onLayoutFinish.append(self.showColData)

	def showColData(self):
		i=0
		if self.pageCol:
			for enterPic,enterUrl in self.pageCol:
				self.streamliste.append((self.pageTitle[i], enterUrl, enterPic))
				i=i+1
			self.chooseMenuList.setList(map(enterColListEntry, self.streamliste))
			self.keyLocked = False
			self.loadPic()

	def loadPic(self):
		streamName = self['streamlist'].getCurrent()[0][0]
		streamFilmLink = self['streamlist'].getCurrent()[0][1]
		self['name'].setText(streamName)
		streamPic = self['streamlist'].getCurrent()[0][2]
		downloadPage(streamPic, "/tmp/spIcon.jpg").addCallback(self.ShowCover)


	def ShowCover(self, picData):
		if fileExists("/tmp/spIcon.jpg"):
			self['coverArt'].instance.setPixmap(gPixmapPtr())
			self.scale = AVSwitch().getFramebufferScale()
			self.picload = ePicLoad()
			size = self['coverArt'].instance.size()
			self.picload.setPara((size.width(), size.height(), self.scale[0], self.scale[1], False, 1, "#FF000000"))
			if self.picload.startDecode("/tmp/spIcon.jpg", 0, 0, False) == 0:
				ptr = self.picload.getData()
				if ptr != None:
					self['coverArt'].instance.setPixmap(ptr)
					self['coverArt'].show()
					del self.picload


	def getRealLink(self, data):
		print 'getRealLink'
		stream_url = re.findall('(http://free-s1.my-entertainment.biz.*?)"', data, re.S)
		print stream_url
		if stream_url:
			print stream_url
			self.startMovie(stream_url[0])

	def startMovie(self, link):
		self.session.open(SimplePlayer, [(self.streamName, link)], showPlaylist=False, ltype='myentertainment')

	def keyOK(self):
		if self.keyLocked:
			return
		streamLink = self['streamlist'].getCurrent()[0][1]
		self.streamName = self['streamlist'].getCurrent()[0][0]
		print 'RealStreamLink...', streamLink
		getPage(streamLink, cookies=kekse, agent=std_headers, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.getRealLink).addErrback(self.dataError)

	def dataError(self, error):
		printl(error,self,"E")

	def keyLeft(self):
		if self.keyLocked:
			return
		self['streamlist'].pageUp()
		self.loadPic()

	def keyRight(self):
		if self.keyLocked:
			return
		self['streamlist'].pageDown()
		self.loadPic()

	def keyUp(self):
		if self.keyLocked:
			return
		self['streamlist'].up()
		self.loadPic()

	def keyDown(self):
		if self.keyLocked:
			return
		self['streamlist'].down()
		self.loadPic()

	def keyCancel(self):
		self.close()

def enterSerienListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 20, 0, 900, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry[0])
		]

class enterSerienListScreen(Screen):

	def __init__(self, session, folgenCol, folgenPic):
		self.session = session
		self.folgenCol = folgenCol
		self.folgenPic = folgenPic
		path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/%s/focus.xml" % config.mediaportal.skin.value
		if not fileExists(path):
			path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/original/focus.xml"
		print path
		with open(path, "r") as f:
			self.skin = f.read()
			f.close()

		Screen.__init__(self, session)

		self["actions"]  = ActionMap(["OkCancelActions", "ShortcutActions", "WizardActions", "ColorActions", "SetupActions", "NumberActions", "MenuActions"], {
			"ok"    : self.keyOK,
			"cancel": self.keyCancel,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft,
		}, -1)

		self['title'] = Label("My-Entertainment.biz")
		self['name'] = Label("Auswahl")
		self['handlung'] = Label("")
		self['coverArt'] = Pixmap()

		self.keyLocked = True
		self.streamliste = []
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['streamlist'] = self.chooseMenuList
		self.onLayoutFinish.append(self.showColData)

	def showColData(self):
		i=1
		if self.folgenCol:
			self.filmliste = []
			for (url,name) in self.folgenCol:
				self.filmliste.append((decodeHtml2(name), url, self.folgenPic))
			self.chooseMenuList.setList(map(enterSerienListEntry, self.filmliste))
			self.keyLocked = False
			self.loadPic

	def loadPic(self):
		streamName = self['streamlist'].getCurrent()[0][0]
		streamFilmLink = self['streamlist'].getCurrent()[0][1]
		self['name'].setText(streamName)
		streamPic = self['streamlist'].getCurrent()[0][2]
		downloadPage(streamPic, "/tmp/spIcon.jpg").addCallback(self.ShowCover)


	def ShowCover(self, picData):
		if fileExists("/tmp/spIcon.jpg"):
			self['coverArt'].instance.setPixmap(gPixmapPtr())
			self.scale = AVSwitch().getFramebufferScale()
			self.picload = ePicLoad()
			size = self['coverArt'].instance.size()
			self.picload.setPara((size.width(), size.height(), self.scale[0], self.scale[1], False, 1, "#FF000000"))
			if self.picload.startDecode("/tmp/spIcon.jpg", 0, 0, False) == 0:
				ptr = self.picload.getData()
				if ptr != None:
					self['coverArt'].instance.setPixmap(ptr)
					self['coverArt'].show()
					del self.picload

	def keyOK(self):
		if self.keyLocked:
			return
		link = self['streamlist'].getCurrent()[0][1]
		self.streamName = self['streamlist'].getCurrent()[0][0]
		link_found = False
		if link:
			link_found = True
			print link
			get_stream_link(self.session).check_link(link, self.got_link, False)
		if not link_found:
			message = self.session.open(MessageBox, _("Stream not found, try another Stream Hoster."), MessageBox.TYPE_INFO, timeout=5)

	def got_link(self, stream_url):
		if stream_url == None:
			message = self.session.open(MessageBox, _("Stream not found, try another Stream Hoster."), MessageBox.TYPE_INFO, timeout=3)
		else:
			self.session.open(SimplePlayer, [(self.streamName, stream_url)], showPlaylist=False, ltype='myentertainment')

	def dataError(self, error):
		printl(error,self,"E")

	def keyLeft(self):
		if self.keyLocked:
			return
		self['streamlist'].pageUp()
		self.loadPic()

	def keyRight(self):
		if self.keyLocked:
			return
		self['streamlist'].pageDown()
		self.loadPic()

	def keyUp(self):
		if self.keyLocked:
			return
		self['streamlist'].up()
		self.loadPic()

	def keyDown(self):
		if self.keyLocked:
			return
		self['streamlist'].down()
		self.loadPic()

	def keyCancel(self):
		self.close()