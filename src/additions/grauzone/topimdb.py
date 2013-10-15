# -*- coding: utf-8 -*-
from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.coverhelper import CoverHelper

from kinoxto import *
from movie4k import *
from mlehd import *
from kinokiste import *

def timdbEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 0, 0, 70, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry[0]),
		(eListboxPythonMultiContent.TYPE_TEXT, 70, 0, 550, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry[1]),
		(eListboxPythonMultiContent.TYPE_TEXT, 620, 0, 100, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry[2]),
		(eListboxPythonMultiContent.TYPE_TEXT, 720, 0, 100, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry[3])
		]

class timdbGenreScreen(Screen):

	def __init__(self, session):
		self.session = session

		path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/%s/defaultListScreen.xml" % config.mediaportal.skin.value
		if not fileExists(path):
			path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/original/defaultListScreen.xml"
		print path
		with open(path, "r") as f:
			self.skin = f.read()
			f.close()

		Screen.__init__(self, session)

		self["actions"]  = ActionMap(["OkCancelActions", "ShortcutActions", "WizardActions", "ColorActions", "SetupActions", "NumberActions", "MenuActions", "EPGSelectActions"], {
		"ok"	: self.keyOK,
		"cancel": self.keyCancel,
		"up" : self.keyUp,
		"down" : self.keyDown,
		"right" : self.keyRight,
		"left" : self.keyLeft,
		"nextBouquet" : self.keyPageUp,
		"prevBouquet" : self.keyPageDown,
		"green" : self.kinoxSearch,
		"yellow" : self.movie4kSearch, 
		"blue" : self.mleSearch,
		"red" : self.kinokisteSearch
		}, -1)

		self['title'] = Label("Top IMDb")
		self['ContentTitle'] = Label("Auswahl:")
		self['name'] = Label("")
		self['F1'] = Label("KinoKiste")
		self['F2'] = Label("Kinox")
		self['F3'] = Label("Movie4k")
		self['F4'] = Label("MLE")
		self['coverArt'] = Pixmap()
		self['Page'] = Label("Page: ")
		self['page'] = Label("")
		self['handlung'] = Label("")

		self.keyLocked = True
		self.filmliste = []
		self.page = 1

		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['liste'] = self.chooseMenuList

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.keyLocked = True
		self.filmliste = []
		self.start = 1
		self.start = (self.page * 50) - 49

		url = "http://www.imdb.de/search/title?groups=top_1000&sort=user_rating,desc&start=%s" % str(self.start)
		print url
		getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded', 'User-agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0', 'Accept-Language':'de-de,de;q=0.8,en-us;q=0.5,en;q=0.3'}).addCallback(self.parseData).addErrback(self.dataError)

	def parseData(self, data):
		movies = re.findall('<td class="number">(.*?)</td>.*?<img src="(.*?)".*?<a href="/title/.*?">(.*?)</a>.*?<span class="year_type">(.*?)</span><br>.*?<div class="rating rating-list".*?title="Users rated this (.*?\/)', data, re.S)
		if movies:
			for place,image,title,year,rates in movies:
				rates = "%s10" % rates
				image_raw = image.split('@@')
				image = "%s@@._V1_SX214_.jpg" % image_raw[0]
				self.filmliste.append((place, decodeHtml(title), year, rates, image))
				self.chooseMenuList.setList(map(timdbEntry, self.filmliste))
			self.showInfos()
			self.keyLocked = False

	def dataError(self, error):
		printl(error,self,"E")

	def showInfos(self):
		coverUrl = self['liste'].getCurrent()[0][4]
		self['page'].setText("%s" % str(self.page))
		CoverHelper(self['coverArt']).getCover(coverUrl)

	def keyOK(self):
		if self.keyLocked:
			return

		self.searchTitle = self['liste'].getCurrent()[0][1]
		print self.searchTitle

	def kinokisteSearch(self):
		self.searchTitle = self['liste'].getCurrent()[0][1]
		self.session.openWithCallback(self.searchKinokisteCallback, VirtualKeyBoard, title = (_("kinokiste: Suche nach..")), text = self.searchTitle)

	def searchKinokisteCallback(self, callbackStr):
		if callbackStr is not None:
			url = "http://kkiste.to/search/?q=%s" % callbackStr.replace(' ','%20')
			self.session.open(kinokisteSearchScreen, url)

	
	def kinoxSearch(self):
		self.searchTitle = self['liste'].getCurrent()[0][1]
		self.session.openWithCallback(self.searchKinoxCallback, VirtualKeyBoard, title = (_("kinox: Suche nach..")), text = self.searchTitle)
		
	def searchKinoxCallback(self, callbackStr):
		if callbackStr is not None:
			url = "http://kinox.to/Search.html?q="
			self.session.open(kxSucheAlleFilmeListeScreen, url, callbackStr)

	def movie4kSearch(self):
		self.searchTitle = self['liste'].getCurrent()[0][1]
		self.session.openWithCallback(self.searchMovie4kCallback, VirtualKeyBoard, title = (_("movie4k: Suche nach..")), text = self.searchTitle)

	def searchMovie4kCallback(self, callbackStr):
		if callbackStr is not None:
			url = "http://www.movie4k.to/movies.php?list=search"
			self.session.open(m4kSucheAlleFilmeListeScreen, url, callbackStr)

	def mleSearch(self):
		self.searchTitle = self['liste'].getCurrent()[0][1]
		self.session.openWithCallback(self.searchMleCallback, VirtualKeyBoard, title = (_("mle: Suche nach..")), text = self.searchTitle)

	def searchMleCallback(self, callbackStr):
		if callbackStr is not None:
			url = "http://mle-hd.se/page/"
			self.session.open(mlehdFilmListeScreen, "Suche", url, callbackStr.replace(' ','%20'))
		
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

	def keyLeft(self):
		if self.keyLocked:
			return
		self['liste'].pageUp()
		self.showInfos()

	def keyRight(self):
		if self.keyLocked:
			return
		self['liste'].pageDown()
		self.showInfos()

	def keyUp(self):
		if self.keyLocked:
			return
		self['liste'].up()
		self.showInfos()

	def keyDown(self):
		if self.keyLocked:
			return
		self['liste'].down()
		self.showInfos()

	def keyCancel(self):
		self.close()