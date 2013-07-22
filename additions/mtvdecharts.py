from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.simpleplayer import SimplePlayer
from Plugins.Extensions.MediaPortal.resources.mtvdelink import MTVdeLink

def MTVdeChartsGenreListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 20, 0, 860, 25, 0, RT_HALIGN_CENTER | RT_VALIGN_CENTER, entry[0])
		]

def MTVdeChartsSongListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 50, 0, 800, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry[0])
		]

class MTVdeChartsGenreScreen(Screen):

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
		self['title'] = Label("MTV.de")
		self['ContentTitle'] = Label("Charts:")
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
		self.genreliste = [('German Top100 Single Charts',"http://www.mtv.de/charts/5-hitlist-germany-top-100"),
							('MTV.de Video Charts',"http://www.mtv.de/musikvideos/11-mtv-de-videocharts/playlist"),
							('German Black Charts',"http://www.mtv.de/charts/9-deutsche-black-charts"),
							('Dance Charts',"http://www.mtv.de/charts/6-dance-charts")]

		self.chooseMenuList.setList(map(MTVdeChartsGenreListEntry, self.genreliste))
		self.keyLocked = False

	def keyOK(self):
		if self.keyLocked:
			return
		MTVName = self['genreList'].getCurrent()[0][0]
		MTVUrl = self['genreList'].getCurrent()[0][1]

		print MTVName, MTVUrl
		self.session.open(MTVdeChartsSongListeScreen, MTVName, MTVUrl)

	def keyCancel(self):
		self.close()

class MTVdeChartsSongListeScreen(Screen):

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
		self['title'] = Label("MTV.de")
		self['ContentTitle'] = Label("Charts: %s" % self.genreName)
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
		charts = re.findall("data-uma-token='(.*?)'.*?title=\"(.*?)\"><span class='chart_position'>.*?src=\"(http://images.mtvnn.com.*?)\"", data, re.S)
		if charts:
			self.filmliste = []
			for (token, title, image) in charts:
				if not re.match('.*?Video nicht', title):
					self.filmliste.append((decodeHtml(title),token,image))
			self.chooseMenuList.setList(map(MTVdeChartsSongListEntry, self.filmliste))
			self.keyLocked = False

	def dataError(self, error):
		printl(error,self,"E")

	def keyOK(self):
		if self.keyLocked:
			return
		MTVName = self['genreList'].getCurrent()[0][0]
		MTVToken = self['genreList'].getCurrent()[0][1]
		idx = self['genreList'].getSelectedIndex()

		print idx, MTVName, MTVToken
		self.session.open(MTVdeChartsPlayer, self.filmliste, int(idx) , True, self.genreName)

	def keyCancel(self):
		self.close()

class MTVdeChartsPlayer(SimplePlayer):

	def __init__(self, session, playList, playIdx=0, playAll=True, listTitle=None):
		print "MTVdeChartsPlayer:"
		print listTitle

		SimplePlayer.__init__(self, session, playList, playIdx=playIdx, playAll=playAll, listTitle=listTitle, ltype='mtv')

		self.onLayoutFinish.append(self.getVideo)

	def getVideo(self):
		title = self.playList[self.playIdx][self.title_inr]
		token = self.playList[self.playIdx][1]
		imgurl = self.playList[self.playIdx][2]
		print title, token

		artist = ''
		p = title.find(' - ')
		if p > 0:
			artist = title[:p].strip()
			title = title[p+3:].strip()

		MTVdeLink(self.session).getLink(self.playStream, self.dataError, title, artist, token, imgurl)