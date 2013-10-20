# -*- coding: utf-8 -*-
from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.simpleplayer import SimplePlayer
from Plugins.Extensions.MediaPortal.resources.coverhelper import CoverHelper

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
		sendungen = re.findall('<img\sclass="az_thumb.*?data-src2x="(.*?)".*?alt="(.*?)"\s/></a><h3><a\sclass="sendung_name"\shref="(/player/tv/.*?)">.*?</a></h3>.*?az_description">(.*?)</p>', data, re.S)
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
		CoverHelper(self['Pic']).getCover(streamPic)

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
		folgen = re.findall('<h3\sclass="title">(.*?)</h3>.*?<a\shref=".*?id=(.*?)">', data, re.S)
		if folgen:
			for (title, id) in folgen:
				url = "http://www.srf.ch/webservice/cvis/segment/%s/.json?nohttperr=1;omit_video_segments_validity=1;omit_related_segments=1;nearline_data=1" % id
				self.filmliste.append((decodeHtml(title), url))
		else:
			self.filmliste.append(("Keine Sendungen gefunden.",None))
		self.chooseMenuList.setList(map(SRFFilmListEntry, self.filmliste))
		self.keyLocked = False

	def keyOK(self):
		if self.keyLocked:
			return
		url = self['List'].getCurrent()[0][1]
		if url == None:
			return
		getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.get_xml).addErrback(self.dataError)

	def get_xml(self, data):
		master = re.findall('"streaming":"hls","quality":".*?","url":"(.*?)"}', data, re.S)
		if master:
			url = master[-1].replace("\/","/")
			getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.get_master).addErrback(self.dataError)

	def get_master(self, data):
		xml = re.findall('CODECS="avc.*?"\n(.*?)\n', data, re.S)
		if xml:
			if re.search('http://.*?', xml[-1], re.S):
				url = xml[-1]
				title = self['List'].getCurrent()[0][0]
				playlist = []
				playlist.append((title, url))
				self.session.open(SimplePlayer, playlist, showPlaylist=False, ltype='srf')
			else:
				url = self['List'].getCurrent()[0][1]
				getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.get_rtmp).addErrback(self.dataError)

	def get_rtmp(self, data):
		xml = re.findall('"url":"(rtmp:.*?)"', data, re.S)
		if xml:
			url = xml[0].replace("\/","/")
			host = url.split('mp4:')[0]
			playpath = url.split('mp4:')[1]
			title = self['List'].getCurrent()[0][0]
			final = "%s swfUrl=http://www.srf.ch/player/flash/srfplayer.swf playpath=mp4:%s swfVfy=1" % (host, playpath)
			playlist = []
			playlist.append((title, final))
			self.session.open(SimplePlayer, playlist, showPlaylist=False, ltype='srf')
		else:
			message = self.session.open(MessageBox, _("Aus rechtlichen Gründen steht dieses Video nur innerhalb der Schweiz zur Verfügung."), MessageBox.TYPE_INFO, timeout=5)
			return

	def keyCancel(self):
		self.close()