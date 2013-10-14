from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.decrypt import *
from Plugins.Extensions.MediaPortal.resources.simpleplayer import SimplePlayer
from Plugins.Extensions.MediaPortal.resources.coverhelper import CoverHelper

def pornhubGenreListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 20, 0, 900, 25, 0, RT_HALIGN_CENTER | RT_VALIGN_CENTER, entry[0])
		]

def pornhubFilmListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 20, 0, 900, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry[0])
		]

def pornhubPlayListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 20, 0, 450, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry[0]),
		(eListboxPythonMultiContent.TYPE_TEXT, 610, 0, 290, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, "Videos: " + entry[1])
		]

def pornhubPornstarListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 20, 0, 140, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, "Rank: " + entry[3]),
		(eListboxPythonMultiContent.TYPE_TEXT, 150, 0, 450, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry[0]),
		(eListboxPythonMultiContent.TYPE_TEXT, 610, 0, 290, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, "Videos: " + entry[4])
		]

class pornhubGenreScreen(Screen):

	def __init__(self, session):
		self.session = session
		path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/%s/XXXGenreScreen.xml" % config.mediaportal.skin.value
		if not fileExists(path):
			path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/original/XXXGenreScreen.xml"
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
			"left" : self.keyLeft
		}, -1)

		self['title'] = Label("Pornhub.com")
		self['name'] = Label("Genre Auswahl")
		self['coverArt'] = Pixmap()
		self.keyLocked = True
		self.suchString = ''

		self.filmliste = []
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['genreList'] = self.chooseMenuList

		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.keyLocked = True
		url = "http://www.pornhub.com/categories"
		getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.genreData).addErrback(self.dataError)

	def genreData(self, data):
		phCats = re.findall('<div\sclass="category-wrapper">.*?<a\shref="(/video\?c=.*?)"><img\ssrc="(.*?)".*?alt="(.*?)"', data, re.S)
		if phCats:
			for (phUrl, phImage, phTitle) in phCats:
				phUrl = "http://www.pornhub.com" + phUrl + "&page="
				self.filmliste.append((phTitle, phUrl, phImage))
			self.filmliste.sort()
			self.filmliste.insert(0, ("Playlists - Most Favorited", "http://www.pornhub.com/playlists?o=mf&page=", None))
			self.filmliste.insert(0, ("Playlists - Top Rated", "http://www.pornhub.com/playlists?page=", None))
			self.filmliste.insert(0, ("Playlists - Most Viewed", "http://www.pornhub.com/playlists?o=mv&page=", None))
			self.filmliste.insert(0, ("Playlists - Most Recent", "http://www.pornhub.com/playlists?o=mr&page=", None))
			self.filmliste.insert(0, ("Pornstars", "http://www.pornhub.com/pornstars?page=", None))
			self.filmliste.insert(0, ("HD", "http://www.pornhub.com/video?c=38&page=", 'http://cdn1a.static.pornhub.phncdn.com/images/categories/38.jpg'))
			self.filmliste.insert(0, ("Longest", "http://www.pornhub.com/video?o=lg&page=", None))
			self.filmliste.insert(0, ("Top Rated", "http://www.pornhub.com/video?o=tr&page=", None))
			self.filmliste.insert(0, ("Most Viewed", "http://www.pornhub.com/video?o=mv&page=", None))
			self.filmliste.insert(0, ("Most Recent", "http://www.pornhub.com/video?o=mr&page=", None))
			self.filmliste.insert(0, ("--- Search ---", "callSuchen", None))
			self.chooseMenuList.setList(map(pornhubGenreListEntry, self.filmliste))
			self.chooseMenuList.moveToIndex(0)
			self.keyLocked = False
			self.showInfos()

	def dataError(self, error):
		printl(error,self,"E")

	def showInfos(self):
		phImage = self['genreList'].getCurrent()[0][2]
		if not phImage == None:
			CoverHelper(self['coverArt']).getCover(phImage)

	def keyOK(self):
		if self.keyLocked:
			return
		streamGenreName = self['genreList'].getCurrent()[0][0]
		if streamGenreName == "--- Search ---":
			self.suchen()
		elif streamGenreName == "Pornstars":
			streamGenreLink = self['genreList'].getCurrent()[0][1]
			self.session.open(pornhubPornstarScreen, streamGenreLink)
		elif re.match("Playlists", streamGenreName):
			streamGenreLink = self['genreList'].getCurrent()[0][1]
			self.session.open(pornhubPlayListScreen, streamGenreLink)
		else:
			streamGenreLink = self['genreList'].getCurrent()[0][1]
			self.session.open(pornhubFilmScreen, streamGenreLink)

	def suchen(self):
		self.session.openWithCallback(self.SuchenCallback, VirtualKeyBoard, title = (_("Suchkriterium eingeben")), text = self.suchString)

	def SuchenCallback(self, callback = None, entry = None):
		if callback is not None and len(callback):
			self.suchString = callback.replace(' ', '%2B')
			streamGenreLink = 'http://www.pornhub.com/video/search?search=%s&page=' % (self.suchString)
			self.session.open(pornhubFilmScreen, streamGenreLink)

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

	def keyCancel(self):
		self.close()

class pornhubPlayListScreen(Screen):

	def __init__(self, session, streamGenreLink):
		self.session = session
		self.Link = streamGenreLink
		path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/%s/XXXFilmScreen.xml" % config.mediaportal.skin.value
		if not fileExists(path):
			path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/original/XXXFilmScreen.xml"
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
			"prevBouquet" : self.keyPageDown,
			"green" : self.keyPageNumber
		}, -1)

		self['title'] = Label("Pornhub.com")
		self['name'] = Label("Playlists")
		self['views'] = Label("")
		self['runtime'] = Label("")
		self['page'] = Label("1")
		self['coverArt'] = Pixmap()
		self.keyLocked = True
		self.page = 1

		self.filmliste = []
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['genreList'] = self.chooseMenuList

		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.filmliste = []
		self.keyLocked = True
		url = self.Link + str(self.page)
		getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.loadpage).addErrback(self.dataError)

	def loadpage(self, data):
		phCats = re.findall('class="playlist-videos.*?<span>(.*?)</span>.*?src="(.*?)".*?class="title".*?href="(.*?)">(.*?)</a>', data, re.S)
		if phCats:
			for phVideos, phImage, phUrl, phTitle in phCats:
				phUrl = "http://www.pornhub.com" + phUrl
				self.filmliste.append((decodeHtml(phTitle), phVideos, phImage, phUrl))
			self.chooseMenuList.setList(map(pornhubPlayListEntry, self.filmliste))
			self.chooseMenuList.moveToIndex(0)
			self.keyLocked = False
			self.showInfos()
			self['page'].setText(str(self.page))

	def dataError(self, error):
		printl(error,self,"E")

	def showInfos(self):
		phImage = self['genreList'].getCurrent()[0][2]
		CoverHelper(self['coverArt']).getCover(phImage)

	def keyOK(self):
		phCatLink = self['genreList'].getCurrent()[0][3]
		self.session.open(pornhubFilmScreen, phCatLink)

	def keyPageNumber(self):
		self.session.openWithCallback(self.callbackkeyPageNumber, VirtualKeyBoard, title = (_("Seitennummer eingeben")), text = str(self.page))

	def callbackkeyPageNumber(self, answer):
		if answer is not None:
			answer = re.findall('\d+', answer)
		else:
			return
		if answer:
			self.page = int(answer[0])
			self.layoutFinished()

	def keyPageDown(self):
		print "PageDown"
		if self.keyLocked:
			return
		if not self.page < 2:
			self.page -= 1
			self.layoutFinished()

	def keyPageUp(self):
		print "PageUP"
		if self.keyLocked:
			return
		self.page += 1
		self.layoutFinished()

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

	def keyCancel(self):
		self.close()

class pornhubPornstarScreen(Screen):

	def __init__(self, session, streamGenreLink):
		self.session = session
		self.Link = streamGenreLink
		path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/%s/XXXFilmScreen.xml" % config.mediaportal.skin.value
		if not fileExists(path):
			path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/original/XXXFilmScreen.xml"
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
			"prevBouquet" : self.keyPageDown,
			"green" : self.keyPageNumber
		}, -1)

		self['title'] = Label("Pornhub.com")
		self['name'] = Label("Pornstars")
		self['views'] = Label("")
		self['runtime'] = Label("")
		self['page'] = Label("1")
		self['coverArt'] = Pixmap()
		self.keyLocked = True
		self.page = 1

		self.filmliste = []
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['genreList'] = self.chooseMenuList

		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.filmliste = []
		self.keyLocked = True
		url = self.Link + str(self.page)
		getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.loadpage).addErrback(self.dataError)

	def loadpage(self, data):
		parse = re.search('class="section_title">Most\sPopular\sPornstars(.*)', data, re.S)
		phCats = re.findall('rank_number">(.*?)<.*?src="(.*?)".*?href="(.*?)".*?class="title".*?>(.*?)<.*?videosNumber">(.*?)\sVideos</span>', parse.group(1), re.S)
		if phCats:
			for phRank, phImage, phUrl, phTitle, phVideos in phCats:
				phUrl = phUrl + "?page="
				self.filmliste.append((decodeHtml(phTitle), phUrl, phImage, phRank, phVideos))
			self.chooseMenuList.setList(map(pornhubPornstarListEntry, self.filmliste))
			self.chooseMenuList.moveToIndex(0)
			self.keyLocked = False
			self.showInfos()
			self['page'].setText(str(self.page))

	def dataError(self, error):
		printl(error,self,"E")

	def showInfos(self):
		phImage = self['genreList'].getCurrent()[0][2]
		CoverHelper(self['coverArt']).getCover(phImage)

	def keyOK(self):
		phCatLink = self['genreList'].getCurrent()[0][1]
		self.session.open(pornhubFilmScreen, phCatLink)

	def keyPageNumber(self):
		self.session.openWithCallback(self.callbackkeyPageNumber, VirtualKeyBoard, title = (_("Seitennummer eingeben")), text = str(self.page))

	def callbackkeyPageNumber(self, answer):
		if answer is not None:
			answer = re.findall('\d+', answer)
		else:
			return
		if answer:
			self.page = int(answer[0])
			self.layoutFinished()

	def keyPageDown(self):
		print "PageDown"
		if self.keyLocked:
			return
		if not self.page < 2:
			self.page -= 1
			self.layoutFinished()

	def keyPageUp(self):
		print "PageUP"
		if self.keyLocked:
			return
		self.page += 1
		self.layoutFinished()

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

	def keyCancel(self):
		self.close()

class pornhubFilmScreen(Screen):

	def __init__(self, session, phCatLink):
		self.session = session
		self.phCatLink = phCatLink
		path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/%s/XXXFilmScreen.xml" % config.mediaportal.skin.value
		if not fileExists(path):
			path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/original/XXXFilmScreen.xml"
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
			"prevBouquet" : self.keyPageDown,
			"green" : self.keyPageNumber
		}, -1)

		self['title'] = Label("Pornhub.com")
		self['name'] = Label("Genre Auswahl")
		self['views'] = Label("")
		self['runtime'] = Label("")
		self['page'] = Label("1")
		self['coverArt'] = Pixmap()
		self.keyLocked = True
		self.page = 1

		self.filmliste = []
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['genreList'] = self.chooseMenuList

		self.onLayoutFinish.append(self.loadpage)

	def loadpage(self):
		self.keyLocked = True
		self['name'].setText('Bitte warten...')
		self.filmliste = []
		self['page'].setText(str(self.page))
		if re.match(".*\/playlist\/",self.phCatLink):
			url = "%s" % (self.phCatLink)
		else:
			url = "%s%s" % (self.phCatLink, str(self.page))
		print url
		getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.genreData).addErrback(self.dataError)

	def genreData(self, data):
		phMovies = re.findall('<div\sclass="wrap">.*?<a\shref="(.*?)".*?\stitle="(.*?)".*?data-mediumthumb="(.*?)".*?<var\sclass="duration">(.*?)</var>.*?<span\sclass="views"><var>(.*?)<.*?<var\sclass="added">(.*?)<', data, re.S)
		if phMovies:
			for (phUrl, phTitle, phImage, phRuntime, phViews, phAdded) in phMovies:
				self.filmliste.append((decodeHtml(phTitle), phUrl, phImage, phRuntime, phViews, phAdded))
			self.chooseMenuList.setList(map(pornhubFilmListEntry, self.filmliste))
			self.chooseMenuList.moveToIndex(0)
			self.keyLocked = False
			self.showInfos()

	def dataError(self, error):
		printl(error,self,"E")

	def showInfos(self):
		phTitle = self['genreList'].getCurrent()[0][0]
		phImage = self['genreList'].getCurrent()[0][2]
		phRuntime = self['genreList'].getCurrent()[0][3]
		phViews = self['genreList'].getCurrent()[0][4]
		phAdded = self['genreList'].getCurrent()[0][5]
		self['name'].setText(phTitle)
		self['views'].setText(phViews)
		self['runtime'].setText(phRuntime)
		CoverHelper(self['coverArt']).getCover(phImage)

	def keyOK(self):
		if self.keyLocked:
			return
		phTitle = self['genreList'].getCurrent()[0][0]
		phLink = self['genreList'].getCurrent()[0][1]
		getPage(phLink, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.parseData).addErrback(self.dataError)

	def keyPageNumber(self):
		self.session.openWithCallback(self.callbackkeyPageNumber, VirtualKeyBoard, title = (_("Seitennummer eingeben")), text = str(self.page))

	def callbackkeyPageNumber(self, answer):
		if answer is not None:
			answer = re.findall('\d+', answer)
		else:
			return
		if answer:
			self.page = int(answer[0])
			self.loadpage()

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

	def parseData(self, data):
		phTitle = self['genreList'].getCurrent()[0][0]
		match = re.compile('"video_url":"([^"]+)"').findall(data)
		if not match:
			match = re.compile('"quality_720p":"([^"]+)"').findall(data)
		if not match:
			match = re.compile('"quality_480p":"([^"]+)"').findall(data)
		if not match:
			match = re.compile('"quality_240p":"([^"]+)"').findall(data)
		fetchurl = match
		fetchurl = urllib2.unquote(match[0])
		match = re.compile('"video_title":"([^"]+)"').findall(data)
		title = urllib.unquote_plus(match[0])
		phStream = decrypt(fetchurl, title, 256)
		if phStream:
			self.session.open(SimplePlayer, [(phTitle, phStream)], showPlaylist=False, ltype='pornhub')

	def keyCancel(self):
		self.close()