from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.simpleplayer import SimplePlayer
from Plugins.Extensions.MediaPortal.resources.coverhelper import CoverHelper

def kinokisteGenreListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 20, 0, 900, 25, 0, RT_HALIGN_CENTER | RT_VALIGN_CENTER, entry[0])
		]

class kinokisteGenreScreen(Screen):

	def __init__(self, session):
		self.session = session
		path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/%s/oldGenreScreen.xml" % config.mediaportal.skin.value
		if not fileExists(path):
			path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/original/oldGenreScreen.xml"
		print path
		with open(path, "r") as f:
			self.skin = f.read()
			f.close()

		Screen.__init__(self, session)

		self["actions"]  = ActionMap(["OkCancelActions", "ShortcutActions", "WizardActions", "ColorActions", "SetupActions", "NumberActions", "MenuActions"], {
			"ok"    : self.keyOK,
			"cancel": self.keyCancel
		}, -1)

		self['title'] = Label("KinoKiste")
		self['name'] = Label("Genre Auswahl")
		self['coverArt'] = Pixmap()

		self.genreliste = []
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['genreList'] = self.chooseMenuList

		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.genreliste.append(("Kinofilme", "http://kkiste.to/aktuelle-kinofilme/"))
		self.genreliste.append(("Serien", "http://kkiste.to/serien/"))
		self.genreliste.append(("Filmlisten", "http://kkiste.to/film-index/"))
		self.genreliste.append(("Genres", "http://kkiste.to/genres/"))
		self.genreliste.append(("Suche", "http://kkiste.to/search/?q="))

		self.chooseMenuList.setList(map(kinokisteGenreListEntry, self.genreliste))

	def keyOK(self):
		kkName = self['genreList'].getCurrent()[0][0]
		kkUrl = self['genreList'].getCurrent()[0][1]

		if kkName == "Kinofilme":
			self.session.open(kinokisteKinoScreen)
		elif kkName == "Serien":
			self.session.open(kinokisteSerienScreen)
		elif kkName == "Filmlisten":
			self.session.open(kinokisteFilmlistenScreen)
		elif kkName == "Genres":
			self.session.open(kinokisteGenrelistenScreen)
		else:
			self.session.openWithCallback(self.searchCallback, VirtualKeyBoard, title = (_("Suchbegriff eingeben")), text = "")
			
	def searchCallback(self, callbackStr):
		if callbackStr is not None:
			print callbackStr
			url = "http://kkiste.to/search/?q=%s" % callbackStr.replace(' ','%20')
			print url
			self.session.open(kinokisteSearchScreen, url)

	def keyCancel(self):
		self.close()

def kinokisteKinoListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 20, 0, 900, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry[0])
		]

class kinokisteKinoScreen(Screen):

	def __init__(self, session):
		self.session = session
		path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/%s/myVideoFilmScreen.xml" % config.mediaportal.skin.value
		if not fileExists(path):
			path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/original/myVideoFilmScreen.xml"
		print path
		with open(path, "r") as f:
			self.skin = f.read()
			f.close()

		Screen.__init__(self, session)

		self["actions"]  = ActionMap(["OkCancelActions", "ShortcutActions", "WizardActions", "ColorActions", "SetupActions", "NumberActions", "MenuActions", "EPGSelectActions"], {
			"ok" : self.keyOK,
			"cancel" : self.keyCancel,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft,
			"nextBouquet" : self.keyPageUp,
			"prevBouquet" : self.keyPageDown
		}, -1)

		self['title'] = Label("KinoKiste")
		self['name'] = Label("Film Auswahl")
		self['handlung'] = Label("")
		self['page'] = Label("")
		self['Pic'] = Pixmap()

		self.page = 1
		self.filmeliste = []
		self.keyLocked = True
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['List'] = self.chooseMenuList

		self.onLayoutFinish.append(self.loadpage)

	def loadpage(self):
		self.filmeliste = []
		url = "http://kkiste.to/aktuelle-kinofilme/?page=%s" % str(self.page)
		self['page'].setText(str(self.page))
		getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.filmData).addErrback(self.dataError)

	def filmData(self, data):
		kkDaten = re.findall('<a href="(.*?)" title="Jetzt (.*?) Stream ansehen" class="image">\n<img src="(.*?)"', data)
		if kkDaten:
			for (kkUrl,kkTitle,kkImage) in kkDaten:
				kkUrl = "http://www.kkiste.to%s" % kkUrl
				self.filmeliste.append((kkTitle, kkUrl, kkImage))
			self.chooseMenuList.setList(map(kinokisteKinoListEntry, self.filmeliste))
			self.keyLocked = False
			self.showInfos()

	def dataError(self, error):
		printl(error,self,"E")

	def showInfos(self):
		kkTitle = self['List'].getCurrent()[0][0]
		self['name'].setText(kkTitle)
		kkUrl = self['List'].getCurrent()[0][1]
		kkImage = self['List'].getCurrent()[0][2]
		kkImageUrl = "%s" % kkImage.replace('_170_120','_145_215')
		CoverHelper(self['Pic']).getCover(kkImageUrl)
		getPage(kkUrl, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.getDescription).addErrback(self.dataError)

	def getDescription(self, data):
		ddDescription = re.findall('<meta name="description" content="(.*?)"', data, re.S)
		if ddDescription:
			self['handlung'].setText(decodeHtml(ddDescription[0]))
		else:
			self['handlung'].setText("Keine Infos gefunden.")

	def keyOK(self):
		if self.keyLocked:
			return
		kkName = self['List'].getCurrent()[0][0]
		kkUrl = self['List'].getCurrent()[0][1]
		getPage(kkUrl, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.getParts).addErrback(self.dataError)

	def getParts(self, data):
		kkName = self['List'].getCurrent()[0][0]
		streams = re.findall('<a href="(http://www.ecostream.tv/stream/.*?)"', data, re.S)
		if streams:
			self.session.open(kinokistePartsScreen, streams, kkName)

	def keyPageDown(self):
		print "PageDown"
		if self.keyLocked:
			return
		if not self.page < 2:
			self.page -= 1
			self.loadpage()

	def keyPageUp(self):
		print "PageUP"
		if self.keyLocked:
			return
		self.page += 1
		self.loadpage()

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

	def keyCancel(self):
		self.close()

class kinokisteSerienScreen(Screen):

	def __init__(self, session):
		self.session = session
		path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/%s/myVideoFilmScreen.xml" % config.mediaportal.skin.value
		if not fileExists(path):
			path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/original/myVideoFilmScreen.xml"
		print path
		with open(path, "r") as f:
			self.skin = f.read()
			f.close()

		Screen.__init__(self, session)

		self["actions"]  = ActionMap(["OkCancelActions", "ShortcutActions", "WizardActions", "ColorActions", "SetupActions", "NumberActions", "MenuActions", "EPGSelectActions"], {
			"ok" : self.keyOK,
			"cancel" : self.keyCancel,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft,
			"nextBouquet" : self.keyPageUp,
			"prevBouquet" : self.keyPageDown
		}, -1)

		self['title'] = Label("KinoKiste - Serien Auswahl:")
		self['name'] = Label("")
		self['handlung'] = Label("")
		self['page'] = Label("")
		self['Pic'] = Pixmap()

		self.page = 1
		self.filmeliste = []
		self.keyLocked = True
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['List'] = self.chooseMenuList

		self.onLayoutFinish.append(self.loadpage)

	def loadpage(self):
		self.filmeliste = []
		url = "http://kkiste.to/serien/?page=%s" % str(self.page)
		self['page'].setText(str(self.page))
		getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.filmData).addErrback(self.dataError)

	def filmData(self, data):
		kkDaten = re.findall('<a href="(.*?)" title="Jetzt (.*?) Stream ansehen" class="image">\n<img src="(.*?)"', data)
		if kkDaten:
			for (kkUrl,kkTitle,kkImage) in kkDaten:
				kkUrl = "http://www.kkiste.to%s" % kkUrl
				self.filmeliste.append((kkTitle, kkUrl, kkImage))
			self.chooseMenuList.setList(map(kinokisteKinoListEntry, self.filmeliste))
			self.keyLocked = False
			self.showInfos()

	def dataError(self, error):
		printl(error,self,"E")

	def showInfos(self):
		kkTitle = self['List'].getCurrent()[0][0]
		self['name'].setText(kkTitle)
		kkUrl = self['List'].getCurrent()[0][1]
		kkImage = self['List'].getCurrent()[0][2]
		self.kkImageUrl = "%s" % kkImage.replace('_170_120','_145_215')
		CoverHelper(self['Pic']).getCover(self.kkImageUrl)
		getPage(kkUrl, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.getDescription).addErrback(self.dataError)

	def getDescription(self, data):
		ddDescription = re.findall('<meta name="description" content="(.*?)"', data, re.S)
		if ddDescription:
			self['handlung'].setText(decodeHtml(ddDescription[0]))
		else:
			self['handlung'].setText("Keine Infos gefunden.")

	def keyOK(self):
		if self.keyLocked:
			return
		kkName = self['List'].getCurrent()[0][0]
		kkUrl = self['List'].getCurrent()[0][1]
		
		print kkName, kkUrl
		self.session.open(kinokisteEpisodeScreen, kkName, kkUrl, self.kkImageUrl)

	def keyPageDown(self):
		print "PageDown"
		if self.keyLocked:
			return
		if not self.page < 2:
			self.page -= 1
			self.loadpage()

	def keyPageUp(self):
		print "PageUP"
		if self.keyLocked:
			return
		self.page += 1
		self.loadpage()

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

	def keyCancel(self):
		self.close()
		
class kinokisteEpisodeScreen(Screen):

	def __init__(self, session, serienName, serienUrl, serienPic):
		self.session = session
		self.serienName = serienName
		self.serienUrl = serienUrl
		self.serienPic = serienPic
		
		path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/%s/myVideoFilmScreen.xml" % config.mediaportal.skin.value
		if not fileExists(path):
			path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/original/myVideoFilmScreen.xml"
		print path
		with open(path, "r") as f:
			self.skin = f.read()
			f.close()

		Screen.__init__(self, session)

		self["actions"]  = ActionMap(["OkCancelActions", "ShortcutActions", "WizardActions", "ColorActions", "SetupActions", "NumberActions", "MenuActions", "EPGSelectActions"], {
			"ok" : self.keyOK,
			"cancel" : self.keyCancel
		}, -1)

		self['title'] = Label("KinoKiste- Episoden Auswahl:")
		self['name'] = Label(self.serienName)
		self['handlung'] = Label("")
		self['page'] = Label("")
		self['Pic'] = Pixmap()

		self.page = 1
		self.kekse = {}
		self.filmeliste = []
		self.keyLocked = True
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['List'] = self.chooseMenuList

		self.onLayoutFinish.append(self.loadpage)

	def loadpage(self):
		self.filmeliste = []
		CoverHelper(self['Pic']).getCover(self.serienPic)
		print self.serienUrl
		getPage(self.serienUrl, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.seasonData).addErrback(self.dataError)

	def seasonData(self, data):
		self.urlliste = []
		jsonLink = re.findall('<select class="seasonselect" data-movie="(.*?)"', data, re.S)
		if jsonLink:
			print jsonLink
			staffeln = re.findall('<option value="(.*\d)">Staffel.*?</option>', data)
			if staffeln:
				print staffeln
				staffeln.reverse()
				for staffel in staffeln:
					url = "http://kkiste.to/xhr/movies/episodes/%s" % jsonLink[0]
					print url, staffel
					self.urlliste.append((url, staffel))
					
		self.count = len(self.urlliste)
		self.counting = 0
		if len(self.urlliste) != 0:
			self.filmeliste = []
			print self.urlliste
			ds = defer.DeferredSemaphore(tokens=1)
			downloads = [ds.run(self.download,url,staffel).addCallback(self.showEpisodes).addErrback(self.dataError) for url,staffel in self.urlliste]
			finished = defer.DeferredList(downloads).addErrback(self.dataError)

	def download(self, url, staffel):
		print url, staffel
		self.counting += 1
		post = {'season': staffel}
		return getPage(url, method='POST', postdata=urlencode(post), headers={'Content-Type':'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest'})
	
	def showEpisodes(self, data):
		eps = re.findall('link":"(.*?)","part":"(.*?)"', data, re.S)
		if eps:
			for link, ep in eps:
				link = "http://www.ecostream.tv/stream/%s.html" % (link)
				zahl = re.findall('Season (.*\d), Episode (.*\d)', ep)
				if zahl:
					(eins, zwei) = zahl[0]
					self.filmeliste.append((ep, link, eins+zwei))

		if self.counting == self.count:
			self.filmeliste.sort(key=lambda x: int(x[2]))
			self.chooseMenuList.setList(map(kinokisteKinoListEntry, self.filmeliste))
			self.keyLocked = False

	def dataError(self, error):
		printl(error,self,"E")

	def keyOK(self):
		if self.keyLocked:
			return
		kkName = self['List'].getCurrent()[0][0]
		self.kkUrl = self['List'].getCurrent()[0][1]
		self.serienName2 = "%s - %s" % (self.serienName, kkName)
		print kkName, self.kkUrl
		getPage(self.kkUrl, cookies=self.kekse, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.eco_read).addErrback(self.dataError)
		
	def eco_read(self, data):
		print data
		print "hole daten"
		id = re.findall('<div id="play" data-id="(.*?)">', data, re.S)
		if id:
			postString = {'id': id[0]}
			print postString
			api_url = "http://www.ecostream.tv/xhr/video/get/"
			getPage(api_url, method='POST', cookies=self.kekse, postdata=urlencode(postString), headers={'Content-Type': 'application/x-www-form-urlencoded', 'Referer': self.kkUrl, 'X-Requested-With': 'XMLHttpRequest'}).addCallback(self.eco_data).addErrback(self.dataError)		

	def eco_data(self, data):
		print "hole stream"
		stream_url = re.findall('"url":"(.*?)"', data, re.S)
		if stream_url:
			print stream_url
			final_url = "http://www.ecostream.tv%s" % stream_url[0]
			print final_url
			self.session.open(SimplePlayer, [(self.serienName2, final_url, self.serienPic)], showPlaylist=False, ltype='kinokiste', cover=True)

	def keyCancel(self):
		self.close()

def kinokistePartsListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 20, 0, 900, 25, 0, RT_HALIGN_CENTER | RT_VALIGN_CENTER, entry[0])
		]

class kinokistePartsScreen(Screen):

	def __init__(self, session, parts, stream_name):
		self.session = session
		self.parts = parts
		self.stream_name = stream_name
		path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/%s/kinokistePartsScreen.xml" % config.mediaportal.skin.value
		if not fileExists(path):
			path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/original/kinokistePartsScreen.xml"
		print path
		with open(path, "r") as f:
			self.skin = f.read()
			f.close()

		Screen.__init__(self, session)

		self["actions"]  = ActionMap(["OkCancelActions", "ShortcutActions", "WizardActions", "ColorActions", "SetupActions", "NumberActions", "MenuActions"], {
			"ok"    : self.keyOK,
			"cancel": self.keyCancel
		}, -1)

		self['title'] = Label("KinoKiste")
		self['name'] = Label("Parts Auswahl")
		self['coverArt'] = Pixmap()

		self.genreliste = []
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['genreList'] = self.chooseMenuList
		self.keyLocked = False
		self.kekse = {}

		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		print self.parts
		self.parts = list(set(self.parts)) # remove dupes
		self.parts.sort() # sortieren
		self.count_disks = 0
		for part in self.parts:
			self.count_disks += 1
			partsName = "PART %s" % self.count_disks
			print partsName, part
			self.genreliste.append((partsName, part))

		self.chooseMenuList.setList(map(kinokistePartsListEntry, self.genreliste))

	def keyOK(self):
		if self.keyLocked:
			return
		self.kkLink = self['genreList'].getCurrent()[0][1]
		print self.kkLink
		self.keyLocked = True
		getPage(self.kkLink, cookies=self.kekse, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.eco_read).addErrback(self.dataError)
		
	def eco_read(self, data):
		print data
		print "hole daten"
		id = re.findall('<div id="play" data-id="(.*?)">', data, re.S)
		if id:
			postString = {'id': id[0]}
			print postString
			api_url = "http://www.ecostream.tv/xhr/video/get/"
			getPage(api_url, method='POST', cookies=self.kekse, postdata=urlencode(postString), headers={'Content-Type': 'application/x-www-form-urlencoded', 'Referer': self.kkLink, 'X-Requested-With': 'XMLHttpRequest'}).addCallback(self.eco_data).addErrback(self.dataError)		

	def eco_data(self, data):
		print "hole stream"
		stream_url = re.findall('"url":"(.*?)"', data, re.S)
		if stream_url:
			print stream_url
			final_url = "http://www.ecostream.tv%s" % stream_url[0]
			print final_url
			part = self['genreList'].getCurrent()[0][0]
			streamname = "%s - %s" % (self.stream_name, part)
			self.session.open(SimplePlayer, [(streamname, final_url)], showPlaylist=False, ltype='kinokiste')			

	def eco_final(self, data):
		part = self['genreList'].getCurrent()[0][0]
		stream_url = re.findall('flashvars="file=(.*?)&', data)
		if stream_url:
			kkStreamUrl = "http://www.ecostream.tv"+stream_url[0]+"&start=0"
			kkStreamUrl = urllib2.unquote(kkStreamUrl)
			print kkStreamUrl
			req = urllib2.Request(kkStreamUrl)
			res = urllib2.urlopen(req)
			finalurl = res.geturl()
			print finalurl
			streamname = "%s - %s" % (self.stream_name, part)
			self.session.open(SimplePlayer, [(streamname, finalurl)], showPlaylist=False, ltype='kinokiste')

	def dataError(self, error):
		printl(error,self,"E")

	def keyCancel(self):
		self.close()

def kinokisteFilmlistenListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 20, 0, 900, 25, 0, RT_HALIGN_CENTER | RT_VALIGN_CENTER, entry[0])
		]

class kinokisteFilmlistenScreen(Screen):

	def __init__(self, session):
		self.session = session
		path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/%s/oldGenreScreen.xml" % config.mediaportal.skin.value
		if not fileExists(path):
			path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/original/oldGenreScreen.xml"
		print path
		with open(path, "r") as f:
			self.skin = f.read()
			f.close()

		Screen.__init__(self, session)

		self["actions"]  = ActionMap(["OkCancelActions", "ShortcutActions", "WizardActions", "ColorActions", "SetupActions", "NumberActions", "MenuActions"], {
			"ok"    : self.keyOK,
			"cancel": self.keyCancel
		}, -1)

		self['title'] = Label("KinoKiste")
		self['name'] = Label("FilmListen Auswahl")
		self['coverArt'] = Pixmap()

		self.genreliste = []
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['genreList'] = self.chooseMenuList

		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		abc = ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z","0","1","2","3","4","5","6","7","8","9"]
		for letter in abc:
			kkLink = "http://kkiste.to/film-index/%s/" % letter
			self.genreliste.append((letter, kkLink))
		self.chooseMenuList.setList(map(kinokisteFilmlistenListEntry, self.genreliste))

	def keyOK(self):
		kkLink = self['genreList'].getCurrent()[0][1]
		print kkLink
		self.session.open(kinokisteFilmLetterScreen, kkLink)

	def keyCancel(self):
		self.close()
		
class kinokisteGenrelistenScreen(Screen):

	def __init__(self, session):
		self.session = session
		self.kkLink = "http://kkiste.to/genres/"
		path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/%s/oldGenreScreen.xml" % config.mediaportal.skin.value
		if not fileExists(path):
			path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/original/oldGenreScreen.xml"
		print path
		with open(path, "r") as f:
			self.skin = f.read()
			f.close()

		Screen.__init__(self, session)

		self["actions"]  = ActionMap(["OkCancelActions", "ShortcutActions", "WizardActions", "ColorActions", "SetupActions", "NumberActions", "MenuActions"], {
			"ok"    : self.keyOK,
			"cancel": self.keyCancel
		}, -1)

		self['title'] = Label("KinoKiste")
		self['name'] = Label("Genre Auswahl")
		self['coverArt'] = Pixmap()

		self.genreliste = []
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['genreList'] = self.chooseMenuList

		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.genreliste.append(("Abenteuer", "http://kkiste.to/abenteuer/"))
		self.genreliste.append(("Action", "http://kkiste.to/action/"))
		self.genreliste.append(("Animation", "http://kkiste.to/animation/"))
		self.genreliste.append(("Biographie", "http://kkiste.to/biographie/"))
		self.genreliste.append(("Bollywood", "http://kkiste.to/bollywood/"))
		self.genreliste.append(("Dokumentation", "http://kkiste.to/dokumentation/"))
		self.genreliste.append(("Drama", "http://kkiste.to/drama/"))
		self.genreliste.append(("Familie", "http://kkiste.to/familie/"))
		self.genreliste.append(("Fantasy", "http://kkiste.to/fantasy/"))
		self.genreliste.append(("Geschichte", "http://kkiste.to/geschichte/"))
		self.genreliste.append(("Horror", "http://kkiste.to/horror/"))
		self.genreliste.append(("Klassiker", "http://kkiste.to/klassiker/"))
		self.genreliste.append(("Komoedie", "http://kkiste.to/komoedie/"))	
		self.genreliste.append(("Kriegsfilm", "http://kkiste.to/kriegsfilm/"))
		self.genreliste.append(("Krimi", "http://kkiste.to/krimi/"))
		self.genreliste.append(("Musik", "http://kkiste.to/musik/"))
		self.genreliste.append(("Mystery", "http://kkiste.to/mystery/"))
		self.genreliste.append(("Romantik", "http://kkiste.to/romantik/"))
		self.genreliste.append(("Sci-Fi", "http://kkiste.to/sci-fi/"))		
		self.genreliste.append(("Sport", "http://kkiste.to/sport/"))
		self.genreliste.append(("Thriller", "http://kkiste.to/thriller/"))
		self.genreliste.append(("Western", "http://kkiste.to/western/"))
		
		self.chooseMenuList.setList(map(kinokisteGenreListEntry, self.genreliste))

	def keyOK(self):
		kkLink = self['genreList'].getCurrent()[0][1]
		print kkLink
		self.session.open(kinokisteInGenreScreen, kkLink)

	def keyCancel(self):
		self.close()
		
def kinokisteInGenreListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 20, 0, 500, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry[0])
		]

class kinokisteInGenreScreen(Screen):

	def __init__(self, session, kkLink):
		self.session = session
		self.kkLink = kkLink
		path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/%s/kinokisteFilmLetterScreen.xml" % config.mediaportal.skin.value
		if not fileExists(path):
			path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/original/kinokisteFilmLetterScreen.xml"
		print path
		with open(path, "r") as f:
			self.skin = f.read()
			f.close()

		Screen.__init__(self, session)

		self["actions"]  = ActionMap(["OkCancelActions", "ShortcutActions", "WizardActions", "ColorActions", "SetupActions", "NumberActions", "MenuActions", "EPGSelectActions"], {
			"ok" : self.keyOK,
			"cancel" : self.keyCancel,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft,
			"nextBouquet" : self.keyPageUp,
			"prevBouquet" : self.keyPageDown
		}, -1)

		self['title'] = Label("KinoKiste")
		self['name'] = Label("Film Auswahl")
		self['page'] = Label("1")
		self['handlung'] = Label("")
		self['coverArt'] = Pixmap()

		self.genreliste = []
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['genreList'] = self.chooseMenuList
		self.keyLocked = True
		self.page = 1

		self.onLayoutFinish.append(self.loadpage)

	def loadpage(self):
		self.genreliste = []
		self['page'].setText(str(self.page))
		kkLink = "%s?page=%s" % (self.kkLink, str(self.page))
		print kkLink
		getPage(kkLink, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.pageData).addErrback(self.dataError)

	def pageData(self, data):
		kkMovies = re.findall('<div class="mbox" >.*?<a href="(.*?)" title="Jetzt (.*?) Stream ansehen".*?<img src="(.*?)"', data, re.S)
		if kkMovies:
			for (kkUrl,kkTitle,kkImage) in kkMovies:
				kkUrl = "http://kkiste.to%s" % kkUrl
				self.genreliste.append((kkTitle, kkUrl, kkImage))
			self.chooseMenuList.setList(map(kinokisteInGenreListEntry, self.genreliste))
			self.keyLocked = False
			self.showInfos()

	def dataError(self, error):
		printl(error,self,"E")

	def showInfos(self):
		kkTitle = self['genreList'].getCurrent()[0][0]
		self['name'].setText(kkTitle)
		kkUrl = self['genreList'].getCurrent()[0][1]
		kkImage = self['genreList'].getCurrent()[0][2]
		kkImageUrl = "%s" % kkImage.replace('_170_120','_145_215')
		CoverHelper(self['coverArt']).getCover(kkImageUrl)
		getPage(kkUrl, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.getDescription).addErrback(self.dataError)

	def getDescription(self, data):
		ddDescription = re.findall('<meta name="description" content="(.*?)"', data, re.S)
		if ddDescription:
			self['handlung'].setText(decodeHtml(ddDescription[0]))
		else:
			self['handlung'].setText("Keine Infos gefunden.")
					
	def keyPageDown(self):
		print "PageDown"
		if self.keyLocked:
			return
		if not self.page < 2:
			self.page -= 1
			self.loadpage()

	def keyPageUp(self):
		print "PageUP"
		if self.keyLocked:
			return
		self.page += 1
		self.loadpage()

	def keyLeft(self):
		if self.keyLocked:
			return
		self['genreList'].pageUp()
		self.showInfos()

	def keyRight(self):
		if self.keyLocked:
			return
		self['genreList'].pageDown()
		self.showInfos()

	def keyUp(self):
		if self.keyLocked:
			return
		self['genreList'].up()
		self.showInfos()

	def keyDown(self):
		if self.keyLocked:
			return
		self['genreList'].down()
		self.showInfos()

	def keyOK(self):
		if self.keyLocked:
			return
		kkLink = self['genreList'].getCurrent()[0][1]
		print kkLink
		getPage(kkLink, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.getParts).addErrback(self.dataError)

	def getParts(self, data):
		kkName = self['genreList'].getCurrent()[0][0]
		streams = re.findall('<a href="(http://www.ecostream.tv/stream/.*?)"', data, re.S)
		print streams
		if streams:
			self.session.open(kinokistePartsScreen, streams, kkName)

	def keyCancel(self):
		self.close()

def kinokisteFilmLetterListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 20, 0, 500, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry[0]),
		(eListboxPythonMultiContent.TYPE_TEXT, 520, 0, 150, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry[1]),
		(eListboxPythonMultiContent.TYPE_TEXT, 670, 0, 150, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry[2])
		]

class kinokisteFilmLetterScreen(Screen):

	def __init__(self, session, kkLink):
		self.session = session
		self.kkLink = kkLink
		path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/%s/kinokisteFilmLetterScreen.xml" % config.mediaportal.skin.value
		if not fileExists(path):
			path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/original/kinokisteFilmLetterScreen.xml"
		print path
		with open(path, "r") as f:
			self.skin = f.read()
			f.close()

		Screen.__init__(self, session)

		self["actions"]  = ActionMap(["OkCancelActions", "ShortcutActions", "WizardActions", "ColorActions", "SetupActions", "NumberActions", "MenuActions", "EPGSelectActions"], {
			"ok" : self.keyOK,
			"cancel" : self.keyCancel,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft,
			"nextBouquet" : self.keyPageUp,
			"prevBouquet" : self.keyPageDown
		}, -1)

		self['title'] = Label("KinoKiste")
		self['name'] = Label("Film Auswahl")
		self['page'] = Label("1")
		self['handlung'] = Label("")
		self['coverArt'] = Pixmap()

		self.genreliste = []
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['genreList'] = self.chooseMenuList
		self.keyLocked = True
		self.page = 1

		self.onLayoutFinish.append(self.loadpage)

	def loadpage(self):
		self.genreliste = []
		self['page'].setText(str(self.page))
		kkLink = "%s?page=%s" % (self.kkLink, str(self.page))
		print kkLink
		getPage(kkLink, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.pageData).addErrback(self.dataError)

	def pageData(self, data):
		kkMovies = re.findall('<li class="mbox list".*?<a href="(.*?)" title="Jetzt (.*?) Stream ansehen".*?<p class="year">(.*?)</p>\n<p class="genre">(.*?)</p>', data, re.S)
		if kkMovies:
			for (kkUrl,kkTitle,kkYear,kkGenre) in kkMovies:
				kkUrl = "http://kkiste.to%s" % kkUrl
				self.genreliste.append((kkTitle, kkYear, kkGenre, kkUrl))
			self.chooseMenuList.setList(map(kinokisteFilmLetterListEntry, self.genreliste))
			self.keyLocked = False
			self.loadpage2()

	def loadpage2(self):
		kkLink = self['genreList'].getCurrent()[0][3]
		getPage(kkLink, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.showInfos).addErrback(self.dataError)	
		
	def showInfos(self, data):
		ddDescription = re.findall('<meta name="description" content="(.*?)"', data, re.S)
		kkCover = re.findall('<img src="(.*?)".*?alt=".*?>', data, re.S)
		if ddDescription:
			self['handlung'].setText(decodeHtml(ddDescription[0]))
		else:
			self['handlung'].setText("Keine Infos gefunden.")
		kkImage = kkCover[0]
		kkImageUrl = "%s" % kkImage.replace('_170_120','_145_215')
		CoverHelper(self['coverArt']).getCover(kkImageUrl)
		
	def dataError(self, error):
		printl(error,self,"E")

	def keyPageDown(self):
		print "PageDown"
		if self.keyLocked:
			return
		if not self.page < 2:
			self.page -= 1
			self.loadpage()

	def keyPageUp(self):
		print "PageUP"
		if self.keyLocked:
			return
		self.page += 1
		self.loadpage()
		
	def keyLeft(self):
		if self.keyLocked:
			return
		self['genreList'].pageUp()
		self.loadpage2()

	def keyRight(self):
		if self.keyLocked:
			return
		self['genreList'].pageDown()
		self.loadpage2()

	def keyUp(self):
		if self.keyLocked:
			return
		self['genreList'].up()
		self.loadpage2()

	def keyDown(self):
		if self.keyLocked:
			return
		self['genreList'].down()
		self.loadpage2()

	def keyOK(self):
		if self.keyLocked:
			return
		kkLink = self['genreList'].getCurrent()[0][3]
		print kkLink
		getPage(kkLink, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.getParts).addErrback(self.dataError)

	def getParts(self, data):
		kkName = self['genreList'].getCurrent()[0][0]
		streams = re.findall('<a href="(http://www.ecostream.tv/stream/.*?)"', data, re.S)
		print streams
		if streams:
			self.session.open(kinokistePartsScreen, streams, kkName)

	def keyCancel(self):
		self.close()
		
class kinokisteSearchScreen(Screen):

	def __init__(self, session, kkLink):
		self.session = session
		self.kkLink = kkLink
		path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/%s/kinokisteFilmLetterScreen.xml" % config.mediaportal.skin.value
		if not fileExists(path):
			path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/original/kinokisteFilmLetterScreen.xml"
		print path
		with open(path, "r") as f:
			self.skin = f.read()
			f.close()

		Screen.__init__(self, session)

		self["actions"]  = ActionMap(["OkCancelActions", "ShortcutActions", "WizardActions", "ColorActions", "SetupActions", "NumberActions", "MenuActions", "EPGSelectActions"], {
			"ok" : self.keyOK,
			"cancel" : self.keyCancel
		}, -1)

		self['title'] = Label("KinoKiste - Search")
		self['name'] = Label("Film Auswahl")
		self['page'] = Label("")
		self['handlung'] = Label("")
		self['coverArt'] = Pixmap()

		self.genreliste = []
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['genreList'] = self.chooseMenuList
		self.keyLocked = True

		self.onLayoutFinish.append(self.loadpage)

	def loadpage(self):
		self.genreliste = []
		print self.kkLink
		getPage(self.kkLink, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.pageData).addErrback(self.dataError)

	def pageData(self, data):
		kkMovies = re.findall('<li class="mbox list".*?<a href="(.*?)" title="Jetzt (.*?) Stream ansehen".*?<p class="year">(.*?)</p>\n<p class="genre">(.*?)</p>', data, re.S)
		if kkMovies:
			for (kkUrl,kkTitle,kkYear,kkGenre) in kkMovies:
				kkUrl = "http://kkiste.to%s" % kkUrl
				self.genreliste.append((kkTitle, kkYear, kkGenre, kkUrl))
			self.chooseMenuList.setList(map(kinokisteFilmLetterListEntry, self.genreliste))
			self.keyLocked = False

	def dataError(self, error):
		printl(error,self,"E")

	def keyOK(self):
		if self.keyLocked:
			return
		kkLink2 = self['genreList'].getCurrent()[0][3]
		print kkLink2
		getPage(kkLink2, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.getParts).addErrback(self.dataError)

	def getParts(self, data):
		kkName = self['genreList'].getCurrent()[0][0]
		streams = re.findall('<a href="(http://www.ecostream.tv/stream/.*?)"', data, re.S)
		print streams
		if streams:
			self.session.open(kinokistePartsScreen, streams, kkName)

	def keyCancel(self):
		self.close()
