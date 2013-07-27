from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.simpleplayer import SimplePlayer

def sport1fmGenreListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 50, 0, 800, 25, 0, RT_HALIGN_CENTER | RT_VALIGN_CENTER, entry[0])
		]

def sport1fmListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 50, 0, 800, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry)
		]

class sport1fmGenreScreen(Screen):

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

		self.keyLocked = True
		self['title'] = Label("Sport1.fm")
		self['ContentTitle'] = Label("Sendungen:")
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
		url = "http://www.sport1.fm/data/live.json"
		getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.loadPageData).addErrback(self.dataError)

	def loadPageData(self, data):
		info = re.findall('"resource":"(.*?)".*?"adcode":".*?".*?"resourceid":.*?."type":"stream"."tstamp":.*?."stream.start":(.*?)."stream.end":(.*?).".*?game.home.name":"(.*?)"."game.guest.iconid":.*?"game.guest.name":"(.*?)"."game.status":"(.*?)"."game.minute":(.*?)."game.scores.half":".*?"."game.scores.current":"(.*?)"', data, re.S)
		if info:
			self.genreliste = []
			for (stream, start, end, teamA, teamB, status, running, score) in info:
				print stream, start, end, teamA, teamB, status, running, score
				match = "%s - %s" % (teamA, teamB)
				status = "%s: %s" % (status, running)
				self.genreliste.append((decodeHtml(match), stream, status, score))
			self.chooseMenuList.setList(map(sport1fmGenreListEntry, self.genreliste))
			self.keyLocked = False
		else:
			self.genreliste.append(("Keine Streams vorhanden."))
			self.chooseMenuList.setList(map(sport1fmListEntry, self.genreliste))

	def dataError(self, error):
		printl(error,self,"E")

	def keyOK(self):
		if self.keyLocked:
			return
		sport1fmName = self['genreList'].getCurrent()[0][0]
		sport1fmUrl = self['genreList'].getCurrent()[0][1]
		print sport1fmName, sport1fmUrl
		self.session.open(sport1fmListeScreen, sport1fmName, sport1fmUrl)

	def keyCancel(self):
		self.close()

class sport1fmListeScreen(Screen):

	def __init__(self, session, sport1fmName, sport1fmUrl):
		self.session = session
		self.sport1fmName = sport1fmName
		self.sport1fmUrl = sport1fmUrl

		self.plugin_path = mp_globals.pluginPath
		self.skin_path =  mp_globals.pluginPath + "/skins"

		path = "%s/%s/defaultListWideScreen.xml" % (self.skin_path, config.mediaportal.skin.value)
		if not fileExists(path):
			path = self.skin_path + "/original/defaultListWideScreen.xml"

		with open(path, "r") as f:
			self.skin = f.read()
			f.close()

		Screen.__init__(self, session)

		self["actions"]  = ActionMap(["OkCancelActions", "ShortcutActions", "WizardActions", "ColorActions", "SetupActions", "NumberActions", "MenuActions", "EPGSelectActions"], {
			"ok"    : self.keyOK,
			"cancel": self.keyCancel,
			"red": self.keyCancel
		}, -1)

		self.keyLocked = True
		self['title'] = Label("Sport1.fm")
		self['ContentTitle'] = Label("Streams:")
		self['name'] = Label("")
		self['F1'] = Label("Exit")
		self['F2'] = Label("")
		self['F3'] = Label("")
		self['F4'] = Label("")
		self['F3'].hide()
		self['F4'].hide()
		self['handlung'] = Label("")
		self['page'] = Label("")
		self['Page'] = Label("")
		self['coverArt'] = Pixmap()

		self.streamliste = []
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['liste'] = self.chooseMenuList

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		print "hole daten"
		url = "http://playerservices.streamtheworld.com/api/livestream?version=1.5&mount=%sAAC" % self.sport1fmUrl
		print url
		getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.loadPageData).addErrback(self.dataError)

	def loadPageData(self, data):
		self.streamliste = []
		streams = re.findall('<ip>(.*?)</ip>', data, re.S)
		mount = re.findall('<mount>(.*?)</mount>', data, re.S)
		if streams and mount:
			for stream in streams:
				stream = "http://%s/%s" % (stream, mount[0])
				print stream
				self.streamliste.append((stream))

			self.chooseMenuList.setList(map(sport1fmListEntry, self.streamliste))
			self.keyLocked = False

	def keyOK(self):
		if self.keyLocked:
			return
		stream_url = self['liste'].getCurrent()[0]
		print stream_url
		self.session.open(SimplePlayer, [(self.sport1fmName, stream_url)], showPlaylist=False, ltype='sport1fm')

	def dataError(self, error):
		printl(error,self,"E")

	def keyCancel(self):
		self.close()