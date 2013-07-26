from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.simpleplayer import SimplePlayer

def eroprofileGenreListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 20, 0, 900, 25, 0, RT_HALIGN_CENTER | RT_VALIGN_CENTER, entry[0])
		]

def eroprofileFilmListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 20, 0, 900, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry[0])
		]

class eroprofileGenreScreen(Screen):

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

		self['title'] = Label("EroProfile.com")
		self['name'] = Label("Genre Auswahl")
		self['coverArt'] = Pixmap()
		self.keyLocked = True
		self.suchString = ''

		self.genreliste = []
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['genreList'] = self.chooseMenuList

		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.genreliste.append(("--- Search ---", ""))
		self.genreliste.append(("Newest", "home"))
		self.genreliste.append(("Popular", "popular"))
		self.genreliste.append(("Amateur Moms/Mature", "13"))
		self.genreliste.append(("Amateur Teens", "14"))
		self.genreliste.append(("Amateurs", "12"))
		self.genreliste.append(("Asian", "19"))
		self.genreliste.append(("Ass", "27"))
		self.genreliste.append(("Big Ladies", "5"))
		self.genreliste.append(("Big Tits", "11"))
		self.genreliste.append(("Bisexual", "18"))
		self.genreliste.append(("Black / Ebony", "20"))
		self.genreliste.append(("Celeb", "23"))
		self.genreliste.append(("Facial / Cum", "24"))
		self.genreliste.append(("Fetish / Kinky", "10"))
		self.genreliste.append(("Fucking / Sucking", "26"))
		self.genreliste.append(("Hairy", "7"))
		self.genreliste.append(("Interracial", "15"))
		self.genreliste.append(("Lesbian", "6"))
		self.genreliste.append(("Lingerie / Panties", "30"))
		self.genreliste.append(("Nudist / Voyeur / Public", "16"))
		self.genreliste.append(("Other", "28"))
		self.genreliste.append(("Swingers / Gangbang", "8"))
		self.chooseMenuList.setList(map(eroprofileGenreListEntry, self.genreliste))
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
			streamSearchString = ""
			streamGenreID = self['genreList'].getCurrent()[0][1]
			self.session.open(eroprofileFilmScreen, streamSearchString, streamGenreID)

	def suchen(self):
		self.session.openWithCallback(self.SuchenCallback, VirtualKeyBoard, title = (_("Suchkriterium eingeben")), text = self.suchString)

	def SuchenCallback(self, callback = None, entry = None):
		if callback is not None and len(callback):
			self.suchString = callback.replace(' ', '+')
			streamSearchString = self.suchString
			streamGenreID = ""
			self.session.open(eroprofileFilmScreen, streamSearchString, streamGenreID)

	def keyLeft(self):
		if self.keyLocked:
			return
		self['genreList'].pageUp()

	def keyRight(self):
		if self.keyLocked:
			return
		self['genreList'].pageDown()

	def keyUp(self):
		if self.keyLocked:
			return
		self['genreList'].up()

	def keyDown(self):
		if self.keyLocked:
			return
		self['genreList'].down()

	def keyCancel(self):
		self.close()

class eroprofileFilmScreen(Screen):

	def __init__(self, session, phSearchString, phCatID):
		self.session = session
		self.SearchString = phSearchString
		self.phCatID = phCatID
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

		self['title'] = Label("EroProfile.com")
		self['name'] = Label("Film Auswahl")
		self['views'] = Label("")
		self['runtime'] = Label("")
		self['page'] = Label("")
		self['coverArt'] = Pixmap()
		self.keyLocked = True
		self.page = 1
		self.lastpage = 1
		self.suchString = ''

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
		if self.phCatID == "":
			url = 'http://www.eroprofile.com/m/videos/home?text=%s&pnum=%s' % (self.SearchString, str(self.page))
		elif self.phCatID == "home":
			url = 'http://www.eroprofile.com/m/videos/home?text=%s&pnum=%s' % (self.SearchString, str(self.page))
		elif self.phCatID == "popular":
			url = 'http://www.eroprofile.com/m/videos/popular/month?text=%s&pnum=%s' % (self.SearchString, str(self.page))
		else:
			url = 'http://www.eroprofile.com/m/videos/niche/%s/?text=%s&pnum=%s' % (self.phCatID, self.SearchString, str(self.page))
		print url
		getPage(url, headers={'Cookie': 'hideNiches=9%2C2%2C3%2C1%2C29%2C31%2C4%2C21%2C22%2C25', 'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.loadData).addErrback(self.dataError)

	def loadData(self, data):
		lastp = re.search('class="maxW"><tr><td><b>(.*?)</b>\sresults</td>', data, re.S)
		if lastp:
			lastp = round((float(lastp.group(1)) / 12) + 0.5)
			print lastp
			self.lastpage = int(lastp)
		else:
			self.lastpage = 1
		self['page'].setText(str(self.page) + ' / ' + str(self.lastpage))
		phMovies = re.findall('class="video">.*?img\ssrc="(.*?)".*?class="title"><a\shref="(.*?)">(.*?)</a.*?class="duration">(.*?)</div>', data, re.S)
		if phMovies:
			for (phImage, phUrl, phTitle, phRuntime) in phMovies:
				self.filmliste.append((decodeHtml(phTitle), phUrl, phImage.replace('amp;',''), phRuntime))
			if self.page == 1:
				self.filmliste.insert(0, ("--- Search ---", None, None, None))
			self.chooseMenuList.setList(map(eroprofileFilmListEntry, self.filmliste))
			self.chooseMenuList.moveToIndex(0)
			self.keyLocked = False
			self.showInfos()

	def dataError(self, error):
		printl(error,self,"E")

	def showInfos(self):
		phTitle = self['genreList'].getCurrent()[0][0]
		phImage = self['genreList'].getCurrent()[0][2]
		ptRuntime = self['genreList'].getCurrent()[0][3]
		self['name'].setText(phTitle)
		self['runtime'].setText(ptRuntime)
		if not phImage == None:
			downloadPage(phImage, "/tmp/Icon.jpg").addCallback(self.ShowCover)
		else:
			self.ShowCoverNone()

	def ShowCover(self, picData):
		picPath = "/tmp/Icon.jpg"
		self.ShowCoverFile(picPath)

	def ShowCoverNone(self):
		picPath = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/%s/images/no_coverArt.png" % config.mediaportal.skin.value
		self.ShowCoverFile(picPath)

	def ShowCoverFile(self, picPath):
		if fileExists(picPath):
			self['coverArt'].instance.setPixmap(gPixmapPtr())
			self.scale = AVSwitch().getFramebufferScale()
			self.picload = ePicLoad()
			size = self['coverArt'].instance.size()
			self.picload.setPara((size.width(), size.height(), self.scale[0], self.scale[1], False, 1, "#FF000000"))
			if self.picload.startDecode(picPath, 0, 0, False) == 0:
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
				self.loadpage()
			else:
				self.page = self.lastpage
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
		if self.page < self.lastpage:
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
		phTitle = self['genreList'].getCurrent()[0][0]
		if phTitle == "--- Search ---":
			self.suchen()
		else:
			phTitle = self['genreList'].getCurrent()[0][0]
			phLink = self['genreList'].getCurrent()[0][1]
			self.keyLocked = True
			phLink = 'http://www.eroprofile.com' + phLink
			getPage(phLink, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.getVideoPage).addErrback(self.dataError)

	def suchen(self):
		self.session.openWithCallback(self.SuchenCallback, VirtualKeyBoard, title = (_("Suchkriterium eingeben")), text = self.suchString)

	def SuchenCallback(self, callback = None, entry = None):
		if callback is not None and len(callback):
			self.suchString = callback.replace(' ', '+')
			self.SearchString = self.suchString
			self.loadpage()

	def getVideoPage(self, data):
		videoPage = re.findall('file:\'(.*?)\'', data, re.S)
		if videoPage:
			for phurl in videoPage:
				url = phurl
				self.keyLocked = False
				self.play(url)

	def play(self,file):
		xxxtitle = self['genreList'].getCurrent()[0][0]
		self.session.open(SimplePlayer, [(xxxtitle, file)], showPlaylist=False, ltype='eroprofile')

	def keyCancel(self):
		self.close()