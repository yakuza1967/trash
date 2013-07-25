#	-*-	coding:	utf-8	-*-

from Plugins.Extensions.MediaPortal.resources.imports import *
import Queue
import threading
from Plugins.Extensions.MediaPortal.resources.playhttpmovie import PlayHttpMovie
from Plugins.Extensions.MediaPortal.resources.simpleplayer import SimplePlayer
from Plugins.Extensions.MediaPortal.resources.twagenthelper import TwAgentHelper
from Plugins.Extensions.MediaPortal.resources.coverhelper import CoverHelper

if fileExists('/usr/lib/enigma2/python/Plugins/Extensions/TMDb/plugin.pyo'):
	from Plugins.Extensions.TMDb.plugin import *
	TMDbPresent = True
elif fileExists('/usr/lib/enigma2/python/Plugins/Extensions/IMDb/plugin.pyo'):
	TMDbPresent = False
	IMDbPresent = True
	from Plugins.Extensions.IMDb.plugin import *
else:
	IMDbPresent = False
	TMDbPresent = False

IS_Version = "iStream.ws v1.14"

IS_siteEncoding = 'utf-8'

"""
	Tastenfunktionen in der Filmliste:
		Bouquet +/-				: Seitenweise blättern in 1 Schritten Up/Down
		'1', '4', '7',
		'3', 6', '9'			: blättern in 2er, 5er, 10er Schritten Down/Up
		Grün/Gelb				: Sortierung [A-Z] bzw. [IMDB]
		INFO					: anzeige der IMDB-Bewertung

	Stream Auswahl:
		Rot/Blau				: Die Beschreibung Seitenweise scrollen

"""

def IStreamGenreListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 20, 0, 860, 25, 0, RT_HALIGN_CENTER | RT_VALIGN_CENTER, entry[0])
		]
class showIStreamGenre(Screen):

	def __init__(self, session, mode):
		self.session = session
		self.mode = mode
		self.plugin_path = mp_globals.pluginPath
		self.skin_path =  mp_globals.pluginPath + "/skins"

		path = "%s/%s/defaultGenreScreen.xml" % (self.skin_path, config.mediaportal.skin.value)
		if not fileExists(path):
			path = self.skin_path + "/original/defaultGenreScreen.xml"
		print path
		with open(path, "r") as f:
			self.skin = f.read()
			f.close()

		Screen.__init__(self, session)

		self["actions"] = ActionMap(["OkCancelActions", "ShortcutActions", "WizardActions", "ColorActions", "SetupActions", "NumberActions", "MenuActions", "EPGSelectActions"], {
			"ok"    : self.keyOK,
			"cancel": self.keyCancel
		}, -1)

		self['title'] = Label(IS_Version)
		self['ContentTitle'] = Label("M e n ü")
		self['name'] = Label("Genre Auswahl")
		self['F1'] = Label("")
		self['F2'] = Label("")
		self['F3'] = Label("")
		self['F4'] = Label("")

		self.param_search = ""
		self.keyLocked = True
		self.genreListe = []
		self.keckse = {}
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['genreList'] = self.chooseMenuList

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		print "ISteam.ws:"
		genreListe = []
		if self.mode == "porn":
			Genre = [
				("All", "http://istream.ws/c/porn/page/"),
				("German", "http://istream.ws/c/porn/deutsch/page/"),
				("AbbyWinters", "http://istream.ws/c/clips/abbywinters/page/"),
				("X-Art", "http://istream.ws/c/porn/x-art-porn/page/")]
		else:
			Genre = [
				("Suche...", "http://istream.ws/?s=%s"),
				("Kino", "http://istream.ws/c/filme/kino/page/"),
				("Neue Filme", "http://istream.ws/page/"),
				("Alle Filme", "http://istream.ws/c/filme/page/"),
				("Abenteuer", "http://istream.ws/c/filme/abenteuer/page/"),
				("Action", "http://istream.ws/c/filme/action/page/"),
				("Adventure", "http://istream.ws/c/filme/adventure/page/"),
				("Animation", "http://istream.ws/c/filme/animation/page/"),
				("Anime", "http://istream.ws/c/filme/anime/page/"),
				("Bollywood", "http://istream.ws/c/filme/bollywood/page/"),
				("Comedy", "http://istream.ws/c/filme/comedy/page/"),
				("Crime", "http://istream.ws/c/filme/crime/page/"),
				("Dokumentation", "http://istream.ws/c/filme/dokumentation/page/"),
				("Drama", "http://istream.ws/c/filme/drama/page/"),
				("Family", "http://istream.ws/c/filme/family/page/"),
				("Fantasy", "http://istream.ws/c/filme/fantasy/page/"),
				("Historienfilm", "http://istream.ws/c/filme/historienfilm/page/"),
				("History", "http://istream.ws/c/filme/history/page/"),
				("Horror", "http://istream.ws/c/filme/horror/page/"),
				("Kinderfilm", "http://istream.ws/c/filme/kinderfilm/page/"),
				("Komödie", "http://istream.ws/c/filme/komodie/page/"),
				("Kriegsfilm", "http://istream.ws/c/filme/kriegsfilm/page/"),
				("Kurzfilm", "http://istream.ws/c/filme/kurzfilm/page/"),
				("Martial Arts", "http://istream.ws/c/filme/martial-arts/page/"),
				("Mystery", "http://istream.ws/c/filme/mystery/page/"),
				("Romance", "http://istream.ws/c/filme/romance/page/"),
				("Satire", "http://istream.ws/c/filme/satire/page/"),
				("SciFi", "http://istream.ws/c/filme/science-ficton/page/"),
				("Sitcom", "http://istream.ws/c/filme/sitcom/page/"),
				("Sport", "http://istream.ws/c/filme/sport/page/"),
				("Thriller", "http://istream.ws/c/filme/thriller/page/"),
				("Trickfilm", "http://istream.ws/c/filme/trickfilm/page/"),
				("War", "http://istream.ws/c/filme/war/page/"),
				("Western", "http://istream.ws/c/filme/western/page/")]

		for (Name,Url) in Genre:
			self.genreListe.append((Name,Url))

		self.chooseMenuList.setList(map(IStreamGenreListEntry, self.genreListe))
		self.keyLocked = False


	def cb_Search(self, callback = None, entry = None):
		if callback != None:
			self.param_search = callback.strip()
			words = re.split('[^a-zA-Z0-9äÄöÖüÜß]+', self.param_search)
			s = ""
			j = len(words)
			i = 0
			if not j:
				return

			for word in words:
				i += 1
				if word != '':
					s += urllib.quote(word)
				if i < (j-1):
					s += '+'

			genreName = 'Videosuche: ' + self.param_search
			genreLink = self['genreList'].getCurrent()[0][1] % s
			print genreLink
			self.session.open(IStreamFilmListeScreen, genreLink, genreName)

	def keyOK(self):
		if self.keyLocked:
			return
		genreName = self['genreList'].getCurrent()[0][0]
		genreLink = self['genreList'].getCurrent()[0][1]
		print genreLink
		if re.match('.*?Suche...',genreName):
			self.session.openWithCallback(self.cb_Search, VirtualKeyBoard, title = (_("Suchanfrage")), text = self.param_search)
		else:
			self.session.open(IStreamFilmListeScreen, genreLink, genreName)

	def keyCancel(self):
		self.close()

def IStreamFilmListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 20, 0, 860, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry[0])
		]
class IStreamFilmListeScreen(Screen):

	def __init__(self, session, genreLink, genreName):
		self.session = session
		self.genreLink = genreLink
		self.genreName = genreName

		self.plugin_path = mp_globals.pluginPath
		self.skin_path =  mp_globals.pluginPath + "/skins"

		path = "%s/%s/defaultListScreen.xml" % (self.skin_path, config.mediaportal.skin.value)
		if not fileExists(path):
			path = self.skin_path + "/original/defaultListScreen.xml"

		print path
		with open(path, "r") as f:
			self.skin = f.read()
			f.close()

		Screen.__init__(self, session)

		self["actions"]  = ActionMap(["OkCancelActions", "ShortcutActions", "ColorActions", "SetupActions", "NumberActions", "MenuActions", "EPGSelectActions","DirectionActions"], {
			"ok"    : self.keyOK,
			"cancel": self.keyCancel,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft,
			"upUp" : self.key_repeatedUp,
			"rightUp" : self.key_repeatedUp,
			"leftUp" : self.key_repeatedUp,
			"downUp" : self.key_repeatedUp,
			"upRepeated" : self.keyUpRepeated,
			"downRepeated" : self.keyDownRepeated,
			"rightRepeated" : self.keyRightRepeated,
			"leftRepeated" : self.keyLeftRepeated,
			"nextBouquet" : self.keyPageUp,
			"prevBouquet" : self.keyPageDown,
			"1" : self.key_1,
			"3" : self.key_3,
			"4" : self.key_4,
			"6" : self.key_6,
			"7" : self.key_7,
			"9" : self.key_9,
			"yellow" : self.keySort,
			"red" :  self.keyTxtPageUp,
			"blue" :  self.keyTxtPageDown,
			"info" :  self.keyTMDbInfo
		}, -1)

		self.sortOrder = 0;
		self.sortParStr = ["", "?orderby=title&order=ASC", "?imdb_rating=desc"]
		self.genreTitle = "Filme in Genre "
		self.sortOrderStr = [" - Sortierung neuste", " - Sortierung A-Z", " - Sortierung IMDb"]
		self.sortOrderStrGenre = ""
		self['title'] = Label(IS_Version)
		self['ContentTitle'] = Label("")
		self['name'] = Label("")
		self['handlung'] = ScrollLabel("")
		self['coverArt'] = Pixmap()
		self['Page'] = Label("Page")
		self['page'] = Label("")
		self['F1'] = Label("Text-")
		self['F2'] = Label("")
		self['F3'] = Label("Sortierung")
		self['F4'] = Label("Text+")

		self.tw_agent_hlp = TwAgentHelper()
		self.timerStart = False
		self.seekTimerRun = False
		self.eventL = threading.Event()
		self.eventH = threading.Event()
		self.eventP = threading.Event()
		self.filmQ = Queue.Queue(0)
		self.hanQ = Queue.Queue(0)
		self.picQ = Queue.Queue(0)
		self.updateP = 0
		self.keyLocked = True
		self.filmListe = []
		self.keckse = {}
		self.page = 0
		self.pages = 0;
		self.neueFilme = re.match('.*?Neue Filme',self.genreName)
		self.sucheFilme = re.match('.*?Videosuche',self.genreName)
		self.setGenreStrTitle()

		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['liste'] = self.chooseMenuList

		self.onLayoutFinish.append(self.loadPage)

	def setGenreStrTitle(self):
		if not self.neueFilme and not self.sucheFilme:
			self.sortOrderStrGenre = self.sortOrderStr[self.sortOrder]
		else:
			self.sortOrderStrGenre = ""
		self['ContentTitle'].setText("%s%s%s" % (self.genreTitle,self.genreName,self.sortOrderStrGenre))

	def loadPage(self):
		print "loadPage:"
		if not self.sucheFilme:
			url = "%s%d%s" % (self.genreLink, self.page, self.sortParStr[self.sortOrder])
		else:
			url = self.genreLink

		if self.page:
			self['page'].setText("%d / %d" % (self.page,self.pages))

		self.filmQ.put(url)
		print "eventL ",self.eventL.is_set()
		if not self.eventL.is_set():
			self.eventL.set()
			self.loadPageQueued()
		else:
			self['name'].setText('Bitte warten...')
			self['handlung'].setText("")
			self['coverArt'].hide()

		print "eventL ",self.eventL.is_set()

	def loadPageQueued(self):
		print "loadPageQueued:"
		self['name'].setText('Bitte warten...')
		self['handlung'].setText("")
		self['coverArt'].hide()

		while not self.filmQ.empty():
			url = self.filmQ.get_nowait()
		print url
		self.tw_agent_hlp.getWebPage(self.loadPageData, self.dataError, url, False)

	def dataError(self, error):
		self.eventL.clear()
		print "dataError:"
		printl(error,self,"E")
		self.filmListe.append(("No movies found !",""))
		self.chooseMenuList.setList(map(IStreamFilmListEntry,	self.filmListe))

	def loadPageData(self, data):
		print "loadPageData:",len(data)

		self.filmListe = []
		if not self.neueFilme:
			filme = re.findall('<div class="cover">.*?<a href="(.*?)" rel=.*?title="(.*?)">.*?data-original="(.*?)"', data, re.S)
		else:
			print "Parse new movies"
			filme = re.findall('<div class="voting".*?<a href="(.*?)".*?title="(.*?)">.*?data-original="(.*?)"', data)

		if filme:
			print "Movies found !"
			if not self.pages:
				m = re.findall('<span class=\'pages\'>Seite 1 von (.*?)</', data)
				if m:
					self.pages = int(m[0])
				else:
					self.pages = 1

				self.page = 1
				print "Page: %d / %d" % (self.page,self.pages)
				self['page'].setText("%d / %d" % (self.page,self.pages))

			for	(url,name,imageurl) in filme:
				#print	"Url: ", url, "Name: ", name, "ImgUrl: ", imageurl
				self.filmListe.append((decodeHtml(name), url, imageurl))

			self.chooseMenuList.setList(map(IStreamFilmListEntry,	self.filmListe))
			self.keyLocked = False
			self.loadPicQueued()
		else:
			print "No movies found !"
			self.filmListe.append(("No movies found !",""))
			self.chooseMenuList.setList(map(IStreamFilmListEntry,	self.filmListe))
			if self.filmQ.empty():
				self.eventL.clear()
			else:
				self.loadPageQueued()

	def loadPicQueued(self):
		print "loadPicQueued:"
		self.picQ.put(None)
		if not self.eventP.is_set():
			self.eventP.set()
			self.loadPic()
		print "eventP: ",self.eventP.is_set()

	def loadPic(self):
		print "loadPic:"

		if self.picQ.empty():
			self.eventP.clear()
			print "picQ is empty"
			return

		if self.eventH.is_set() or self.updateP:
			print "Pict. or descr. update in progress"
			print "eventH: ",self.eventH.is_set()
			print "eventP: ",self.eventP.is_set()
			print "updateP: ",self.updateP
			return

		while not self.picQ.empty():
			self.picQ.get_nowait()

		streamName = self['liste'].getCurrent()[0][0]
		self['name'].setText(streamName)
		streamPic = self['liste'].getCurrent()[0][2]

		streamUrl = self['liste'].getCurrent()[0][1]
		self.getHandlung(streamUrl)
		self.updateP = 1
		CoverHelper(self['coverArt'], self.showCoverExit).getCover(streamPic)

	def dataErrorP(self, error):
		print "dataError:"
		printl(error,self,"E")
		self.ShowCoverNone()

	def getHandlung(self, url):
		print "getHandlung:"
		if url == None:
			print "No Infos found !"
			self['handlung'].setText("Keine Infos gefunden.")
			return

		self.hanQ.put(url)
		if not self.eventH.is_set():
			self.eventH.set()
			self.getHandlungQeued()
		print "eventH: ",self.eventH.is_set()

	def getHandlungQeued(self):
		while not self.hanQ.empty():
			url = self.hanQ.get_nowait()
		#print url
		self.tw_agent_hlp.getWebPage(self.setHandlung, self.dataErrorH, url, False)

	def dataErrorH(self, error):
		self.eventH.clear()
		print "dataErrorH:"
		printl(error,self,"E")
		self['handlung'].setText("Keine Infos gefunden.")

	def setHandlung(self, data):
		print "setHandlung:"

		m = re.findall('meta property="og:description".*?=\'(.*?)\' />', data)
		if m:
			self['handlung'].setText(decodeHtml(re.sub(r"\s+", " ", m[0])))
		else:
			print "No Infos found !"
			self['handlung'].setText("Keine Infos gefunden.")

		if not self.hanQ.empty():
			self.getHandlungQeued()
		else:
			self.eventH.clear()
			self.loadPic()
		print "eventH: ",self.eventH.is_set()
		print "eventL: ",self.eventL.is_set()

	def showCoverExit(self):
		self.updateP = 0;
		if not self.filmQ.empty():
			self.loadPageQueued()
		else:
			self.eventL.clear()
			self.loadPic()

	def keyOK(self):
		if self.keyLocked or self.eventL.is_set():
			return

		streamLink = self['liste'].getCurrent()[0][1]
		streamName = self['liste'].getCurrent()[0][0]
		imageLink = self['liste'].getCurrent()[0][2]
		self.session.open(IStreamStreams, streamLink, streamName, imageLink)

	def keyUp(self):
		if self.keyLocked:
			return
		self['liste'].up()

	def keyDown(self):
		if self.keyLocked:
			return
		self['liste'].down()

	def keyUpRepeated(self):
		#print "keyUpRepeated"
		if self.keyLocked:
			return
		self['coverArt'].hide()
		self['liste'].up()

	def keyDownRepeated(self):
		#print "keyDownRepeated"
		if self.keyLocked:
			return
		self['coverArt'].hide()
		self['liste'].down()

	def key_repeatedUp(self):
		#print "key_repeatedUp"
		if self.keyLocked:
			return
		self.loadPicQueued()

	def keyLeft(self):
		if self.keyLocked:
			return
		self['liste'].pageUp()

	def keyRight(self):
		if self.keyLocked:
			return
		self['liste'].pageDown()

	def keyLeftRepeated(self):
		if self.keyLocked:
			return
		self['coverArt'].hide()
		self['liste'].pageUp()

	def keyRightRepeated(self):
		if self.keyLocked:
			return
		self['coverArt'].hide()
		self['liste'].pageDown()

	def keyPageDown(self):
		#print "keyPageDown()"
		if self.seekTimerRun:
			self.seekTimerRun = False
		self.keyPageDownFast(1)

	def keyPageUp(self):
		#print "keyPageUp()"
		if self.seekTimerRun:
			self.seekTimerRun = False
		self.keyPageUpFast(1)

	def keyPageUpFast(self,step):
		if self.keyLocked:
			return
		#print "keyPageUpFast: ",step
		oldpage = self.page
		if (self.page + step) <= self.pages:
			self.page += step
		else:
			self.page = 1
		#print "Page %d/%d" % (self.page,self.pages)
		if oldpage != self.page:
			self.loadPage()

	def keyPageDownFast(self,step):
		if self.keyLocked:
			return
		print "keyPageDownFast: ",step
		oldpage = self.page
		if (self.page - step) >= 1:
			self.page -= step
		else:
			self.page = self.pages
		#print "Page %d/%d" % (self.page,self.pages)
		if oldpage != self.page:
			self.loadPage()

	def key_1(self):
		#print "keyPageDownFast(2)"
		self.keyPageDownFast(2)

	def key_4(self):
		#print "keyPageDownFast(5)"
		self.keyPageDownFast(5)

	def key_7(self):
		#print "keyPageDownFast(10)"
		self.keyPageDownFast(10)

	def key_3(self):
		#print "keyPageUpFast(2)"
		self.keyPageUpFast(2)

	def key_6(self):
		#print "keyPageUpFast(5)"
		self.keyPageUpFast(5)

	def key_9(self):
		#print "keyPageUpFast(10)"
		self.keyPageUpFast(10)

	def keySort(self):
		if (self.keyLocked):
			return
		if not self.neueFilme:
			if self.sortOrder < 2:
				self.sortOrder += 1
			else:
				self.sortOrder = 0
			self.setGenreStrTitle()
			self.loadPage()

	def keyTMDbInfo(self):
		if not self.keyLocked and TMDbPresent:
			title = self['liste'].getCurrent()[0][0]
			self.session.open(TMDbMain, title)
		elif not self.keyLocked and IMDbPresent:
			title = self['liste'].getCurrent()[0][0]
			self.session.open(IMDB, title)

	def keyTxtPageUp(self):
		self['handlung'].pageUp()

	def keyTxtPageDown(self):
		self['handlung'].pageDown()

	def keyCancel(self):
		self.close()

def IStreamStreamListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 20, 0, 860, 25, 0, RT_HALIGN_CENTER | RT_VALIGN_CENTER, entry[0]+entry[2])
		]
class IStreamStreams(Screen, ConfigListScreen):

	def __init__(self, session, filmUrl, filmName, imageLink):
		self.session = session
		self.filmUrl = filmUrl
		self.filmName = filmName
		self.imageUrl = imageLink

		self.plugin_path = mp_globals.pluginPath
		self.skin_path =  mp_globals.pluginPath + "/skins"

		path = "%s/%s/defaultListScreen.xml" % (self.skin_path, config.mediaportal.skin.value)
		if not fileExists(path):
			path = self.skin_path + "/original/defaultListScreen.xml"

		print path
		with open(path, "r") as f:
			self.skin = f.read()
			f.close()

		Screen.__init__(self, session)

		self["actions"]  = ActionMap(["OkCancelActions", "ShortcutActions", "EPGSelectActions", "WizardActions", "ColorActions", "NumberActions", "MenuActions", "MoviePlayerActions", "InfobarSeekActions"], {
			"red" 		: self.keyTxtPageUp,
			"blue" 		: self.keyTxtPageDown,
			"ok"    	: self.keyOK,
			"info" 		: self.keyTMDbInfo,
			"cancel"	: self.keyCancel
		}, -1)

		self['title'] = Label(IS_Version)
		self['ContentTitle'] = Label("Stream Auswahl")
		self['coverArt'] = Pixmap()
		self['handlung'] = ScrollLabel("")
		self['name'] = Label(filmName)
		self['Page'] = Label("")
		self['page'] = Label("")
		self['F1'] = Label("Text-")
		self['F2'] = Label("")
		self['F3'] = Label("")
		self['F4'] = Label("Text+")

		self.tw_agent_hlp = TwAgentHelper()
		self.streamListe = []
		self.streamMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.streamMenuList.l.setFont(0, gFont('mediaportal', 24))
		self.streamMenuList.l.setItemHeight(25)
		self['liste'] = self.streamMenuList
		self.keyLocked = True
		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		print "loadPage:"
		streamUrl = self.filmUrl
		#print "FilmUrl: %s" % self.filmUrl
		#print "FilmName: %s" % self.filmName
		self.tw_agent_hlp.getWebPage(self.parseData, self.dataError, streamUrl, False)

	def parseData(self, data):
		print "parseData:"
		streams = re.findall('a class="hoster-button.*?href="(.*?)".*?title=".*?\[(.*?)\](.*?)"', data)
		mdesc = re.search('class="desc">(.*?)<br />',data, re.S)
		if mdesc:
			print "Descr. found"
			desc = mdesc.group(1).strip()
		else:
			desc = "Keine weiteren Info's !"

		self.streamListe = []
		if streams:
			print "Streams found"
			for (isUrl,isStream,streamPart) in streams:
				if re.match('.*?(putlocker|sockshare|flash strea|streamclou|xvidstage|filenuke|movreel|nowvideo|xvidstream|uploadc|vreer|MonsterUploads|Novamov|Videoweed|Divxstage|Ginbig|Flashstrea|Movshare|yesload|faststream|Vidstream|PrimeShare|flashx|Divxmov|Putme|Zooupload|Click.*?Play|BitShare)', isStream, re.S|re.I):
					#print isUrl
					#print isStream,streamPart
					self.streamListe.append((isStream,isUrl,streamPart))
				else:
					print "No supported hoster:"
					print isStream
					print isUrl
		else:
			print "No Streams found"
			self.streamListe.append(("No streams found!","",""))

		self.streamMenuList.setList(map(IStreamStreamListEntry, self.streamListe))
		self['handlung'].setText(decodeHtml(desc))
		self.keyLocked = False
		print "imageUrl: ",self.imageUrl
		CoverHelper(self['coverArt']).getCover(self.imageUrl)

	def dataError(self, error):
		print "dataError:"
		printl(error,self,"E")
		self.streamListe.append(("Read error !",""))
		self.streamMenuList.setList(map(IStreamStreamListEntry, self.streamListe))

	def got_link(self, stream_url):
		print "got_link:"
		if stream_url == None:
			message = self.session.open(MessageBox, _("Stream not found, try another Stream Hoster."), MessageBox.TYPE_INFO, timeout=3)
		else:
			title = self.filmName + self['liste'].getCurrent()[0][2]
			if config.mediaportal.useHttpDump.value:
				movieinfo = [stream_url,self.filmName,""]
				self.session.open(PlayHttpMovie, movieinfo, title)
			else:
				self.session.open(SimplePlayer, [(title, stream_url, self.imageUrl)], cover=True, showPlaylist=False, ltype='istream.ws')

	def keyTMDbInfo(self):
		if TMDbPresent:
			self.session.open(TMDbMain, self.filmName)
		elif IMDbPresent:
			self.session.open(IMDB, self.filmName)

	def keyOK(self):
		if self.keyLocked:
			return
		streamLink = self['liste'].getCurrent()[0][1]
		self.tw_agent_hlp.getRedirectedUrl(self.keyOK2, self.dataError, streamLink)

	def keyOK2(self, streamLink):
		saveads = re.search('.*?saveads.org', streamLink, re.S)
		if saveads:
			id = re.search('url=(.*?)%3D', streamLink, re.S)
			url = "http://istream.ws/go.php?url=" + id.group(1)
			self.tw_agent_hlp.getRedirectedUrl(self.keyOK3, self.dataError, url)
		else:
			get_stream_link(self.session).check_link(streamLink, self.got_link)

	def keyOK3(self, streamLink):
		get_stream_link(self.session).check_link(streamLink, self.got_link)

	def keyTxtPageUp(self):
		self['handlung'].pageUp()

	def keyTxtPageDown(self):
		self['handlung'].pageDown()

	def keyCancel(self):
		self.close()
