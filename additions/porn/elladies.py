from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.simpleplayer import SimplePlayer

def elladiesGenreListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 20, 0, 900, 25, 0, RT_HALIGN_CENTER | RT_VALIGN_CENTER, entry[0])
		]

def elladiesFilmListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 20, 0, 900, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry[0])
		]

class elladiesGenreScreen(Screen):

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

		self['title'] = Label("El-Ladies.com")
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
		self.genreliste.append(("All", ""))
		self.genreliste.append(("3some", "1"))
		self.genreliste.append(("Amateur", "2"))
		self.genreliste.append(("Anal", "3"))
		self.genreliste.append(("Anime-toons", "5"))
		self.genreliste.append(("Asian", "6"))
		self.genreliste.append(("Ass", "7"))
		self.genreliste.append(("Babe", "8"))
		self.genreliste.append(("BDSM", "9"))
		self.genreliste.append(("Big Cock", "10"))
		self.genreliste.append(("Big Lady", "11"))
		self.genreliste.append(("Big Tits", "12"))
		self.genreliste.append(("Bisex", "13"))
		self.genreliste.append(("Blowjob", "47"))
		self.genreliste.append(("Bondage", "15"))
		self.genreliste.append(("Celeb", "16"))
		self.genreliste.append(("Cumsex", "17"))
		self.genreliste.append(("Dildo", "18"))
		self.genreliste.append(("Drunk", "53"))
		self.genreliste.append(("Ebony", "19"))
		self.genreliste.append(("Extreme", "20"))
		self.genreliste.append(("Facials", "21"))
		self.genreliste.append(("Fetish", "22"))
		self.genreliste.append(("Fisting", "23"))
		self.genreliste.append(("Gangbang", "28"))
		self.genreliste.append(("Granny", "30"))
		self.genreliste.append(("Group", "31"))
		self.genreliste.append(("Hairy", "24"))
		self.genreliste.append(("Hardcore", "25"))
		self.genreliste.append(("Horny", "55"))
		self.genreliste.append(("Indian", "26"))
		self.genreliste.append(("Interracial", "27"))
		self.genreliste.append(("Kinky", "61"))
		self.genreliste.append(("Latex", "32"))
		self.genreliste.append(("Latina", "50"))
		self.genreliste.append(("Lesbian", "33"))
		self.genreliste.append(("Lingerie", "34"))
		self.genreliste.append(("Mature", "35"))
		self.genreliste.append(("Mom", "51"))
		self.genreliste.append(("Old & Young", "36"))
		self.genreliste.append(("Orgasm", "56"))
		self.genreliste.append(("Orgy", "63"))
		self.genreliste.append(("Outdoor", "60"))
		self.genreliste.append(("Panties", "48"))
		self.genreliste.append(("Party", "37"))
		self.genreliste.append(("Pregnant", "39"))
		self.genreliste.append(("Pussy", "59"))
		self.genreliste.append(("Shaved", "58"))
		self.genreliste.append(("Slave", "42"))
		self.genreliste.append(("Slut", "54"))
		self.genreliste.append(("Small Tits", "43"))
		self.genreliste.append(("Swingers", "62"))
		self.genreliste.append(("Teens", "44"))
		self.genreliste.append(("Toons", "45"))
		self.genreliste.append(("Vintage", "46"))
		self.genreliste.append(("Voyeur", "57"))
		self.chooseMenuList.setList(map(elladiesGenreListEntry, self.genreliste))
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
			self.session.open(elladiesFilmScreen, streamSearchString, streamGenreID)

	def suchen(self):
		self.session.openWithCallback(self.SuchenCallback, VirtualKeyBoard, title = (_("Suchkriterium eingeben")), text = self.suchString)

	def SuchenCallback(self, callback = None, entry = None):
		if callback is not None and len(callback):
			self.suchString = callback.replace(' ', '+')
			streamSearchString = self.suchString
			streamGenreID = ""
			self.session.open(elladiesFilmScreen, streamSearchString, streamGenreID)

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

class elladiesFilmScreen(Screen):

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
			"yellow" : self.keyHD,
			"green" : self.keyPageNumber
		}, -1)

		self['title'] = Label("El-Ladies.com")
		self['name'] = Label("Film Auswahl")
		self['views'] = Label("")
		self['runtime'] = Label("")
		self['page'] = Label("")
		self['coverArt'] = Pixmap()
		self.keyLocked = True
		self.page = 1
		self.lastpage = 1
		self.suchString = ''
		self.HD = 0
		self.HDText = ['Off','On']
		self['title'].setText('El-Ladies.com (HD: ' + self.HDText[self.HD] + ')')

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
		url = 'http://search.el-ladies.com/?search=%s&fun=0&niche=%s&pnum=%s&hd=%s' % (self.SearchString, self.phCatID, str(self.page), self.HD)
		print url
		getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.loadData).addErrback(self.dataError)

	def loadData(self, data):
		lastp = re.search('.*pnum=(.*?)"', data, re.S)
		if lastp:
			lastp = lastp.group(1)
			print lastp
			self.lastpage = int(lastp)
		else:
			self.lastpage = 1
		self['page'].setText(str(self.page) + ' / ' + str(self.lastpage))
		phMovies = re.findall('<a\shref="http://just.eroprofile.com/play/(.*?)".*?<img\ssrc="(.*?)".*?<div>(.*?)</div>', data, re.S)
		if phMovies:
			for (phID, phImage, phCat) in phMovies:
				phTitle = decodeHtml(phCat) + ' - ' + phID
				self.filmliste.append((phTitle, phID, phImage))
			if self.page == 1:
				self.filmliste.insert(0, ("--- Search ---", None, None))
			self.chooseMenuList.setList(map(elladiesFilmListEntry, self.filmliste))
			self.chooseMenuList.moveToIndex(0)
			self.keyLocked = False
			self.showInfos()

	def dataError(self, error):
		printl(error,self,"E")

	def showInfos(self):
		phTitle = self['genreList'].getCurrent()[0][0]
		phImage = self['genreList'].getCurrent()[0][2]
		self['name'].setText(phTitle)
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

	def keyHD(self):
		if self.HD == 1:
			self.HD = 0
		else:
			self.HD = 1
		self['title'].setText('El-Ladies.com (HD: ' + self.HDText[self.HD] + ')')
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
			phLink = 'http://just.eroprofile.com/play/' + phLink
			getPage(phLink, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.getVideoPage).addErrback(self.dataError)

	def suchen(self):
		self.session.openWithCallback(self.SuchenCallback, VirtualKeyBoard, title = (_("Suchkriterium eingeben")), text = self.suchString)

	def SuchenCallback(self, callback = None, entry = None):
		if callback is not None and len(callback):
			self.suchString = callback.replace(' ', '+')
			self.SearchString = self.suchString
			self.loadpage()

	def getVideoPage(self, data):
		videoPage = re.findall('\'file\',.\'(.*?)\'', data, re.S)
		if videoPage:
			for phurl in videoPage:
				url = phurl
				self.keyLocked = False
				self.play(url)

	def play(self,file):
		xxxtitle = self['genreList'].getCurrent()[0][0]
		self.session.open(SimplePlayer, [(xxxtitle, file)], showPlaylist=False, ltype='elladies')

	def keyCancel(self):
		self.close()