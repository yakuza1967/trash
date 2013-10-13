from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.simpleplayer import SimplePlayer

def movie25GenreListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 20, 0, 900, 25, 0, RT_HALIGN_CENTER | RT_VALIGN_CENTER, entry[0])
		]

def movie25FilmListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 20, 0, 900, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry[0])
		]

def movie25HosterListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 20, 0, 900, 25, 0, RT_HALIGN_CENTER | RT_VALIGN_CENTER, entry[0])
		]

class movie25GenreScreen(Screen):

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
		self['title'] = Label("movie25.so")
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
		self.genreliste = [ ('New Releases',"http://www.movie25.so/movies/new-releases/"),
		                    ('Last Added',"http://www.movie25.so/movies/latest-added/"),
		                    ('Featured Movies',"http://www.movie25.so/movies/featured-movies/"),
		                    ('Latest HQ Movies',"http://www.movie25.so/movies/latest-hd-movies/"),
		                    ('Most Viewed',"http://www.movie25.so/movies/most-viewed/"),
		                    ('Most Voted',"http://www.movie25.so/movies/most-voted/"),
                            ('Action',"http://www.movie25.so/movies/action/"),
                            ('Adventure',"http://www.movie25.so/movies/adventure/"),
                            ('Animation',"http://www.movie25.so/movies/animation/"),
                            ('Biography',"http://www.movie25.so/movies/biography/"),
                            ('Comedy',"http://www.movie25.so/movies/comedy/"),
                            ('Crime',"http://www.movie25.so/movies/crime/"),
                            ('Documentary',"http://www.movie25.so/movies/documentary/"),
                            ('Drama',"http://www.movie25.so/movies/drama/"),
                            ('Family',"http://www.movie25.so/movies/family/"),
                            ('History',"http://www.movie25.so/movies/history/"),
                            ('Horror',"http://www.movie25.so/movies/horror/"),
                            ('Music',"http://www.movie25.so/movies/music/"),
                            ('Musical',"http://www.movie25.so/movies/musical/"),
                            ('Mystery',"http://www.movie25.so/movies/mystery/"),
                            ('Romance',"http://www.movie25.so/movies/romance/"),
                            ('Sci-Fi',"http://www.movie25.so/movies/sci-fi/"),
                            ('Short',"http://www.movie25.so/movies/short/"),
                            ('Sport',"http://www.movie25.so/movies/sport/"),
                            ('Thriller',"http://www.movie25.so/movies/thriller/"),
                            ('War',"http://www.movie25.so/movies/war/"),
                            ('Western',"http://www.movie25.so/movies/western/"),
                            ('Movie Title 0-9',"http://www.movie25.so/movies/0-9/"),
                            ('Movie Title A',"http://www.movie25.so/movies/a/"),
                            ('Movie Title B',"http://www.movie25.so/movies/b/"),
                            ('Movie Title C',"http://www.movie25.so/movies/c/"),
                            ('Movie Title D',"http://www.movie25.so/movies/d/"),
                            ('Movie Title E',"http://www.movie25.so/movies/e/"),
                            ('Movie Title F',"http://www.movie25.so/movies/f/"),
                            ('Movie Title G',"http://www.movie25.so/movies/g/"),
                            ('Movie Title H',"http://www.movie25.so/movies/h/"),
                            ('Movie Title I',"http://www.movie25.so/movies/i/"),
                            ('Movie Title J',"http://www.movie25.so/movies/j/"),
                            ('Movie Title K',"http://www.movie25.so/movies/k/"),
                            ('Movie Title L',"http://www.movie25.so/movies/l/"),
                            ('Movie Title M',"http://www.movie25.so/movies/m/"),
                            ('Movie Title N',"http://www.movie25.so/movies/n/"),
                            ('Movie Title O',"http://www.movie25.so/movies/o/"),
                            ('Movie Title P',"http://www.movie25.so/movies/p/"),
                            ('Movie Title Q',"http://www.movie25.so/movies/q/"),
                            ('Movie Title R',"http://www.movie25.so/movies/r/"),
                            ('Movie Title S',"http://www.movie25.so/movies/s/"),
                            ('Movie Title T',"http://www.movie25.so/movies/t/"),
                            ('Movie Title U',"http://www.movie25.so/movies/u/"),
                            ('Movie Title V',"http://www.movie25.so/movies/v/"),
                            ('Movie Title W',"http://www.movie25.so/movies/w/"),
                            ('Movie Title X',"http://www.movie25.so/movies/x/"),
                            ('Movie Title Y',"http://www.movie25.so/movies/y/"),
                            ('Movie Title Z',"http://www.movie25.so/movies/z/"),]

		self.chooseMenuList.setList(map(movie25GenreListEntry, self.genreliste))
		self.keyLocked = False

	def keyOK(self):
		streamGenreName = self['genreList'].getCurrent()[0][0]
		streamGenreLink = self['genreList'].getCurrent()[0][1]
		print streamGenreName, streamGenreLink

		self.session.open(movie25FilmeListeScreen, streamGenreLink, streamGenreName)

	def keyCancel(self):
		self.close()

class movie25FilmeListeScreen(Screen):

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
			"cancel": self.keyCancel,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft,
			"nextBouquet" : self.keyPageUp,
			"prevBouquet" : self.keyPageDown
		}, -1)

		self['title'] = Label("movie25.so")
		self['ContentTitle'] = Label("%s:" % self.streamGenreName)
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
		self.page = 1
		self.filmliste = []
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['liste'] = self.chooseMenuList

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self['Page'].setText(str(self.page)+ " of")
		url = "%s%s" % (self.streamGenreLink, str(self.page))
		print "url =", url
		getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.loadPageData).addErrback(self.dataError)

	def dataError(self, error):
		printl(error,self,"E")

	def loadPageData(self, data):
		print "daten bekommen"
		lastpage = re.findall('>Page <font color=red>.*?</font> of (.*\d)</td>', data, re.S)
		if lastpage:
			self['page'].setText(lastpage[0])

		data=data.replace('\r','').replace('\n','').replace('\t','').replace('&nbsp;','')
		movies = re.findall('        <li><div class="movie_pic"><a href="(.+?)"  target.+?img src="(.+?)".+?target="_self">(.+?)</a></', data, re.S)
                movies += re.findall('</li>      <li><div class="movie_pic"><a href="(.+?)"  target.+?img src="(.+?)".+?target="_self">(.+?)</a></', data, re.S)
		if movies:
			self.filmliste = []
			for (link,image,title) in movies:
			        link = "http://www.movie25.so" + link
				self.filmliste.append((decodeHtml(title),link,image))
			self.chooseMenuList.setList(map(movie25FilmListEntry, self.filmliste))
			self.keyLocked = False
			self.loadPic()

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
		self.session.open(movie25StreamListeScreen, streamLink, streamName)

	def keyLeft(self):
		if self.keyLocked:
			return
		self['liste'].pageUp()
		self.loadPic()

	def keyRight(self):
		if self.keyLocked:
			return
		self['liste'].pageDown()
		self.loadPic()

	def keyUp(self):
		if self.keyLocked:
			return
		self['liste'].up()
		self.loadPic()

	def keyDown(self):
		if self.keyLocked:
			return
		self['liste'].down()
		self.loadPic()

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

class movie25StreamListeScreen(Screen):

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

		self['title'] = Label("movie25.so")
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
		print "movie25StreamListeScreen daten bekommen data = ", data
                streams = re.findall('<li class="link_name">(.*?)</li>.*?<li class="playing_button"><span><a href="(.*?)" target', data, re.S)
                print " streams =", streams
		if streams:
			self.filmliste = []
			for (name,link) in streams:
			        link = "http://www.movie25.so" + link
				if re.match('.*?(mightyupload|sharesix|putme|limevideo|stream2k|played|putlocker|sockshare|streamclou|xvidstage|filenuke|movreel|nowvideo|xvidstream|uploadc|vreer|MonsterUploads|Novamov|Videoweed|Divxstage|Ginbig|Flashstrea|Movshare|yesload|faststream|Vidstream|PrimeShare|flashx|Divxmov|BitShare|Userporn)', name, re.S|re.I):
					self.filmliste.append((decodeHtml(name),link))

			if len(self.filmliste) == 0:
				self.filmliste.append(("No supported streams found.", "No supported streams found."))
				self.chooseMenuList.setList(map(movie25HosterListEntry, self.filmliste))
			else:
				self.chooseMenuList.setList(map(movie25HosterListEntry, self.filmliste))
				self.keyLocked = False

	def keyOK(self):
		if self.keyLocked:
			return
		streamName = self['liste'].getCurrent()[0][0]
		streamLink = self['liste'].getCurrent()[0][1]
		print "streamName, streamLink B=", streamName, streamLink
		getPage(streamLink, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.getLink).addErrback(self.dataError)

	def getLink(self, data):
		print "getLink data =", data
                link = re.findall("value=.*?Click Here to Play.*?onclick=.*?Javascript:location.href=.*?(http://.*?)'", data, re.S)
                print "link =", link
		if link:
			print link[0]
			get_stream_link(self.session).check_link(link[0], self.got_link, False)
		else:
			message = self.session.open(MessageBox, _("Stream not found, try another Stream Hoster."), MessageBox.TYPE_INFO, timeout=3)

	def got_link(self, stream_url):
		if stream_url == None:
			message = self.session.open(MessageBox, _("Stream not found, try another Stream Hoster."), MessageBox.TYPE_INFO, timeout=3)
		else:
			self.session.open(SimplePlayer, [(self.streamGenreName, stream_url)], showPlaylist=False, ltype='movie25')

	def keyCancel(self):
		self.close()