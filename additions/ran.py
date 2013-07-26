from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.simpleplayer import SimplePlayer

def ranListEntry(entry):
	#TYPE_TEXT, x, y, width, height, fnt, flags, string [, color, backColor, backColorSelected, borderWidth, borderColor])
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 50, 0, 200, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry[0]),
		(eListboxPythonMultiContent.TYPE_TEXT, 250, 0, 550, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry[1])
		]

class ranGenreScreen(Screen):

	def __init__(self, session):
		self.session = session

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
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft,
			"nextBouquet" : self.keyPageUp,
			"prevBouquet" : self.keyPageDown
		}, -1)

		self.keyLocked = True
		self['title'] = Label("ran.de")
		self['ContentTitle'] = Label("Alle Sport Videos:")
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
		self.page = 0
		self.genreliste = []
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['liste'] = self.chooseMenuList

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.keyLocked = True
		self['Page'].setText(str(self.page)+ " von")
		url = "http://www.ran.de/videoclip-categoryclips.html?conId=ajxVid579060&cat=102&page=%s" % str(self.page)
		print url
		getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.loadPageData).addErrback(self.dataError)

	def loadPageData(self, data):
		print "drin"
		self.genreliste = []
		lastpage = re.findall('class="page pageEn">(.*?)</span>', data)
		if lastpage:
			self['page'].setText(lastpage[-1])
		match = re.findall('<img src="(.*?)".*?title="(.*?)".*?<div class="cat">(.*?)</div><h3><a href=".*?-(\d+).html"', data, re.S)
		if match:
			for image,title,cat,id in match:
				url = "http://ws.vtc.sim-technik.de/video/video.jsonp?clipid=%s" % id
				image = "http://www.ran.de%s" % image
				self.genreliste.append((decodeHtml(cat.replace('Champions League','CL')),decodeHtml(title),url,image))
			self.chooseMenuList.setList(map(ranListEntry, self.genreliste))
			self.keyLocked = False
			self.loadPic()

	def dataError(self, error):
		printl(error,self,"E")

	def loadPic(self):
		streamPic = self['liste'].getCurrent()[0][3]
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

	def keyOK(self):
		if self.keyLocked:
			return
		ranUrl = self['liste'].getCurrent()[0][2]
		print ranUrl
		self.keyLocked = True
		getPage(ranUrl, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.getStream).addErrback(self.dataError)

	def getStream(self, data):
		stream_url = re.findall('VideoURL":"(.*?)"', data, re.S)
		if stream_url:
			ranCat = self['liste'].getCurrent()[0][0]
			ranTitle = self['liste'].getCurrent()[0][1]
			ranName = "%s: %s" % (ranCat, ranTitle)
			self.keyLocked = False
			stream_url = stream_url[0].replace('\\','')
			self.session.open(SimplePlayer, [(ranName, stream_url)], showPlaylist=False, ltype='ran')
		else:
			message = self.session.open(MessageBox, _("Video not found!"), MessageBox.TYPE_INFO, timeout=5)

	def keyCancel(self):
		self.close()