#
# ARD-Mediathek von chroma_key
#
from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.playrtmpmovie import PlayRtmpMovie
from Plugins.Extensions.MediaPortal.resources.simpleplayer import SimplePlayer

def ARDGenreListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 20, 0, 900, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry[0])
		]

def ARDFilmListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 20, 0, 900, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry[0])
		]

class ARDGenreScreen(Screen):

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

		self['title'] = Label("ARD Mediathek")
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
		self.genreliste = []
		for c in xrange(26):
			self.genreliste.append((chr(ord('A') + c), None))
		self.genreliste.insert(0, ('0-9', None))
		self.chooseMenuList.setList(map(ARDGenreListEntry, self.genreliste))
		self.keyLocked = False

	def dataError(self, error):
		printl(error,self,"E")

	def keyOK(self):
		if self.keyLocked:
			return
		streamGenreLink = self['List'].getCurrent()[0][0]
		self.session.open(ARDSubGenreScreen, streamGenreLink)

	def keyLeft(self):
		self['List'].pageUp()

	def keyRight(self):
		self['List'].pageDown()

	def keyUp(self):
		self['List'].up()

	def keyDown(self):
		self['List'].down()

	def keyCancel(self):
		self.close()

class ARDSubGenreScreen(Screen):

	def __init__(self, session, streamGenreLink):
		self.session = session
		self.streamGenreLink = streamGenreLink
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

		self['title'] = Label("ARD Mediathek")
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
		# chroma_key: Beispiel-URL fuer Smartphones... http://m.ardmediathek.de/Sendungen-A-Z?pageId=13932746 .... Auf der koennte man zwar wesentlich leichter aufbauen, da man hier auch die hoechste Qualitaet leichter
		# er-parsen kann, aber leider werden auch deutlich weniger Clips hierfuer gehostet ..... Beispiel... http://m.ardmediathek.de/coldmirror?docId=10017896&pageId=13932914
		# chroma_key: Der RSS-Feed ist super, hat scheinbar gleichviele Treffer wie die hier verwendeten Links, und hat dafuer sogar ausfuehrliche Inhaltsangaben (Metadaten, die bei dem, hier Verwendeten
		# fehlen) doch leider fehlt den RSS-Feeds ein Vorschau-Bildchen, sowie die Duration.....Beispiel...  url = "http://www.ardmediathek.de/export/rss/id=10017896" (id ist die docId)
		# chroma_key: URL fuer eine spaetere, einzubauende Suchfunktion (wenn man zb nach "coca cola" suchen wuerde)... http://www.ardmediathek.de/suche?s=coca+cola
		self.keyLocked = True
		url = "http://www.ardmediathek.de/ard/servlet/ajax-cache/3474820/view=list/initial=%s/index.html" % (self.streamGenreLink)
		getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.loadPageData).addErrback(self.dataError)

	def loadPageData(self, data):
		sendungen = re.findall('<img src="(.*?)".*?<a href=".*?documentId=(.*?)".*?data-xtclib=".*?">\n\s+(.*?)\n\s+</a>.*?<span class="mt-count">(.*?)</span>.*?<span class="mt-channel">(.*?)</span>', data, re.S)
		if sendungen:
			for (image,id,title,ausgaben,sender) in sendungen:
				image = image.replace('bild-xs16x9','bild-s16x9')
				image = "http://www.ardmediathek.de%s" % image
				url = "http://www.ardmediathek.de/ard/servlet/ajax-cache/3516962/view=list/documentId=%s" %id
				zusatzinfo = "%s - %s" % (sender,ausgaben)
				self.genreliste.append((decodeHtml(title),url,image,zusatzinfo))
		else:
			self.genreliste.append(('Keine Sendungen mit diesem Buchstaben vorhanden.', None, None, None))
		self.chooseMenuList.setList(map(ARDGenreListEntry, self.genreliste))
		self.keyLocked = False
		self.loadPic()

	def dataError(self, error):
		printl(error,self,"E")

	def loadPic(self):
		streamPic = self['List'].getCurrent()[0][2]
		if streamPic == None:
			return
		streamName = self['List'].getCurrent()[0][0]
		self['name'].setText(streamName)
		streamHandlung = self['List'].getCurrent()[0][3]
		self['handlung'].setText(streamHandlung)
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
		if streamGenreLink == None:
			return
		self.session.open(ARDFilmeListeScreen, streamGenreLink)

	def keyLeft(self):
		if self.keyLocked:
			return
		self['List'].pageUp()
		self.loadPic()

	def keyRight(self):
		if self.keyLocked:
			return
		self['List'].pageDown()
		self.loadPic()

	def keyUp(self):
		if self.keyLocked:
			return
		self['List'].up()
		self.loadPic()

	def keyDown(self):
		if self.keyLocked:
			return
		self['List'].down()
		self.loadPic()

	def keyCancel(self):
		self.close()

class ARDFilmeListeScreen(Screen):

	def __init__(self, session, streamGenreLink):
		self.session = session
		self.streamGenreLink = streamGenreLink
		path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/%s/RTLnowGenreScreen.xml" % config.mediaportal.skin.value
		if not fileExists(path):
			path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/original/RTLnowGenreScreen.xml"
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
			"prevBouquet" : self.keyPageDown
			}, -1)

		self['title'] = Label("ARD Mediathek")
		self['name'] = Label("Folgen Auswahl")
		self['handlung'] = Label("")
		self['Pic'] = Pixmap()
		self.page = 1
		self.keyLocked = True
		self.filmliste = []
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['List'] = self.chooseMenuList

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		url = "%s/goto=%s" % (self.streamGenreLink,self.page)
		getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.loadPageData).addErrback(self.dataError)

	def dataError(self, error):
		printl(error,self,"E")

	def loadPageData(self, data):
		self.filmliste = []
		seiten = re.findall('<option selected="selected".*?goto=(.*?)/.*?<span>(.*?)</span>', data, re.S)
		if seiten:
			for (a,b) in seiten:
				seite = "Seite:\t%s%s" % (a,b)
		else:
			seite = "Seite:\t1 von 1"
		folgen = re.findall('img src="(.*?)".*?<a href="(.*?)".*?xtclib=".*?">(.*?)</a>.*?aus: (.*?)</p>.*?"mt-airtime">(.*?)</span>.*?>(.*?)</span>', data, re.S)
		if folgen:
			for (image,url,title,sendung,airtime,sender) in folgen:
				image = image.replace('bild-s16x9','bild-m16x9')
				image = "http://www.ardmediathek.de%s" % image
				if airtime:
					if len(airtime) == 0:
						date = "Keine Angabe"
						dur = "Keine Angabe"
				if len(airtime) == 8:
					date = "%s" % (airtime)
					dur = "Keine Angabe"
				else:
					date = airtime[:8]
					dur = airtime[9:]
				handlung = "Sendung:\t%s\nClip vom:\t%s\nBroadcaster:\t%s\nDauer:\t>> %s <<\n\n%s" % (decodeHtml(sendung),date,sender,dur,seite)
				self.filmliste.append((decodeHtml(title),url,handlung,image))
		else:
			self.filmliste.append(('Keine Folgen gefunden.', None, None, None))
		self.chooseMenuList.setList(map(ARDFilmListEntry, self.filmliste))
		self.keyLocked = False
		self.loadPic()

	def loadPic(self):
		streamPic = self['List'].getCurrent()[0][3]
		if streamPic == None:
			return
		streamName = self['List'].getCurrent()[0][0]
		self['name'].setText(streamName)
		streamHandlung = self['List'].getCurrent()[0][2]
		self['handlung'].setText(streamHandlung)
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
		self.streamName = self['List'].getCurrent()[0][0]
		self['name'].setText("Bitte warten...")
		self.keyLocked = True
		id = self['List'].getCurrent()[0][1]
		if id == None:
			return
		url = "http://www.ardmediathek.de%s" % id
		print url
		getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.get_Link).addErrback(self.dataError)

	def dataError(self, error):
		printl(error,self,"E")

	def get_Link(self, data):
		qualitycheck = re.findall('mediaCollection.addMediaStream\((.*?),\s+(.*?),\s+"(.*?)",\s+"(.*?)",.*?\)', data, re.S)
		if qualitycheck:
			Q0P = ""
			Q1P = ""
			Q2P = ""
			Q3P = ""
			for (a,b,c,d) in qualitycheck:
				if int(a+b) >= 30:
					if d[-4:] == ".mp4":
						Q3H = c
						Q3P = d
				elif int(a+b) >= 20:
					if d[-4:] == ".mp4":
						Q2H = c
						Q2P = d
				elif int(a+b) >= 10:
					if d[-4:] == ".mp4":
						Q1H = c
						Q1P = d
				elif int(a+b) >= 0:
					if re.search(".mp4", d, re.S):
						Q0H = c
						Q0P = d

			if len(Q0P) > 0:
				if "flashmedia.radiobremen.de" in Q0H:
					host = Q0H.split('mediabase/')[0]
					playpath1 = Q0H.split('/mediabase/')[1]
					playpath2 = Q0P[4:]
					playpath = "mp4:mediabase/" + playpath1 + "/" + playpath2
				else:
					host = Q0H
					playpath = Q0P
			elif len(Q3P) > 0:
				host = Q3H
				playpath = Q3P
			elif len(Q2P) > 0:
				host = Q2H
				playpath = Q2P
			elif len(Q1P) > 0:
				host = Q1H
				playpath = Q1P

			#
			# Broadcaster erkennen. Derzeit nur fuer SWR und SR.
			#
			ard = "mvideos.daserste.de"
			br = "cdn-storage.br.de"
			hr = "www.hr.gl-systemhaus.de"
			mdr = "x4100mp4"
			ndr = "media.ndr.de"
			rb = "httpmedia.radiobremen.de"
			rbb = "http-stream.rbb-online.de"
			sr = "sr.fcod"
			swr = "ios-ondemand.swr.de"
			ts = "media.tagesschau.de"
			wdr = "http-ras.wdr.de"
			#

			self.keyLocked = False
			self['name'].setText("Folgen Auswahl")

			playpath = playpath.replace('&amp;','&')
			print "HOST: " + host
			print "PLAYPATH: " + playpath
			if (host[0:4] == 'rtmp' and config.mediaportal.useRtmpDump.value):
				final = "%s' --playpath=%s'" % (host, playpath)
				movieinfo = [final,self.streamName]
				self.session.open(PlayRtmpMovie, movieinfo, self.streamName)
			elif host[0:4] == 'rtmp':
				final = "%s playpath=%s" % (host, playpath)
				playlist = []
				playlist.append((self.streamName, final))
				self.session.open(SimplePlayer, playlist, showPlaylist=False, ltype='ard')
			else:
				playlist = []
				playlist.append((self.streamName, playpath))
				self.session.open(SimplePlayer, playlist, showPlaylist=False, ltype='ard')


	def keyLeft(self):
		if self.keyLocked:
			return
		self['List'].pageUp()
		self.loadPic()

	def keyRight(self):
		if self.keyLocked:
			return
		self['List'].pageDown()
		self.loadPic()

	def keyUp(self):
		if self.keyLocked:
			return
		self['List'].up()
		self.loadPic()

	def keyDown(self):
		if self.keyLocked:
			return
		self['List'].down()
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

	def keyCancel(self):
		self.close()