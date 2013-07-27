from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.yt_url import *
from Plugins.Extensions.MediaPortal.resources.simpleplayer import SimplePlayer

def mlehdGenreListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 0, 0, 850, 25, 0, RT_HALIGN_CENTER | RT_VALIGN_CENTER, entry[0])
		]

def mlehdListEntry(entry):
	#TYPE_TEXT, x, y, width, height, fnt, flags, string [, color, backColor, backColorSelected, borderWidth, borderColor])
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 50, 0, 800, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry[0])
		]

class mlehdGenreScreen(Screen):

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

		self["actions"]  = ActionMap(["OkCancelActions", "ShortcutActions", "WizardActions", "ColorActions", "SetupActions", "NumberActions", "MenuActions", "EPGSelectActions"], {
			"ok"    : self.keyOK,
			"cancel": self.keyCancel,
			"red": self.keyCancel
		}, -1)

		self.keyLocked = True
		self.language = "de"
		self['title'] = Label("mle-hd.se")
		self['ContentTitle'] = Label("Genre:")
		self['name'] = Label("")
		self['F1'] = Label("Exit")
		self['F2'] = Label("")
		self['F3'] = Label("")
		self['F4'] = Label("")
		self['F3'].hide()
		self['F4'].hide()

		self.genreliste = []
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['genreList'] = self.chooseMenuList

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.genreliste = [("Neuesten", "http://www.mle-hd.se/page/"),
							("Abenteuer", "http://www.mle-hd.se/category/abenteuer/page/"),
							("Action", "http://www.mle-hd.se/category/action/page/"),
							("Animation-Zeichentrick", "http://www.mle-hd.se/category/animation-zeichentrick/page/"),
							("Biografie-History", "http://www.mle-hd.se/category/biografiehistory/page/"),
							("Doku", "http://www.mle-hd.se/category/doku/page/page/"),
							("Drama", "http://www.mle-hd.se/category/dramathriller/page/"),
							("Kinderfilme", "http://www.mle-hd.se/category/kinderfilme/page/"),
							("Fantasy", "http://www.mle-hd.se/category/fantasy/page/"),
							("Horror", "http://www.mle-hd.se/category/horror/page/"),
							("Comedy", "http://www.mle-hd.se/category/komodien/page/"),
							("Krieg", "http://www.mle-hd.se/category/krieg/page/"),
							("Musik", "http://www.mle-hd.se/category/musik/page/"),
							("Romantik", "http://www.mle-hd.se/category/romantik/page/"),
							("Scifi", "http://www.mle-hd.se/category/scifi/page/"),
							("Sport", "http://www.mle-hd.se/category/sport/page/"),
							("Thriller", "http://www.mle-hd.se/category/thriller/page/"),
							("Western", "http://www.mle-hd.se/category/western/page/")]

		self.chooseMenuList.setList(map(mlehdGenreListEntry, self.genreliste))
		self.keyLocked = False

	def dataError(self, error):
		printl(error,self,"E")


	def keyOK(self):
		if self.keyLocked:
			return
		mlehdGenre = self['genreList'].getCurrent()[0][0]
		mlehdUrl = self['genreList'].getCurrent()[0][1]
		print mlehdGenre, mlehdUrl
		self.session.open(mlehdFilmListeScreen, mlehdGenre, mlehdUrl)

	def keyCancel(self):
		self.close()

class mlehdFilmListeScreen(Screen):

	def __init__(self, session, genreName, genreLink):
		self.session = session
		self.genreLink = genreLink
		self.genreName = genreName
		self.plugin_path = mp_globals.pluginPath
		self.skin_path =  mp_globals.pluginPath + "/skins"

		path = "%s/%s/defaultListScreen.xml" % (self.skin_path, config.mediaportal.skin.value)
		if not fileExists(path):
			path = self.skin_path + "/original/defaultListScreen.xml"

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
			"prevBouquet" : self.keyPageDown
		}, -1)

		self.keyLocked = True
		self.page = 1
		self['title'] = Label("mle-hd.se")
		self['ContentTitle'] = Label("%s:" % self.genreName)
		self['name'] = Label("")
		self['F1'] = Label("Exit")
		self['F2'] = Label("")
		self['F3'] = Label("")
		self['F4'] = Label("")
		self['F1'].hide()
		self['F2'].hide()
		self['F3'].hide()
		self['F4'].hide()
		self['coverArt'] = Pixmap()
		self['Page'] = Label("1")
		self['page'] = Label("")
		self['handlung'] = Label("")

		self.filmliste = []
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['liste'] = self.chooseMenuList

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.keyLocked = True
		url = "%s%s" % (self.genreLink,str(self.page))
		print url
		getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.loadPageData).addErrback(self.dataError)

	def loadPageData(self, data):
		print "drin"
		lastpage = re.findall('<div id="pagination"><span>Page.*?of (.*?)</span>', data)
		if lastpage:
			self['page'].setText(lastpage[0])

		#movies = re.findall('<div class="chipsetl1data">.*?<a href="(http://www.mle-hd.se/.*?)" rel="bookmark" title="Permanent Link to (.*?)" class="img1">.*?<img.*?src="(http://www.mle-hd.se/wp-content/uploads/.*?)"', data, re.S)
		movies = re.findall('<div class="entry ">.*?<a href="(http://www.mle-hd.se/.*?)" title="(.*?)" class="opacity"><img.*?src="(http://www.mle-hd.se/wp-content/uploads/.*?)"', data, re.S)
		if movies:
			self.filmliste = []
			for (url,title,image) in movies:
				print title, url
				self.filmliste.append((decodeHtml(title),url,image))
			self.chooseMenuList.setList(map(mlehdListEntry, self.filmliste))
			self['Page'].setText(str(self.page)+" von")
			self.keyLocked = False
			self.loadPic()

	def dataError(self, error):
		printl(error,self,"E")

	def loadPic(self):
		streamPic = self['liste'].getCurrent()[0][2]
		print streamPic
		downloadPage(streamPic, "/tmp/Icon.jpg").addCallback(self.ShowCover)

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
		self.loadPic()

	def keyRight(self):
		if self.keyLocked:
			return
		self['liste'].pageDown()
		self.loadPic()

	def keyUp(self):
		if self.keyLocked:
			return
		self['liste'].up()
		self.loadPic()

	def keyDown(self):
		if self.keyLocked:
			return
		self['liste'].down()
		self.loadPic()

	def keyOK(self):
		if self.keyLocked:
			return
		self.mlehdName = self['liste'].getCurrent()[0][0]
		mlehdurl = self['liste'].getCurrent()[0][1]
		print self.mlehdName, mlehdurl
		self.session.open(mlehdFilmAuswahlScreen, self.mlehdName, mlehdurl)

	def keyCancel(self):
		self.close()

class mlehdFilmAuswahlScreen(Screen):

	def __init__(self, session, genreName, genreLink):
		self.session = session
		self.genreLink = genreLink
		self.genreName = genreName
		self.plugin_path = mp_globals.pluginPath
		self.skin_path =  mp_globals.pluginPath + "/skins"

		path = "%s/%s/defaultListScreen.xml" % (self.skin_path, config.mediaportal.skin.value)
		if not fileExists(path):
			path = self.skin_path + "/original/defaultListScreen.xml"

		with open(path, "r") as f:
			self.skin = f.read()
			f.close()

		Screen.__init__(self, session)

		self["actions"]  = ActionMap(["OkCancelActions", "ShortcutActions", "WizardActions", "ColorActions", "SetupActions", "NumberActions", "MenuActions", "EPGSelectActions"], {
			"ok"    : self.keyOK,
			"cancel": self.keyCancel
		}, -1)

		self.keyLocked = True
		self['title'] = Label("mle-hd.se")
		self['ContentTitle'] = Label("Part Auswahl - %s" % self.genreName)
		self['name'] = Label("")
		self['F1'] = Label("Exit")
		self['F2'] = Label("")
		self['F3'] = Label("")
		self['F4'] = Label("")
		self['F1'].hide()
		self['F2'].hide()
		self['F3'].hide()
		self['F4'].hide()
		self['coverArt'] = Pixmap()
		self['Page'] = Label("")
		self['page'] = Label("")
		self['handlung'] = Label("")

		self.filmliste = []
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['liste'] = self.chooseMenuList
		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.keyLocked = True
		print self.genreLink
		getPage(self.genreLink, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.loadPageData).addErrback(self.dataError)

	def loadPageData(self, data):
		print "drin"
		if re.match('.*?mightyupload.com/embed', data, re.S):
			streamhoster = re.findall('<iframe SRC="(.*?)"', data, re.S)
			if streamhoster:
				print streamhoster
				self.filmliste = []
				count = 0
				for url in streamhoster:
					count += 1
					print url
					part = "Film %s" % count
					self.filmliste.append((part,url))
				self.chooseMenuList.setList(map(mlehdGenreListEntry, self.filmliste))
				self.keyLocked = False

		else:
			movies = re.findall("file: '(.*?)\&sid", data, re.S)
			if movies:
				print movies
				self.filmliste = []
				count = 0
				for url in movies:
					count += 1
					print url
					part = "Film %s" % count
					self.filmliste.append((part,url))
				self.chooseMenuList.setList(map(mlehdGenreListEntry, self.filmliste))
				self.keyLocked = False

	def keyOK(self):
		if self.keyLocked:
			return
		self.part = self['liste'].getCurrent()[0][0]
		link = self['liste'].getCurrent()[0][1]

		if re.match('.*?mightyupload.com/embed', link, re.S):
			get_stream_link(self.session).check_link(link, self.got_link, False)
		else:
			getPage(link, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.getStream).addErrback(self.dataError)

	def got_link(self, stream_url):
		if stream_url == None:
			message = self.session.open(MessageBox, _("Stream not found, try another Stream Hoster."), MessageBox.TYPE_INFO, timeout=3)
		else:
			title = self.genreName+" "+self.part
			self.session.open(SimplePlayer, [(title, stream_url)], showPlaylist=False, ltype='mlehd')

	def getStream(self, data):
		stream_url = re.findall('<location>(http://.*?)</location>', data, re.S)
		if stream_url:
			print stream_url
			title = self.genreName+" "+self.part
			self.session.open(SimplePlayer, [(title, stream_url[0])], showPlaylist=False, ltype='mlehd')

	def dataError(self, error):
		printl(error,self,"E")

	def keyCancel(self):
		self.close()