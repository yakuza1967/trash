from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.decrypt import *
from Plugins.Extensions.MediaPortal.resources.simpleplayer import SimplePlayer
from Plugins.Extensions.MediaPortal.resources.coverhelper import CoverHelper

def tube8GenreListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 20, 0, 900, 25, 0, RT_HALIGN_CENTER | RT_VALIGN_CENTER, entry[0])
		]

def tube8FilmListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 20, 0, 900, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry[0])
		]

def tube8PlayListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 20, 0, 450, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry[0]),
		(eListboxPythonMultiContent.TYPE_TEXT, 610, 0, 290, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, "Videos: " + entry[1])
		]

def tube8PornstarListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 20, 0, 140, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, "Rank: " + entry[3]),
		(eListboxPythonMultiContent.TYPE_TEXT, 150, 0, 450, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry[0]),
		(eListboxPythonMultiContent.TYPE_TEXT, 610, 0, 290, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, "Videos: " + entry[4])
		]

class tube8GenreScreen(Screen):

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
			"cancel" : self.keyCancel
		}, -1)

		self['title'] = Label("Tube8.com")
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
		url = "http://www.tube8.com/categories.html"
		getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.genreData).addErrback(self.dataError)

	def genreData(self, data):
		parse = re.search('id="categories-wrapper"(.*?)</div>', data,re.S)
		phCats = re.findall("href='http://www.tube8.com/(.*?)'.*?Chosen.*?>(.*?)</a>", parse.group(1), re.S)
		if phCats:
			for (phUrl, phTitle) in phCats:
				phUrl = "http://www.tube8.com/" + phUrl + "page/"
				self.filmliste.append((phTitle, phUrl))
			self.filmliste.sort()
			self.filmliste.insert(0, ("Longest", "http://www.tube8.com/longest/page/"))
			self.filmliste.insert(0, ("Most Voted", "http://www.tube8.com/most-voted/page/"))
			self.filmliste.insert(0, ("Most Discussed", "http://www.tube8.com/most-discussed/page/"))
			self.filmliste.insert(0, ("Most Favorited", "http://www.tube8.com/most-favorited/page/"))
			self.filmliste.insert(0, ("Top Rated", "http://www.tube8.com/top/page/"))
			self.filmliste.insert(0, ("Most Viewed", "http://www.tube8.com/most-viewed/page/"))
			self.filmliste.insert(0, ("Newest", "http://www.tube8.com/newest/page/"))
			self.filmliste.insert(0, ("--- Search ---", "callSuchen"))
			self.chooseMenuList.setList(map(tube8GenreListEntry, self.filmliste))
			self.chooseMenuList.moveToIndex(0)
			self.keyLocked = False

	def dataError(self, error):
		printl(error,self,"E")

	def keyOK(self):
		if self.keyLocked:
			return
		streamGenreName = self['genreList'].getCurrent()[0][0]
		if streamGenreName == "--- Search ---":
			self.suchen()
		else:
			streamGenreLink = self['genreList'].getCurrent()[0][1]
			self.session.open(tube8FilmScreen, streamGenreLink)

	def suchen(self):
		self.session.openWithCallback(self.SuchenCallback, VirtualKeyBoard, title = (_("Suchkriterium eingeben")), text = self.suchString)

	def SuchenCallback(self, callback = None, entry = None):
		if callback is not None and len(callback):
			self.suchString = callback.replace(' ', '+')
			streamGenreLink = 'http://www.tube8.com/searches.html?q=%s&page=' % (self.suchString)
			self.session.open(tube8FilmScreen, streamGenreLink)

	def keyCancel(self):
		self.close()

class tube8FilmScreen(Screen):

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

		self['title'] = Label("Tube8.com")
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
		url = "%s%s/" % (self.phCatLink, str(self.page))
		print url
		getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.genreData).addErrback(self.dataError)

	def genreData(self, data):
		phMovies = re.findall('id="video.*?a\shref="(.*?)".*?src="(.*?)".*?title="(.*?)".*?<strong>(.*?)</strong>.*?float-right">(.*?)\sviews.*?float-right">(.*?)\sago</div>', data, re.S)
		if phMovies:
			for (phUrl, phImage, phTitle, phRuntime, phViews, phAdded) in phMovies:
				self.filmliste.append((decodeHtml(phTitle), phUrl, phImage, phRuntime, phViews, phAdded))
			self.chooseMenuList.setList(map(tube8FilmListEntry, self.filmliste))
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
		fetchurl = match
		fetchurl = urllib2.unquote(match[0])
		match = re.compile('"video_title":"([^"]+)"').findall(data)
		title = urllib.unquote_plus(match[0])
		phStream = decrypt(fetchurl, title, 256)
		if phStream:
			self.session.open(SimplePlayer, [(phTitle, phStream)], showPlaylist=False, ltype='tube8')

	def keyCancel(self):
		self.close()