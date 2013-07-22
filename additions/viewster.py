from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.simpleplayer import SimplePlayer

def viewsterGenreListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 0, 0, 850, 25, 0, RT_HALIGN_CENTER | RT_VALIGN_CENTER, entry[0])
		]

def viewsterListEntry(entry):
	#TYPE_TEXT, x, y, width, height, fnt, flags, string [, color, backColor, backColorSelected, borderWidth, borderColor])
	png = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/images/%s.png" % entry[3]
	if fileExists(png):
		flag = LoadPixmap(png)
		return [entry,
			(eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST, 15, 2, 20, 20, flag),
			(eListboxPythonMultiContent.TYPE_TEXT, 50, 0, 600, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry[0])
			]
	else:
		return [entry,
			(eListboxPythonMultiContent.TYPE_TEXT, 50, 0, 600, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry[0])
			]

class viewsterGenreScreen(Screen):

	def __init__(self, session):
		self.session = session

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
			"red": self.keyCancel,
			"green": self.change_lang,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft,
			"nextBouquet" : self.keyPageUp,
			"prevBouquet" : self.keyPageDown
		}, -1)

		self.keyLocked = True
		self.language = "de"
		self['title'] = Label("viewster.com")
		self['ContentTitle'] = Label("Movies:")
		self['name'] = Label("")
		self['F1'] = Label("Exit")
		self['F2'] = Label(self.language)
		self['F3'] = Label("")
		self['F4'] = Label("")
		self['F1'].hide()
		self['F3'].hide()
		self['F4'].hide()
		self['coverArt'] = Pixmap()
		self['Page'] = Label("1")
		self['page'] = Label("")
		self['handlung'] = Label("")

		self.genreliste = []
		self.page = 1
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['liste'] = self.chooseMenuList

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.keyLocked = True
		url = "http://www.de.viewster.com/MovieList/Movies?page=%s&genreid=&language=%s&filter=NotSorted&avfilter=Free" % (str(self.page), self.language)
		print url, self.language
		getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.loadPageData).addErrback(self.dataError)

	def loadPageData(self, data):
		self['Page'].setText(str(self.page))
		movies = re.findall('<a href="(.*?)">.*?<img alt="(.*?)".*?src="(.*?)"', data, re.S)
		if movies:
			self.genreliste = []
			for (url, title, image) in movies:
				url = "http://%s.viewster.com%s" % (self.language, url)
				self.genreliste.append((title, url, image))
			self.chooseMenuList.setList(map(viewsterGenreListEntry, self.genreliste))
			self.keyLocked = False
			self.loadPic()

	def dataError(self, error):
		printl(error,self,"E")

	def change_lang(self):
		if self.language == "de":
			self.language = "en"
		elif self.language == "en":
			self.language = "es"
		elif self.language == "es":
			self.language = "fr"
		elif self.language == "fr":
			self.language = "de"

		self['F2'].setText(self.language)
		print "Sprache:", self.language
		self.loadPage()

	def keyOK(self):
		if self.keyLocked:
			return
		viewsterGenre = self['liste'].getCurrent()[0][0]
		viewsterUrl = self['liste'].getCurrent()[0][1]
		viewsterImage = self['liste'].getCurrent()[0][2]
		idx = self['liste'].getSelectedIndex()

		print idx, viewsterGenre, viewsterUrl
		self.session.open(viewsterPlayer, self.genreliste, int(idx))

	def loadPic(self):
		streamPic = self['liste'].getCurrent()[0][2]
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

	def keyCancel(self):
		self.close()

class viewsterPlayer(SimplePlayer):

	def __init__(self, session, playList, playIdx=0, playAll=True, listTitle=None, cover=True):
		print "viewsterPlayer:"

		SimplePlayer.__init__(self, session, playList, playIdx, playAll, listTitle, 'local', 0, cover)

		self.onLayoutFinish.append(self.getVideo)

	def getVideo(self):
		self.viewsterName = self.playList[self.playIdx][0]
		viewsterUrl = self.playList[self.playIdx][1]
		print self.viewsterName, viewsterUrl

		getPage(viewsterUrl, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.getStream).addErrback(self.dataError)

	def getStream(self, data):
		stream_url = re.findall("onclick=\"playTrailer.*?'(rtmpe://.*?)'", data, re.S)
		if stream_url:
			print stream_url[0]
			img = self.playList[self.playIdx][2]
			self.playStream(self.viewsterName, stream_url[0], imgurl=img)
