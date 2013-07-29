from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.simpleplayer import SimplePlayer

def wrestlingnetworkGenreListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 0, 0, 800, 25, 0, RT_HALIGN_CENTER | RT_VALIGN_CENTER, entry[0])
		]

def wrestlingnetworkListEntry(entry):
	#TYPE_TEXT, x, y, width, height, fnt, flags, string [, color, backColor, backColorSelected, borderWidth, borderColor])
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 50, 0, 800, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry[0])
		]

class wrestlingnetworkGenreScreen(Screen):

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
		self['title'] = Label("wrestling-network.net")
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
		self.genreliste = [('Full Replays',"http://wrestling-network.net/tag/show-replay/page/"),
							('WWE',"http://wrestling-network.net/category/wwe/page/"),
							('RAW',"http://wrestling-network.net/category/wwe/wwe-raw/page/"),
							('Smackdown',"http://wrestling-network.net/category/wwe/wwe-smackdown/page/"),
							('NXT',"http://wrestling-network.net/category/wwe/wwe-nxt/page"),
							('TNA',"http://wrestling-network.net/category/tna/page/"),
							('ROH',"http://wrestling-network.net/category/roh/page/")]

		self.chooseMenuList.setList(map(wrestlingnetworkGenreListEntry, self.genreliste))
		self.keyLocked = False

	def keyOK(self):
		if self.keyLocked:
			return
		wrestlingnetworkName = self['genreList'].getCurrent()[0][0]
		wrestlingnetworkUrl = self['genreList'].getCurrent()[0][1]

		print wrestlingnetworkName, wrestlingnetworkUrl
		self.session.open(wrestlingnetworkSongListeScreen, wrestlingnetworkName, wrestlingnetworkUrl)


	def keyCancel(self):
		self.close()

class wrestlingnetworkSongListeScreen(Screen):

	def __init__(self, session, genreName, genreLink):
		self.session = session
		self.genreLink = genreLink
		self.genreName = genreName
		self.plugin_path = mp_globals.pluginPath
		self.skin_path =  mp_globals.pluginPath + "/skins"

		path = "%s/%s/defaultListScreen.xml" % (self.skin_path, config.mediaportal.skin.value)
		if not fileExists(path):
			path = self.skin_path + "/original/defaultListScreen.xml"

		with open(path, "r") as f:
			self.skin = f.read()
			f.close()

		Screen.__init__(self, session)

		self["actions"]  = ActionMap(["OkCancelActions", "ShortcutActions", "WizardActions", "ColorActions", "SetupActions", "NumberActions", "MenuActions", "EPGSelectActions"], {
			"ok"    : self.keyOK,
			"cancel": self.keyCancel,
			"nextBouquet" : self.keyPageUp,
			"prevBouquet" : self.keyPageDown
		}, -1)

		self.keyLocked = True
		self['title'] = Label("wrestling-network.net")
		self['ContentTitle'] = Label("Genre: %s" % self.genreName)
		self['name'] = Label("")
		self['F1'] = Label("Exit")
		self['F2'] = Label("")
		self['F3'] = Label("")
		self['F4'] = Label("")
		self['F1'].hide()
		self['F2'].hide()
		self['F3'].hide()
		self['F4'].hide()
		self['coverArt'] = Pixmap()
		self['Page'] = Label("")
		self['page'] = Label("")
		self['handlung'] = Label("")

		self.filmliste = []
		self.page = 1
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['liste'] = self.chooseMenuList

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.keyLocked = True
		url = "%s%s" % (self.genreLink ,str(self.page))
		print url
		getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.loadPageData).addErrback(self.dataError)

	def loadPageData(self, data):
		print "drin"
		self['Page'].setText(str(self.page)+" of")
		self.lastpage = re.findall("<span class='pages'>Page.*?of (.*?)</span>", data, re.S|re.I)
		if self.lastpage:
			self['page'].setText(self.lastpage[0])

		shows = re.findall('<h2 class="title"><a href="(.*?)" rel="bookmark" title=".*?">(.*?)</a></h2>', data, re.S)
		if shows:
			self.filmliste = []
			for (url,title) in shows:
				self.filmliste.append((title,url))
			self.chooseMenuList.setList(map(wrestlingnetworkListEntry, self.filmliste))
			self.keyLocked = False

	def dataError(self, error):
		printl(error,self,"E")

	def keyOK(self):
		if self.keyLocked:
			return
		wrestlingnetworkName = self['liste'].getCurrent()[0][0]
		wrestlingnetworkUrl = self['liste'].getCurrent()[0][1]
		idx = self['liste'].getSelectedIndex()

		print idx, wrestlingnetworkName, wrestlingnetworkUrl
		self.session.open(wrestlingnetworkPlayer, self.filmliste, int(idx) , True, None, None)

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
		if not self.page == int(self.lastpage[0]):
			self.page += 1
			self.loadPage()

	def keyCancel(self):
		self.close()

class wrestlingnetworkPlayer(SimplePlayer):

	def __init__(self, session, playList, playIdx=0, playAll=True, listTitle=None, cover=None):
		print "wrestlingnetworkPlayer:"

		SimplePlayer.__init__(self, session, playList, playIdx, playAll, listTitle, 'local', 0, cover)

		self.onLayoutFinish.append(self.getVideo)

	def getVideo(self):
		self.wrestlingnetworkName = self.playList[self.playIdx][0]
		wrestlingnetworkUrl = self.playList[self.playIdx][1]
		print self.wrestlingnetworkName, wrestlingnetworkUrl

		getPage(wrestlingnetworkUrl, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.getData).addErrback(self.dataError)

	def getData(self, data):
		print "hole dailymotion id"
		id = re.findall('<iframe.*?src="/dm-big.php\?id=(.*?)&amp;', data, re.S)
		if id:
			url = "http://www.dailymotion.com/sequence/full/%s" % id[0]
			print url
			getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.getStream).addErrback(self.dataError)

	def getStream(self, data):
		print "hole stream_url"
		stream_url = re.findall('"video_url":"(.*?)"', data, re.S)
		if stream_url:
			stream_url = urllib2.unquote(stream_url[0])
			print stream_url
			self.playStream(self.wrestlingnetworkName, stream_url)
