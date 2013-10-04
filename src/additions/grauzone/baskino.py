from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.simpleplayer import SimplePlayer
from Plugins.Extensions.MediaPortal.resources.coverhelper import CoverHelper

def baskinoMainListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 20, 0, 860, 25, 0, RT_HALIGN_LEFT, entry[0])
		]

class baskino(Screen):
	def __init__(self, session):
		self.session = session
		path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/%s/kinderKinoScreen.xml" % config.mediaportal.skin.value
		if not fileExists(path):
			path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/original/kinderKinoScreen.xml"
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

		self['title'] = Label("Baskino.com")
		self['Pic'] = Pixmap()
		self['page'] = Label("1")
		self['name'] = Label("Choose a Movie")

		self.streamList = []
		self.streamMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.streamMenuList.l.setFont(0, gFont('mediaportal', 24))
		self.streamMenuList.l.setItemHeight(25)
		self['List'] = self.streamMenuList

		self.keyLocked = False
		self.page = 1
		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.keyLocked = True
		url = "http://baskino.com/new/page/%s/" % str(self.page)
		getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.parseData).addErrback(self.dataError)

	def parseData(self, data):
		movies = re.findall('<div class="postcover">.*?<a href="(.*?)">.*?<img title="(.*?)" src="(.*?)"', data, re.S)
		if movies:
			self.streamList = []
			for (url,title,image) in movies:
				self.streamList.append((decodeHtml(title), url, image))
			self.streamMenuList.setList(map(baskinoMainListEntry, self.streamList))
		self.keyLocked = False
		self.showInfos()

	def dataError(self, error):
		printl(error,self,"E")

	def showInfos(self):
		self['page'].setText("%s" % str(self.page))
		coverUrl = self['List'].getCurrent()[0][2]
		self.filmName = self['List'].getCurrent()[0][0]
		self['name'].setText(self.filmName) 
		ImageUrl = "%s" % coverUrl.replace('_170_120','_145_215')
		CoverHelper(self['Pic']).getCover(ImageUrl)

	def keyOK(self):
		exist = self['List'].getCurrent()
		if self.keyLocked or exist == None:
			return
		url = self['List'].getCurrent()[0][1]
		print url
		getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.parseVideo).addErrback(self.dataError)

	def parseVideo(self, data):
		video = re.findall('file:"(.*?)"', data, re.S)
		if video:
			print video
			self.session.open(SimplePlayer, [(self.filmName, video[0])], showPlaylist=False, ltype='baskino')
		else:
			message = self.session.open(MessageBox, _("No Stream Found."), MessageBox.TYPE_INFO, timeout=3)

	def keyLeft(self):
		if self.keyLocked:
			return
		self['List'].pageUp()
		self.showInfos()

	def keyRight(self):
		if self.keyLocked:
			return
		self['List'].pageDown()
		self.showInfos()

	def keyUp(self):
		if self.keyLocked:
			return
		self['List'].up()
		self.showInfos()

	def keyDown(self):
		if self.keyLocked:
			return
		self['List'].down()
		self.showInfos()

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

	def keyCancel(self):
		self.close()
