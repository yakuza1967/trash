from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.simpleplayer import SimplePlayer

def galileovlGenreListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 50, 0, 800, 25, 0, RT_HALIGN_CENTER | RT_VALIGN_CENTER, entry[0])
		]

def galileovlListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 50, 0, 800, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry[0])
		]

class galileovlGenreScreen(Screen):

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
		self['title'] = Label("Galileo-Videolexikon.de")
		self['ContentTitle'] = Label("Auswahl:")
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
		self.genreliste = [('Neueste Videos',"http://www.galileo-videolexikon.de/catalog/galileo/clips/mode/latest/t/"),
							('Suche',"http://www.galileo-videolexikon.de/catalog/galileo/clips/")]

		self.chooseMenuList.setList(map(galileovlGenreListEntry, self.genreliste))
		self.keyLocked = False

	def keyOK(self):
		if self.keyLocked:
			return
		self.galileovlName = self['genreList'].getCurrent()[0][0]
		galileovlUrl = self['genreList'].getCurrent()[0][1]
		print self.galileovlName, galileovlUrl

		if self.galileovlName == "Neueste Videos":
			self.session.open(galileovlListeScreen, self.galileovlName, galileovlUrl)
		else:
			self.session.openWithCallback(self.captchaCallback, VirtualKeyBoard, title = (_("Suche:")), text = "")

	def captchaCallback(self, callback = None, entry = None):
		if callback != None or callback != "":
			print callback
			url = "http://www.galileo-videolexikon.de/catalog/galileo/clips/%s" % callback
			print url
			self.session.open(galileovlListeScreen, self.galileovlName, url)

	def keyCancel(self):
		self.close()

class galileovlListeScreen(Screen):

	def __init__(self, session, galileovlName, galileovlUrl):
		self.session = session
		self.galileovlName = galileovlName
		self.galileovlUrl = galileovlUrl

		self.plugin_path = mp_globals.pluginPath
		self.skin_path =  mp_globals.pluginPath + "/skins"

		path = "%s/%s/defaultListWideScreen.xml" % (self.skin_path, config.mediaportal.skin.value)
		if not fileExists(path):
			path = self.skin_path + "/original/defaultListWideScreen.xml"

		with open(path, "r") as f:
			self.skin = f.read()
			f.close()

		Screen.__init__(self, session)

		self["actions"]  = ActionMap(["OkCancelActions", "ShortcutActions", "WizardActions", "ColorActions", "SetupActions", "NumberActions", "MenuActions", "EPGSelectActions"], {
			"ok"    : self.keyOK,
			"cancel": self.keyCancel,
			"red": self.keyCancel,
			"up": self.keyUp,
			"down": self.keyDown,
			"right": self.keyRight,
			"left": self.keyLeft,
		}, -1)

		self.keyLocked = True
		self['title'] = Label("Galileo-Videolexikon.de")
		self['ContentTitle'] = Label("Videos - %s" % self.galileovlName)
		self['name'] = Label("")
		self['F1'] = Label("Exit")
		self['F2'] = Label("")
		self['F3'] = Label("")
		self['F4'] = Label("")
		self['F3'].hide()
		self['F4'].hide()
		self['handlung'] = Label("")
		self['page'] = Label("")
		self['Page'] = Label("")
		self['coverArt'] = Pixmap()

		self.videoliste = []
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['liste'] = self.chooseMenuList

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		print "hole daten"
		getPage(self.galileovlUrl, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.loadPageData).addErrback(self.dataError)

	def loadPageData(self, data):
		self.videoliste = []
		videos = re.findall('"id":"(.*?)".*?"assestid":"(.*?)".*?"title":"(.*?)".*?"serie":"(.*?)".*?"description":"(.*?)".*?"duration":"(.*?)"', data, re.S )
		if videos:
			for (id, videoid, title, date, desc, dur) in videos:
				#print id, videoid, title, date, desc, dur
				title = "%s - %s" % (date, title)
				image = "http://www.prosieben.de/dynamic/h264/thumbnails/?res=high&app=galileo&ClipID=%s" % videoid
				self.videoliste.append((decodeHtml(title), videoid, desc, image))

			self.chooseMenuList.setList(map(galileovlListEntry, self.videoliste))
			self.loadPic()
			self.keyLocked = False

	def loadPic(self):
		streamPic = self['liste'].getCurrent()[0][3]
		handlung = self['liste'].getCurrent()[0][2]
		self['handlung'].setText(decodeHtml(handlung))
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
		self.galileovltitle = self['liste'].getCurrent()[0][0]
		self.galileovlid = self['liste'].getCurrent()[0][1]
		self.imageurl = self['liste'].getCurrent()[0][3]
		self.idx = self['liste'].getSelectedIndex()
		print self.galileovltitle, self.galileovlid

		url = "http://ws.vtc.sim-technik.de/video/video.jsonp?method=1&type=1&app=GalVidLex_web&clipid=%s" % self.galileovlid
		print url
		getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.get_link).addErrback(self.dataError)

	def get_link(self, data):
		stream_url = re.findall('"VideoURL":"(.*?)"', data, re.S)
		if stream_url:
			stream_url = stream_url[0].replace('\\','')
			print stream_url
			self.session.open(SimplePlayer, [(self.galileovltitle, stream_url, self.imageurl)], showPlaylist=False, ltype='galileovl')

	def dataError(self, error):
		printl(error,self,"E")

	def keyCancel(self):
		self.close()