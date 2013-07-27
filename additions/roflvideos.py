from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.simpleplayer import SimplePlayer

def auswahlListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 20, 0, 900, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry[0])
		]

class roflScreen(Screen):

	def __init__(self, session):
		self.session = session
		path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/%s/roflScreen.xml" % config.mediaportal.skin.value
		if not fileExists(path):
			path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/original/roflScreen.xml"
		print path
		with open(path, "r") as f:
			self.skin = f.read()
			f.close()

		Screen.__init__(self, session)

		self["actions"]  = ActionMap(["OkCancelActions", "ShortcutActions", "WizardActions", "ColorActions", "SetupActions", "NumberActions", "MenuActions", "EPGSelectActions"], {
			"ok"    : self.keyOK,
			"cancel": self.keyCancel,
			"up"    : self.keyUp,
			"down"  : self.keyDown,
			"left"  : self.keyLeft,
			"right" : self.keyRight,
			"nextBouquet" : self.keyPageUp,
			"prevBouquet" : self.keyPageDown
		}, -1)

		self.keyLocked = True
		self.page = 1
		self['title'] = Label("Rofl.to")
		self['roflPic'] = Pixmap()
		self['name'] = Label("")
		self['page'] = Label("1")
		self.roflListe = []
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['roflList'] = self.chooseMenuList

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.keyLocked = True
		url = "http://clips.rofl.to/new-clips/week/%s" % str(self.page)
		getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.loadPageData).addErrback(self.dataError)

	def loadPageData(self, data):
		roflVideos = re.findall('class="container.*?<a\shref="(http://clips.rofl.to/clip/.*?)"\srel="nofollow"\stitle=".*?"><img\ssrc="(http://media.rofl.to/clipshots/.*?)".*?alt="(.*?)"\s/>', data)
		if roflVideos:
			self.roflListe = []
			for roflUrl,roflPic,roflName in roflVideos:
				self.roflListe.append((decodeHtml(roflName), roflUrl, roflPic))
			self.chooseMenuList.setList(map(auswahlListEntry, self.roflListe))
			self.showPic()
			self.keyLocked = False

	def dataError(self, error):
		printl(error,self,"E")

	def showPic(self):
		roflPicLink = self['roflList'].getCurrent()[0][2]
		roflName = self['roflList'].getCurrent()[0][0]
		self['name'].setText(roflName)
		self['page'].setText(str(self.page))
		downloadPage(roflPicLink, "/tmp/roflPic.jpg").addCallback(self.roflCoverShow)

	def roflCoverShow(self, data):
		if fileExists("/tmp/roflPic.jpg"):
			self['roflPic'].instance.setPixmap(gPixmapPtr())
			self.scale = AVSwitch().getFramebufferScale()
			self.picload = ePicLoad()
			size = self['roflPic'].instance.size()
			self.picload.setPara((size.width(), size.height(), self.scale[0], self.scale[1], False, 1, "#FF000000"))
			if self.picload.startDecode("/tmp/roflPic.jpg", 0, 0, False) == 0:
				ptr = self.picload.getData()
				if ptr != None:
					self['roflPic'].instance.setPixmap(ptr)
					self['roflPic'].show()
					del self.picload

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
		self['roflList'].pageUp()
		self.showPic()

	def keyRight(self):
		if self.keyLocked:
			return
		self['roflList'].pageDown()
		self.showPic()

	def keyUp(self):
		if self.keyLocked:
			return
		self['roflList'].up()
		self.showPic()

	def keyDown(self):
		if self.keyLocked:
			return
		self['roflList'].down()
		self.showPic()

	def keyOK(self):
		if self.keyLocked:
			return
		roflURL = self['roflList'].getCurrent()[0][1]
		print roflURL
		getPage(roflURL, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.parseData).addErrback(self.dataError)

	def parseData(self, data):
		print data
		roflName = self['roflList'].getCurrent()[0][0]
		roflLink = re.findall('id="video-player".*?href="(.*?.flv)"', data, re.S)
		if roflLink:
			self.session.open(SimplePlayer, [(roflName, roflLink[0])], showPlaylist=False, ltype='roflto')

	def keyCancel(self):
		self.close()