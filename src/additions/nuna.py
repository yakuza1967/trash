from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.simpleplayer import SimplePlayer

def nunaGenreListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 50, 0, 800, 25, 0, RT_HALIGN_CENTER | RT_VALIGN_CENTER, entry[0])
		]

def nunaListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 50, 0, 800, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry[0])
		]

class nunaGenreScreen(Screen):

	def __init__(self, session):
		self.session = session

		self.plugin_path = mp_globals.pluginPath
		self.skin_path =  mp_globals.pluginPath + "/skins"

		path = "%s/%s/defaultGenreScreen.xml" % (self.skin_path, config.mediaportal.skin.value)
		if not fileExists(path):
			path = self.skin_path + "/original/defaultGenreScreen.xml"

		with open(path, "r") as f:
			self.skin = f.read()
			f.close()

		Screen.__init__(self, session)

		self["actions"]  = ActionMap(["OkCancelActions", "ShortcutActions", "WizardActions", "ColorActions", "SetupActions", "NumberActions", "MenuActions", "EPGSelectActions"], {
			"ok"    : self.keyOK,
			"cancel": self.keyCancel,
			"red": self.keyCancel
		}, -1)

		self.lastservice = session.nav.getCurrentlyPlayingServiceReference()
		self.playing = False

		self.keyLocked = True
		self['title'] = Label("nuna.tv")
		self['ContentTitle'] = Label("Genre:")
		self['name'] = Label("")
		self['F1'] = Label("Exit")
		self['F2'] = Label("")
		self['F3'] = Label("")
		self['F4'] = Label("")
		self['F3'].hide()
		self['F4'].hide()

		self.genreliste = []
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['genreList'] = self.chooseMenuList

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.genreliste = [('Musikrichtung',"Musikrichtung"),
							('Kuenstler',"nstler")]

		self.chooseMenuList.setList(map(nunaGenreListEntry, self.genreliste))
		self.keyLocked = False

	def keyOK(self):
		if self.keyLocked:
			return
		nunaName = self['genreList'].getCurrent()[0][0]
		nunaUrl = self['genreList'].getCurrent()[0][1]

		print nunaName, nunaUrl
		self.session.open(nunaArtistListeScreen, nunaName, nunaUrl)

	def keyCancel(self):
		self.close()

class nunaArtistListeScreen(Screen):

	def __init__(self, session, genreName, genreLink):
		self.session = session
		self.genreLink = genreLink
		self.genreName = genreName
		self.plugin_path = mp_globals.pluginPath
		self.skin_path =  mp_globals.pluginPath + "/skins"

		path = "%s/%s/defaultGenreScreen.xml" % (self.skin_path, config.mediaportal.skin.value)
		if not fileExists(path):
			path = self.skin_path + "/original/defaultGenreScreen.xml"

		with open(path, "r") as f:
			self.skin = f.read()
			f.close()

		Screen.__init__(self, session)

		self["actions"]  = ActionMap(["OkCancelActions", "ShortcutActions", "WizardActions", "ColorActions", "SetupActions", "NumberActions", "MenuActions", "EPGSelectActions"], {
			"ok"    : self.keyOK,
			"cancel": self.keyCancel
		}, -1)

		self.keyLocked = True
		self['title'] = Label("nuna.tv")
		self['ContentTitle'] = Label("Genre: %s" % self.genreName)
		self['name'] = Label("")
		self['F1'] = Label("Exit")
		self['F2'] = Label("")
		self['F3'] = Label("")
		self['F4'] = Label("")
		self['F3'].hide()
		self['F4'].hide()

		self.filmliste = []
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['genreList'] = self.chooseMenuList

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.keyLocked = True
		url = "http://www.nuna.tv/"

		getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.loadPageData).addErrback(self.dataError)

	def loadPageData(self, data):
		print "drin"
		if re.match('.*?Musikrichtung', self.genreLink, re.S):
			parse = "Musikrichtung"
		else:
			parse = "nstler"

		raw = re.search('<select\sdata-placeholder=".*?'+parse+'"\sclass="chzn-select">(.*)</select>', data, re.S)
		if raw:
			self.filmliste = []
			genre = re.findall('<option\svalue="(/videos.js.*?)"\s{0,2}>(.*?)</option', raw.group(1), re.S|re.I)
			if genre:
				for link,title in genre:
					url = "http://www.nuna.tv%s" % link
					self.filmliste.append((decodeHtml(title),url))
			self.chooseMenuList.setList(map(nunaListEntry, self.filmliste))
			self.keyLocked = False

	def dataError(self, error):
		printl(error,self,"E")

	def keyOK(self):
		if self.keyLocked:
			return
		nunaName = self['genreList'].getCurrent()[0][0]
		nunaUrl = self['genreList'].getCurrent()[0][1]

		print nunaName, nunaUrl
		self.session.open(nunaMusicListeScreen, nunaName, nunaUrl)

	def keyCancel(self):
		self.close()

class nunaMusicListeScreen(Screen):

	def __init__(self, session, genreName, genreLink):
		self.session = session
		self.genreLink = genreLink
		self.genreName = genreName
		self.plugin_path = mp_globals.pluginPath
		self.skin_path =  mp_globals.pluginPath + "/skins"

		path = "%s/%s/defaultGenreScreen.xml" % (self.skin_path, config.mediaportal.skin.value)
		if not fileExists(path):
			path = self.skin_path + "/original/defaultGenreScreen.xml"

		with open(path, "r") as f:
			self.skin = f.read()
			f.close()

		Screen.__init__(self, session)

		self["actions"]  = ActionMap(["OkCancelActions", "ShortcutActions", "WizardActions", "ColorActions", "SetupActions", "NumberActions", "MenuActions", "EPGSelectActions"], {
			"ok"    : self.keyOK,
			"cancel": self.keyCancel
		}, -1)

		self.keyLocked = True
		self['title'] = Label("nuna.tv")
		self['ContentTitle'] = Label("Genre: %s" % self.genreName)
		self['name'] = Label("")
		self['F1'] = Label("Exit")
		self['F2'] = Label("")
		self['F3'] = Label("")
		self['F4'] = Label("")
		self['F3'].hide()
		self['F4'].hide()

		self.filmliste = []
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['genreList'] = self.chooseMenuList

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.keyLocked = True
		print self.genreLink
		getPage(self.genreLink, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.loadPageData).addErrback(self.dataError)

	def loadPageData(self, data):
		print "drin"

		vids = re.findall('li\s{0,1}>\s{0,1}<a\shref="(.*?)".*?<img\salt="(.*?)"\ssrc="(.*?)"\s/>', data, re.S)
		if vids:
			self.filmliste = []
			for (link,title,image) in vids:
				url = "http://www.nuna.tv%s" % link
				self.filmliste.append((decodeHtml(title),url,image))
			self.chooseMenuList.setList(map(nunaListEntry, self.filmliste))
			self.keyLocked = False

	def dataError(self, error):
		printl(error,self,"E")

	def keyOK(self):
		if self.keyLocked:
			return
		self.nunaName = self['genreList'].getCurrent()[0][0]
		nunaUrl = self['genreList'].getCurrent()[0][1]
		nunaImage = self['genreList'].getCurrent()[0][2]
		idx = self['genreList'].getSelectedIndex()

		print idx, self.nunaName, nunaUrl, nunaImage
		self.session.open(NunaPlayer, self.filmliste, int(idx) , True, None)

	def keyCancel(self):
		self.close()

class NunaPlayer(SimplePlayer):

	def __init__(self, session, playList, playIdx=0, playAll=True, listTitle=None):
		print "NunaPlayer:"

		SimplePlayer.__init__(self, session, playList, playIdx=playIdx, playAll=playAll, listTitle=listTitle)

	def getVideo(self):
		self.nunaName = self.playList[self.playIdx][0]
		nunaUrl = self.playList[self.playIdx][1]
		print self.nunaName, nunaUrl
		getPage(nunaUrl, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.getStream).addErrback(self.dataError)

	def getStream(self, data):
		stream_url = re.findall('data-site-url=".*?" href="(.*?)"', data)
		if stream_url:
			print stream_url
			self.playStream(self.nunaName, stream_url[0])