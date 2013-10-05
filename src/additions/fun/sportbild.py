from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.simpleplayer import SimplePlayer
from Plugins.Extensions.MediaPortal.resources.coverhelper import CoverHelper

def sportBildListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 20, 0, 900, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry[0])
		]

class sportBildScreen(Screen):

	def __init__(self, session):
		self.session = session
		path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/%s/sportBildScreen.xml" % config.mediaportal.skin.value
		if not fileExists(path):
			path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/original/sportBildScreen.xml"
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
		self.page = 0
		self['title'] = Label("SportBild.de")
		self['Pic'] = Pixmap()
		self['name'] = Label("")
		self['page'] = Label("1")
		self['runtime'] = Label("")
		self['date'] = Label("")
		self.spListe = []
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['List'] = self.chooseMenuList

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.keyLocked = True
		url = "http://sportbild.bild.de/SPORT/video/clip/video-home/teaser-alle-videos,templateId=renderVideoChannelList,page=%s,rootDocumentId=13275342.html" % str(self.page)
		print url
		getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.loadPageData).addErrback(self.dataError)

	def loadPageData(self, data):
		spVideos = re.findall('<a href="(/SPORT/video.*?)" target="btobody"><img src="(.*?.jpg)".*?<div class="bdeVideoDachzeile">(.*?)</div>.*?<div class="bdeVideoTeaser11 bdeVideoTime">(.*?)</div>.*?<div class="bdeVideoTeaser11 bdeVideoDate">(.*?)</div>', data, re.S)
		print spVideos
		if spVideos:
			self.spListe = []
			for (spUrl,spImage,spTitle,spRuntime,spDate) in spVideos:
				spImage = "http://sportbild.bild.de" + spImage
				self.spListe.append((decodeHtml(spTitle), spUrl, spImage, spRuntime, spDate))
			self.chooseMenuList.setList(map(sportBildListEntry, self.spListe))
			self.keyLocked = False
			self.showPic()

	def dataError(self, error):
		printl(error,self,"E")

	def showPic(self):
		spTitle = self['List'].getCurrent()[0][0]
		spPicLink = self['List'].getCurrent()[0][2]
		spRuntime = self['List'].getCurrent()[0][3]
		spDate = self['List'].getCurrent()[0][4]
		self['name'].setText(spTitle)
		self['page'].setText(str(self.page))
		self['date'].setText(spDate)
		self['runtime'].setText(spRuntime)
		ImageUrl = "%s" % spPicLink
		CoverHelper(self['Pic']).getCover(ImageUrl)

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
		self['List'].pageUp()
		self.showPic()

	def keyRight(self):
		if self.keyLocked:
			return
		self['List'].pageDown()
		self.showPic()

	def keyUp(self):
		if self.keyLocked:
			return
		self['List'].up()
		self.showPic()

	def keyDown(self):
		if self.keyLocked:
			return
		self['List'].down()
		self.showPic()

	def keyOK(self):
		if self.keyLocked:
			return
		spUrl = self['List'].getCurrent()[0][1]
		spUrl = re.sub('seite=.*?html','templateId=renderJavaScript,layout=17,startvideo=true.js',spUrl)
		url = "http://sportbild.bild.de" + spUrl
		print url
		getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.parseData).addErrback(self.dataError)

	def parseData(self, data):
		spTitle = self['List'].getCurrent()[0][0]
		spStream = re.findall('src="(http://.*?[mp4|flv])"', data, re.S)
		if spStream:
			print spStream
			self.session.open(SimplePlayer, [(spTitle, spStream[0])], showPlaylist=False, ltype='sportbild')

	def keyCancel(self):
		self.close()