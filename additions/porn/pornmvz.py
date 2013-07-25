from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.simpleplayer import SimplePlayer

def pornmvzGenreListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 30, 0, 850, 25, 0, RT_HALIGN_CENTER | RT_VALIGN_CENTER, entry[0])
		]

def pornmvzListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 50, 0, 800, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry[0])
		]

class pornmvzGenreScreen(Screen):

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
		self.language = "de"
		self.suchString = ''
		self['title'] = Label("PORNMVZ.com")
		self['ContentTitle'] = Label("Genres")
		self['name'] = Label("Genre Auswahl")
		self['F1'] = Label("Exit")
		self['F2'] = Label("")
		self['F3'] = Label("")
		self['F4'] = Label("")
		self['F2'].hide()
		self['F3'].hide()
		self['F4'].hide()

		self.genreliste = []
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['genreList'] = self.chooseMenuList

		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.keyLocked = True
		url = "http://pornmvz.com/"
		getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.genreData).addErrback(self.dataError)

	def genreData(self, data):
		parse = re.search('Categories</h6>(.*?)</select>', data, re.S)
		phCat = re.findall('value="(.*?)">(.*?)\sXXX\sMovies', parse.group(1), re.S)
		if phCat:
			for (phID, phTitle) in phCat:
				phUrl = 'http://pornmvz.com/?cat=%s&paged=' % phID
				self.genreliste.append((phTitle, phUrl))
			self.genreliste.sort()
			self.genreliste.insert(0, ("Newest", "http://pornmvz.com/?paged="))
			self.genreliste.insert(0, ("--- Search ---", "callSuchen", None))
			self.chooseMenuList.setList(map(pornmvzGenreListEntry, self.genreliste))
			self.keyLocked = False

	def dataError(self, error):
		printl(error,self,"E")

	def suchen(self):
		self.session.openWithCallback(self.SuchenCallback, VirtualKeyBoard, title = (_("Suchkriterium eingeben")), text = self.suchString)

	def SuchenCallback(self, callback = None, entry = None):
		if callback is not None and len(callback):
			self.suchString = callback.replace(' ', '+')
			pornmvzUrl = '%s' % (self.suchString)
			pornmvzGenre = "--- Search ---"
			self.session.open(pornmvzFilmListeScreen, pornmvzGenre, pornmvzUrl)

	def keyOK(self):
		if self.keyLocked:
			return
		pornmvzGenre = self['genreList'].getCurrent()[0][0]
		pornmvzUrl = self['genreList'].getCurrent()[0][1]
		print pornmvzGenre, pornmvzUrl
		if pornmvzGenre == "--- Search ---":
			self.suchen()
		else:
			self.session.open(pornmvzFilmListeScreen, pornmvzGenre, pornmvzUrl)

	def keyCancel(self):
		self.close()

class pornmvzFilmListeScreen(Screen):

	def __init__(self, session, genreName, genreLink):
		self.session = session
		self.genreLink = genreLink
		self.genreName = genreName
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
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft,
			"nextBouquet" : self.keyPageUp,
			"prevBouquet" : self.keyPageDown,
			"green" : self.keyPageNumber
		}, -1)

		self.keyLocked = True
		self.page = 1
		self.lastpage = 1
		self['title'] = Label("PORNMVZ.com")
		self['ContentTitle'] = Label("%s" % self.genreName)
		self['name'] = Label("Film Auswahl")
		self['F1'] = Label("Exit")
		self['F2'] = Label("Page")
		self['F3'] = Label("")
		self['F4'] = Label("")
		self['F3'].hide()
		self['F4'].hide()
		self['coverArt'] = Pixmap()
		self['Page'] = Label("Page")
		self['page'] = Label("")
		self['handlung'] = Label("")

		self.filmliste = []
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['liste'] = self.chooseMenuList

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.keyLocked = True
		self['name'].setText('Bitte warten...')
		if self.genreName == "--- Search ---":
			url = "http://pornmvz.com/?s=%s&paged=%s" % (self.genreLink,str(self.page))
		else:
			url = "%s%s" % (self.genreLink,str(self.page))
		print url
		getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.loadPageData).addErrback(self.dataError)

	def loadPageData(self, data):
		lastpparse = re.search('id="post-navigator">(.*?)</div>', data, re.S)
		lastp = re.search('Page.*?of\s(.*?):</span>', lastpparse.group(1), re.S)
		if lastp:
			self.lastpage = int(lastp.group(1))
		else:
			self.lastpage = 1
		self['page'].setText("%d/%d" % (self.page,self.lastpage))
		movies = re.findall('<div\sclass="post-meta"\sid=".*?<div\sclass="thumb"><a href="(http://pornmvz.com/.*?)"\s{0,2}title=".*?([a-zA-Z0-9].*?)"><img.*?src="(.*?)"', data, re.S)
		if movies:
			self.filmliste = []
			for (url,title,image) in movies:
				self.filmliste.append((decodeHtml(title),url,image))
			self.chooseMenuList.setList(map(pornmvzListEntry, self.filmliste))
			self.chooseMenuList.moveToIndex(0)
			self.keyLocked = False
			self.loadPic()

	def dataError(self, error):
		print "dataError:"
		printl(error,self,"E")

	def loadPic(self):
		streamTitle = self['liste'].getCurrent()[0][0]
		streamUrl = self['liste'].getCurrent()[0][1]
		streamPic = self['liste'].getCurrent()[0][2]
		self['name'].setText(streamTitle)
		downloadPage(streamPic, "/tmp/Icon.jpg").addCallback(self.ShowCover)
		getPage(streamUrl, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.getDescription).addErrback(self.dataError)

	def getDescription(self, data):
		ddDescription = re.search('class="post-content-single">\n<center>.*?</a><br\s/>\n{0,1}(.*?)<br\s/>.*?</center>', data, re.S)
		if ddDescription:
			if ddDescription.group(1) == "&#8230;":
				self['handlung'].setText("Keine Infos gefunden.")
			else:
				self['handlung'].setText(decodeHtml(ddDescription.group(1)))
		else:
			self['handlung'].setText("Keine Infos gefunden.")

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

	def keyPageNumber(self):
		self.session.openWithCallback(self.callbackkeyPageNumber, VirtualKeyBoard, title = (_("Seitennummer eingeben")), text = str(self.page))

	def callbackkeyPageNumber(self, answer):
		if answer is not None:
			answer = re.findall('\d+', answer)
		else:
			return
		if answer:
			if int(answer[0]) < self.lastpage + 1:
				self.page = int(answer[0])
				self.loadPage()
			else:
				self.page = self.lastpage
				self.loadPage()

	def keyPageDown(self):
		print "PageDown"
		if self.keyLocked:
			return
		if not self.page < 1:
			self.page -= 1
			self.loadPage()

	def keyPageUp(self):
		print "PageUP"
		if self.keyLocked:
			return
		if self.page < self.lastpage:
			self.page += 1
			self.loadPage()

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

	def keyOK(self):
		if self.keyLocked:
			return
		title = self['liste'].getCurrent()[0][0]
		url = self['liste'].getCurrent()[0][1]
		image = self['liste'].getCurrent()[0][2]
		self.session.open(pornmvzFilmAuswahlScreen, title, url, image)

	def keyCancel(self):
		self.close()

class pornmvzFilmAuswahlScreen(Screen):

	def __init__(self, session, genreName, genreLink, cover):
		self.session = session
		self.genreLink = genreLink
		self.genreName = genreName
		self.cover = cover
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
			"cancel": self.keyCancel
		}, -1)

		self.keyLocked = True
		self['title'] = Label("PORNMVZ.com")
		self['ContentTitle'] = Label("Streams")
		self['name'] = Label(self.genreName)
		self['F1'] = Label("Exit")
		self['F2'] = Label("")
		self['F3'] = Label("")
		self['F4'] = Label("")
		self['F2'].hide()
		self['F3'].hide()
		self['F4'].hide()
		self['coverArt'] = Pixmap()
		self['Page'] = Label("")
		self['page'] = Label("")
		self['handlung'] = Label("")

		self.filmliste = []
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['liste'] = self.chooseMenuList
		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.keyLocked = True
		print self.genreLink
		getPage(self.genreLink, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.loadPageData).addErrback(self.dataError)

	def loadPageData(self, data):
		parse = re.search('post-content-single(.*?)post-navigator-single', data, re.S)
		streams = re.findall('.*?"(http://.*?(streamcloud.eu|flashx|userporn|pixhost|pornmvz).*?)".*?', parse.group(1) , re.S)
		if streams:
			for (stream, hostername) in streams:
				if re.match('.*?(streamcloud.eu|flashx|userporn)', hostername, re.S|re.I):
					hostername = hostername.replace('.eu','')
					hostername = hostername.title()
					disc = re.search('.*?(CD-1|CD1|CD-2|CD2|_a.avi|_b.avi|-a.avi|-b.avi|DISC1|DISC2).*?', stream, re.S|re.I)
					if disc:
						discno = disc.group(1)
						discno = discno.replace('CD1','Teil 1').replace('CD2','Teil 2').replace('CD-1','Teil 1').replace('CD-2','Teil 2').replace('_a.avi','Teil 1').replace('_b.avi','Teil 2')
						discno = discno.replace('-a.avi','Teil 1').replace('-b.avi','Teil 2').replace('DISC1','Teil 1').replace('DISC2','Teil 2').replace('Disc1','Teil 1').replace('Disc2','Teil 2')
						hostername = hostername + ' (' + discno + ')'
					self.filmliste.append((hostername, stream))
		else:
			self.filmliste.append(("No streams found!",None))
		self.chooseMenuList.setList(map(pornmvzGenreListEntry, self.filmliste))
		self.keyLocked = False

	def keyOK(self):
		if self.keyLocked:
			return
		streamLink = self['liste'].getCurrent()[0][1]
		if streamLink == None:
			return
		url = streamLink
		url = url.replace('&amp;','&')
		url = url.replace('&#038;','&')
		get_stream_link(self.session).check_link(url, self.got_link)

	def got_link(self, stream_url):
		print "got_link:"
		if stream_url == None:
			message = self.session.open(MessageBox, _("Stream not found, try another Stream Hoster."), MessageBox.TYPE_INFO, timeout=3)
		else:
			title = self.genreName
			self.session.open(SimplePlayer, [(title, stream_url, self.cover)], showPlaylist=False, ltype='pornmvz', cover=True)

	def dataError(self, error):
		print "dataError:"
		printl(error,self,"E")

	def keyCancel(self):
		self.close()