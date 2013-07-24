from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.playrtmpmovie import PlayRtmpMovie
from Plugins.Extensions.MediaPortal.resources.simpleplayer import SimplePlayer

def SRFGenreListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 20, 0, 900, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry[0])
		]

def SRFFilmListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 20, 0, 900, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry[0])
		]

class SRFGenreScreen(Screen):

	def __init__(self, session):
		self.session = session
		path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/%s/RTLnowGenreScreen.xml" % config.mediaportal.skin.value
		if not fileExists(path):
			path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/original/RTLnowGenreScreen.xml"
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
			"left" : self.keyLeft
		}, -1)

		self['title'] = Label("SRF Player")
		self['name'] = Label("Auswahl der Sendung")
		self['handlung'] = Label("")
		self['Pic'] = Pixmap()

		self.genreliste = []
		self.keyLocked = True
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['List'] = self.chooseMenuList

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.keyLocked = True
		url = "http://www.srf.ch/player/tv/sendungen?displayedKey=Alle"
		getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.loadPageData).addErrback(self.dataError)

	def loadPageData(self, data):
		sendungen = re.findall('<img\sclass="az_thumb"\ssrc="(.*?)"\swidth="\d+"\sheight="\d+"\salt="(.*?)"\s/></a><h3><a\sclass="sendung_name"\shref="(/player/tv/.*?)">.*?</a></h3>.*?az_description">(.*?)</p>', data, re.S)
		if sendungen:
			self.genreliste = []
			for (image, title, url, handlung) in sendungen:
				url = "http://www.srf.ch%s" % url
				image = image.replace("width=144","width=320")
				self.genreliste.append((decodeHtml(title), url, image, handlung))
			self.genreliste.sort()
			self.chooseMenuList.setList(map(SRFGenreListEntry, self.genreliste))
			self.keyLocked = False
			self.loadPic()

	def dataError(self, error):
		printl(error,self,"E")

	def loadPic(self):
		streamName = self['List'].getCurrent()[0][0]
		self['name'].setText(streamName)
		streamHandlung = self['List'].getCurrent()[0][3]
		self['handlung'].setText(decodeHtml(streamHandlung))
		streamPic = self['List'].getCurrent()[0][2]
		downloadPage(streamPic, "/tmp/Icon.jpg").addCallback(self.ShowCover)

	def ShowCover(self, picData):
		if fileExists("/tmp/Icon.jpg"):
			self['Pic'].instance.setPixmap(gPixmapPtr())
			self.scale = AVSwitch().getFramebufferScale()
			self.picload = ePicLoad()
			size = self['Pic'].instance.size()
			self.picload.setPara((size.width(), size.height(), self.scale[0], self.scale[1], False, 1, "#FF000000"))
			if self.picload.startDecode("/tmp/Icon.jpg", 0, 0, False) == 0:
				ptr = self.picload.getData()
				if ptr != None:
					self['Pic'].instance.setPixmap(ptr)
					self['Pic'].show()
					del self.picload

	def keyOK(self):
		if self.keyLocked:
			return
		streamGenreLink = self['List'].getCurrent()[0][1]
		self.session.open(SRFFilmeListeScreen, streamGenreLink)

	def dataError(self, error):
		printl(error,self,"E")

	def keyLeft(self):
		self['List'].pageUp()
		self.loadPic()

	def keyRight(self):
		self['List'].pageDown()
		self.loadPic()

	def keyUp(self):
		self['List'].up()
		self.loadPic()

	def keyDown(self):
		self['List'].down()
		self.loadPic()

	def keyCancel(self):
		self.close()

class SRFFilmeListeScreen(Screen):

	def __init__(self, session, streamGenreLink):
		self.session = session
		self.streamGenreLink = streamGenreLink
		path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/%s/RTLnowFilmeScreen.xml" % config.mediaportal.skin.value
		if not fileExists(path):
			path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/original/RTLnowFilmeScreen.xml"
		print path
		with open(path, "r") as f:
			self.skin = f.read()
			f.close()

		Screen.__init__(self, session)

		self["actions"]  = ActionMap(["OkCancelActions", "ShortcutActions", "WizardActions", "ColorActions", "SetupActions", "NumberActions", "MenuActions", "EPGSelectActions"], {
			"ok"    : self.keyOK,
			"cancel": self.keyCancel
		}, -1)

		self['title'] = Label("SRF Player")
		self['name'] = Label("Folgen Auswahl")

		self.keyLocked = True
		self.filmliste = []
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['List'] = self.chooseMenuList

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		getPage(self.streamGenreLink, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.loadPageData).addErrback(self.dataError)

	def dataError(self, error):
		printl(error,self,"E")

	def loadPageData(self, data):
		self.filmliste = []
		folgen = re.findall('<h2\sclass="title"><a\stitle="(.*?)"\salt=".*?"\shref=".*?id=(.*?)"', data, re.S)
		if folgen:
			for (title, id) in folgen:
				url = "http://www.srf.ch/webservice/cvis/segment/%s/.json?nohttperr=1;omit_video_segments_validity=1;omit_related_segments=1;nearline_data=1" % id
				self.filmliste.append((decodeHtml(title), url))
			self.chooseMenuList.setList(map(SRFFilmListEntry, self.filmliste))
			self.keyLocked = False

	def keyOK(self):
		if self.keyLocked:
			return
		streamName = self['List'].getCurrent()[0][0]
		url = self['List'].getCurrent()[0][1]
		getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.get_xml).addErrback(self.dataError)

	def get_xml(self, data):
		if re.search('geoblock', data, re.S):
			message = self.session.open(MessageBox, _("Aus rechtlichen Gruenden steht dieses Video nur innerhalb der Schweiz zur Verfuegung."), MessageBox.TYPE_INFO, timeout=5)
			return
		xml = re.findall('"url":"(rtmp:.*?)"', data, re.S)
		if xml:
			url = xml[0].replace("\/","/")
			host = url.split('mp4:')[0]
			playpath = url.split('mp4:')[1]
		title = self['List'].getCurrent()[0][0]
		if config.mediaportal.useRtmpDump.value:
			final = "%s' --swfVfy=1 --playpath=mp4:%s --swfUrl=http://www.srf.ch/player/flash/srfplayer.swf'" % (host, playpath)
			movieinfo = [final,title]
			self.session.open(PlayRtmpMovie, movieinfo, title)
		else:
			final = "%s swfUrl=http://www.srf.ch/player/flash/srfplayer.swf playpath=mp4:%s swfVfy=1" % (host, playpath)
			print final
			playlist = []
			playlist.append((title, final))
			self.session.open(SimplePlayer, playlist, showPlaylist=False, ltype='srf')

	def keyCancel(self):
		self.close()