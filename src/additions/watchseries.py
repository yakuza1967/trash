from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.simpleplayer import SimplePlayer

def watchseriesGenreListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 20, 0, 900, 25, 0, RT_HALIGN_CENTER | RT_VALIGN_CENTER, entry[0])
		]

def watchseriesFilmListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 20, 0, 900, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry[0])
		]

def watchseriesHosterListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 20, 0, 900, 25, 0, RT_HALIGN_CENTER | RT_VALIGN_CENTER, entry[0])
		]

class watchseriesGenreScreen(Screen):

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

		self["actions"]  = ActionMap(["OkCancelActions", "ShortcutActions", "WizardActions", "ColorActions", "SetupActions", "NumberActions", "MenuActions"], {
			"ok"    : self.keyOK,
			"cancel": self.keyCancel
		}, -1)

		self.keyLocked = True
		self['title'] = Label("watchseries.lt")
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
		self.genreliste = [('Series',"http://watchseries.lt/letters/"),
							('Newest Episodes Added',"http://watchseries.lt/latest"),
							('Popular Episodes Added This Week',"http://watchseries.lt/new"),
							('TV Schedule',"http://watchseries.lt/tvschedule/-1")]

		self.chooseMenuList.setList(map(watchseriesGenreListEntry, self.genreliste))
		self.keyLocked = False

	def keyOK(self):
		streamGenreName = self['genreList'].getCurrent()[0][0]
		streamGenreLink = self['genreList'].getCurrent()[0][1]
		print streamGenreName, streamGenreLink

		if streamGenreName == "Series":
			self.session.open(watchseriesSeriesLetterScreen, streamGenreLink, streamGenreName)
		#elif streamGenreName == "Newest Episodes Added":
		else:
			self.session.open(watchseriesNewSeriesScreen, streamGenreLink, streamGenreName)
		#elif streamGenreName == "Popular Episodes Added This Week":
		#	self.session.open(watchseriesSeriesScreen, streamGenreLink, streamGenreName)
		#elif streamGenreName == "TV Schedule":
		#	self.session.open(watchseriesSeriesScreen, streamGenreLink, streamGenreName)

	def keyCancel(self):
		self.close()

class watchseriesNewSeriesScreen(Screen):

	def __init__(self, session, streamGenreLink, streamGenreName):
		self.session = session
		self.streamGenreLink = streamGenreLink
		self.streamGenreName = streamGenreName
		self.plugin_path = mp_globals.pluginPath
		self.skin_path =  mp_globals.pluginPath + "/skins"

		path = "%s/%s/defaultGenreScreen.xml" % (self.skin_path, config.mediaportal.skin.value)
		if not fileExists(path):
			path = self.skin_path + "/original/defaultGenreScreen.xml"

		with open(path, "r") as f:
			self.skin = f.read()
			f.close()

		Screen.__init__(self, session)

		self["actions"]  = ActionMap(["OkCancelActions", "ShortcutActions", "WizardActions", "ColorActions", "SetupActions", "NumberActions", "MenuActions"], {
			"ok"    : self.keyOK,
			"cancel": self.keyCancel
		}, -1)

		self.keyLocked = True
		self['title'] = Label("watchseries.lt")
		self['ContentTitle'] = Label("%s:" % self.streamGenreName)
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
		print self.streamGenreLink
		getPage(self.streamGenreLink, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.loadPageData).addErrback(self.dataError)

	def dataError(self, error):
		printl(error,self,"E")

	def loadPageData(self, data):
		eps = re.findall('<li><a title=".*?" href="(/episode/.*?)">(.*?)</a></li>', data, re.S)
		if eps:
			for link,title in eps:
				title = title.replace('Seas. ','- S').replace('Ep. ','E')
				url = "http://watchseries.lt%s" % link
				self.genreliste.append((title, url))
			self.chooseMenuList.setList(map(watchseriesFilmListEntry, self.genreliste))
			self.keyLocked = False

	def keyOK(self):
		streamGenreName = self['genreList'].getCurrent()[0][0]
		streamGenreLink = self['genreList'].getCurrent()[0][1]
		print streamGenreName, streamGenreLink

		self.session.open(watchseriesStreamListeScreen, streamGenreLink, streamGenreName)

	def keyCancel(self):
		self.close()

class watchseriesSeriesLetterScreen(Screen):

	def __init__(self, session, streamGenreLink, streamGenreName):
		self.session = session
		self.streamGenreLink = streamGenreLink
		self.streamGenreName = streamGenreName
		self.plugin_path = mp_globals.pluginPath
		self.skin_path =  mp_globals.pluginPath + "/skins"

		path = "%s/%s/defaultGenreScreen.xml" % (self.skin_path, config.mediaportal.skin.value)
		if not fileExists(path):
			path = self.skin_path + "/original/defaultGenreScreen.xml"

		with open(path, "r") as f:
			self.skin = f.read()
			f.close()

		Screen.__init__(self, session)

		self["actions"]  = ActionMap(["OkCancelActions", "ShortcutActions", "WizardActions", "ColorActions", "SetupActions", "NumberActions", "MenuActions"], {
			"ok"    : self.keyOK,
			"cancel": self.keyCancel
		}, -1)

		self.keyLocked = True
		self['title'] = Label("watchseries.lt")
		self['ContentTitle'] = Label("Letter:")
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
		abc = ["09","A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]
		for letter in abc:
			url = "http://watchseries.lt/letters/%s" % letter
			self.genreliste.append((letter, url))

		self.chooseMenuList.setList(map(watchseriesGenreListEntry, self.genreliste))
		self.keyLocked = False

	def keyOK(self):
		streamGenreName = self['genreList'].getCurrent()[0][0]
		streamGenreLink = self['genreList'].getCurrent()[0][1]
		print streamGenreName, streamGenreLink

		self.session.open(watchseriesSeriesScreen, streamGenreLink, streamGenreName)

	def keyCancel(self):
		self.close()

class watchseriesSeriesScreen(Screen):

	def __init__(self, session, streamGenreLink, streamGenreName):
		self.session = session
		self.streamGenreLink = streamGenreLink
		self.streamGenreName = streamGenreName
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
			"cancel": self.keyCancel
			#"up" : self.keyUp
			#"down" : self.keyDown,
			#"right" : self.keyRight,
			#"left" : self.keyLeft,
			#"nextBouquet" : self.keyPageUp,
			#"prevBouquet" : self.keyPageDown
		}, -1)

		self['title'] = Label("watchseries.lt")
		self['ContentTitle'] = Label("Letter - %s:" % self.streamGenreName)
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

		self.keyLocked = True
		self.filmliste = []
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['liste'] = self.chooseMenuList

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		print self.streamGenreLink
		getPage(self.streamGenreLink, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.loadPageData).addErrback(self.dataError)

	def dataError(self, error):
		printl(error,self,"E")

	def loadPageData(self, data):
		print "daten bekommen"

		series = re.findall('<a title="(.*?)" href="(/serie/.*?)">', data, re.S)
		if series:
			self.filmliste = []
			for (title,link) in series:
				url = "http://watchseries.lt%s" % link
				self.filmliste.append((decodeHtml(title),url))
			self.chooseMenuList.setList(map(watchseriesFilmListEntry, self.filmliste))
			#self.loadPic()
			self.keyLocked = False

	def loadPic(self):
		streamPic = self['liste'].getCurrent()[0][2]
		downloadPage(streamPic, "/tmp/Icon.jpg").addCallback(self.ShowCover)

	def ShowCover(self, picData):
		if fileExists("/tmp/Icon.jpg"):
			self['coverArt'].instance.setPixmap(gPixmapPtr())
			self.scale = AVSwitch().getFramebufferScale()
			self.picload = ePicLoad()
			size = self['coverArt'].instance.size()
			self.picload.setPara((size.width(), size.height(), self.scale[0], self.scale[1], False, 1, "#FF000000"))
			if self.picload.startDecode("/tmp/Icon.jpg", 0, 0, False) == 0:
				ptr = self.picload.getData()
				if ptr != None:
					self['coverArt'].instance.setPixmap(ptr)
					self['coverArt'].show()
					del self.picload

	def keyOK(self):
		if self.keyLocked:
			return
		streamName = self['liste'].getCurrent()[0][0]
		streamLink = self['liste'].getCurrent()[0][1]

		print streamName, streamLink

		self.session.open(watchseriesEpisodeListeScreen, streamLink, streamName)

	def keyLeft(self):
		if self.keyLocked:
			return
		self['liste'].pageUp()
		#self.loadPic()

	def keyRight(self):
		if self.keyLocked:
			return
		self['liste'].pageDown()
		#self.loadPic()

	def keyUp(self):
		if self.keyLocked:
			return
		self['liste'].up()
		#self.loadPic()

	def keyDown(self):
		if self.keyLocked:
			return
		self['liste'].down()
		#self.loadPic()

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
		self.page += 1
		self.loadPage()

	def keyCancel(self):
		self.close()

class watchseriesEpisodeListeScreen(Screen):

	def __init__(self, session, streamGenreLink, streamGenreName):
		self.session = session
		self.streamGenreLink = streamGenreLink
		self.streamGenreName = streamGenreName
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
			"cancel": self.keyCancel
		}, -1)

		self['title'] = Label("watchseries.lt")
		self['ContentTitle'] = Label("Episodes for %s:" % self.streamGenreName)
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

		self.keyLocked = True
		self.filmliste = []
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['liste'] = self.chooseMenuList

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		print self.streamGenreLink
		getPage(self.streamGenreLink, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.loadPageData).addErrback(self.dataError)

	def dataError(self, error):
		printl(error,self,"E")

	def loadPageData(self, data):
		print "daten bekommen"
		eps = re.findall('<li><a href="(/episode/.*?)">', data, re.S)
		if eps:
			self.filmliste = []
			for url in eps:
				epinfo = re.findall('_s(\d)_e(\d).html', url)
				if epinfo:
					(episode,season) = epinfo[0]
					print episode, season, url
					episode = "S%sE%s" % (episode, season)
					url = "http://watchseries.lt%s" % url
					self.filmliste.append((decodeHtml(episode),url))
			self.chooseMenuList.setList(map(watchseriesGenreListEntry, self.filmliste))
			self.keyLocked = False

	def keyOK(self):
		if self.keyLocked:
			return
		streamName = self['liste'].getCurrent()[0][0]
		streamLink = self['liste'].getCurrent()[0][1]
		print streamName, streamLink

		self.session.open(watchseriesStreamListeScreen, streamLink, streamName)

	def keyCancel(self):
		self.close()

class watchseriesStreamListeScreen(Screen):

	def __init__(self, session, streamGenreLink, streamGenreName):
		self.session = session
		self.streamGenreLink = streamGenreLink
		self.streamGenreName = streamGenreName
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
			"cancel": self.keyCancel
		}, -1)

		self['title'] = Label("watchseries.lt")
		self['ContentTitle'] = Label("Streams for %s:" % self.streamGenreName)
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

		self.keyLocked = True
		self.filmliste = []
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['liste'] = self.chooseMenuList

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		print self.streamGenreLink
		getPage(self.streamGenreLink, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.loadPageData).addErrback(self.dataError)

	def dataError(self, error):
		printl(error,self,"E")

	def loadPageData(self, data):
		print "daten bekommen: streamlist"
		if re.match('.*?there are no links available for this episode', data, re.S|re.I):
			self.filmliste = []
			self.filmliste.append(("There are no links available for this episode", "No supported streams found."))
			self.chooseMenuList.setList(map(watchseriesHosterListEntry, self.filmliste))
		else:
			streams = re.findall('</td></tr><tr.*?><td><span>(.*?)</span></td><td> <a target="_blank" href="(/open/cale/.*?)"', data, re.S)
			print streams
			if streams:
				self.filmliste = []
				for (shname,shurl) in streams:
					print shname,shurl
					if re.match('.*?(sharesix|putme|limevideo|stream2k|played|putlocker|sockshare|streamclou|xvidstage|filenuke|movreel|nowvideo|xvidstream|uploadc|vreer|MonsterUploads|Novamov|Videoweed|Divxstage|Ginbig|Flashstrea|Movshare|yesload|faststream|Vidstream|PrimeShare|flashx|Divxmov|Zooupload|Wupfile|BitShare|Userporn)', shname, re.S|re.I):
						url = "http://watchseries.lt%s" % shurl
						self.filmliste.append((decodeHtml(shname),url))

				if len(self.filmliste) == 0:
					self.filmliste.append(("No supported streams found.", "No supported streams found."))
					self.chooseMenuList.setList(map(watchseriesHosterListEntry, self.filmliste))
				else:
					self.chooseMenuList.setList(map(watchseriesHosterListEntry, self.filmliste))
					self.keyLocked = False
			else:
				self.filmliste.append(("Wrong parsing..", "No supported streams found."))
				self.chooseMenuList.setList(map(watchseriesHosterListEntry, self.filmliste))

	def keyOK(self):
		if self.keyLocked:
			return
		streamName = self['liste'].getCurrent()[0][0]
		streamLink = self['liste'].getCurrent()[0][1]
		print streamName, streamLink
		getPage(streamLink, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.getLink).addErrback(self.dataError)

	def getLink(self, data):
		link = re.findall('<a class="myButton" href="(.*?)">Click Here to Play</a>', data, re.S)
		if link:
			print link[0]
			get_stream_link(self.session).check_link(link[0], self.got_link, False)
		else:
			message = self.session.open(MessageBox, _("Stream not found, try another Stream Hoster."), MessageBox.TYPE_INFO, timeout=3)

	def got_link(self, stream_url):
		if stream_url == None:
			message = self.session.open(MessageBox, _("Stream not found, try another Stream Hoster."), MessageBox.TYPE_INFO, timeout=3)
		else:
			self.session.open(SimplePlayer, [(self.streamGenreName, stream_url)], showPlaylist=False, ltype='watchseries')

	def keyCancel(self):
		self.close()
