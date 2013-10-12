#	-*-	coding:	utf-8	-*-
#
# ARD-Mediathek von chroma_key
# v0.4
#
# GenreFlags (self.gF):
# 1 = ABC (TV)
# 2 = Suche (TV+Podcasts)
# 3 = Kategorien (TV)
# 4 = A-Z (Radio) <--- Gibt es noch nicht in der ARD-Mediathek
# 5 = Suche (Radio+Podcasts)
# 6 = Kategorien (Radio)
# 7 = Dossiers (TV+Radio)
# 8 = Reportage & Doku (TV)
# 9 = Film-Highlights (TV)
# 10 = Einzelne Sender (TV+Radio)
from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.playrtmpmovie import PlayRtmpMovie
from Plugins.Extensions.MediaPortal.resources.simpleplayer import SimplePlayer
from Plugins.Extensions.MediaPortal.resources.coverhelper import CoverHelper

# Globals
suchCache = ""
textTrigger = 0
mainLink = "http://www.ardmediathek.de"
tDef = "Keine Informationen/Angaben"
isWeg = "Leider nicht (mehr) auf den ARD-Servern vorhanden!"
helpText = "\n\nTipp:\nBei allen gefundenen Inhalten ist die 'INFO'-Taste belegt."
suchDef = decodeHtml("\nDiese Auswahl ist f&uuml;r die ARD-Server rechenintensiv,\nund kann daher einige Sekunden dauern...")
alienFound = "Kann nicht abgespielt werden! Entweder sind die Inhalte nicht mehr vorhanden, oder die Stream-Links werden auf Seiten \
der ARD-Server nun anders zusammengesetzt. In letzterem Fall muss auf ein Update dieses Plugins gewartet werden!"
placeHolder = ("---","99")

def ARDBody(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 20, 0, 900, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry[0])
		]

class ARDGenreScreen(Screen):

	def __init__(self, session):
		self.session = session
		path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/%s/RTLnowGenreScreen.xml" % config.mediaportal.skin.value
		if not fileExists(path):
			path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/original/RTLnowGenreScreen.xml"
		with open(path, "r") as f:
			self.skin = f.read()
			f.close()

		Screen.__init__(self, session)

		self["actions"]  = ActionMap(["OkCancelActions", "ShortcutActions", "WizardActions", "ColorActions", "SetupActions", "NumberActions", "MenuActions"], {
			"ok"    : self.keyOK,
			"cancel": self.keyCancel,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft
		}, -1)

		self['title'] = Label("ARD-Mediathek")
		self['name'] = Label("Auswahl des Genres")
		self['handlung'] = Label(helpText)
		self['Pic'] = Pixmap()

		self.genreliste = []
		self.keyLocked = True
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['List'] = self.chooseMenuList
		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.genreliste = []
		self.genreliste.append(("A bis Z  -  TV", "1"))
		self.genreliste.append(("Suche  -  TV", "2"))
		self.genreliste.append(("Kategorien  -  TV", "3"))
		#self.genreliste.append(("A bis Z  -  Radio", "4"))
		self.genreliste.append(("Suche  -  Radio", "5"))
		self.genreliste.append(("Kategorien  -  Radio", "6"))
		self.genreliste.append(("Dossiers  -  TV & Radio", "7"))
		self.genreliste.append(("Reportage & Doku  -  TV", "8"))
		self.genreliste.append(("Film-Highlights  -  TV", "9"))
		self.genreliste.append(placeHolder)
		self.genreliste.append(("Einzelne Sender  -  TV & Radio", "10"))
		self.chooseMenuList.setList(map(ARDBody, self.genreliste))
		self.keyLocked = False

	def dataError(self, error):
		printl(error,self,"E")

	def keyOK(self):
		if self.keyLocked:
			return
		genreName = self['List'].getCurrent()[0][0]
		genreFlag = self['List'].getCurrent()[0][1]
		if genreFlag == "99":
			return
		if genreFlag == "2" or genreFlag == "5": # Suche TV oder Radio
			self.session.openWithCallback(self.searchCallback, VirtualKeyBoard, title = (_("Suchbegriff eingeben")), text = suchCache)
		elif genreFlag == "7": # Dossiers
			auswahl = "dummy"
			self.session.open(ARDPostSelect,auswahl,genreName,genreFlag, "dummy")
		elif genreFlag == "8": # Reportage & Doku
			url = mainLink + "/ard/servlet/ajax-cache/3474718/view=switch/goto=%s/index.html"
			genreName = "Reportage+Doku"
			self.session.open(ARDStreamScreen,url,genreName,genreFlag)
		elif genreFlag == "9": # Film-Highlights
			url = mainLink + "/ard/servlet/ajax-cache/4585472/view=switch/goto=%s/index.html"
			genreName = "Film-Highlights"
			self.session.open(ARDStreamScreen,url,genreName,genreFlag)
		else: # ABC (TV oder Radio), Podcasts, Kategorien
			self.session.open(ARDPreSelect,genreName,genreFlag)

	def searchCallback(self, callbackStr):
		genreFlag = self['List'].getCurrent()[0][1]
		if callbackStr is not None:
			global suchCache
			suchCache = callbackStr
			self.searchStr = callbackStr
			genreName = "Suche... ' %s '" % self.searchStr
			self.searchStr = self.searchStr.replace(' ', '+')
			if genreFlag == "2":
				url = mainLink + "/suche?detail=40&s="+self.searchStr+"&inhalt=tv&goto=%s"
			elif genreFlag == "5":
				url = mainLink + "/suche?detail=40&s="+self.searchStr+"&inhalt=radio&goto=%s"
			self.session.open(ARDStreamScreen,url,genreName,genreFlag)

	def keyLeft(self):
		self['List'].pageUp()

	def keyRight(self):
		self['List'].pageDown()

	def keyUp(self):
		self['List'].up()

	def keyDown(self):
		self['List'].down()

	def keyCancel(self):
		self.close()

class ARDPreSelect(Screen):

	def __init__(self,session,genreName,genreFlag):
		self.session = session
		self.gN = genreName
		self.gF = genreFlag
		path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/%s/RTLnowGenreScreen.xml" % config.mediaportal.skin.value
		if not fileExists(path):
			path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/original/RTLnowGenreScreen.xml"
		with open(path, "r") as f:
			self.skin = f.read()
			f.close()

		Screen.__init__(self, session)

		self["actions"]  = ActionMap(["OkCancelActions", "ShortcutActions", "WizardActions", "ColorActions", "SetupActions", "NumberActions", "MenuActions"], {
			"ok"    : self.keyOK,
			"cancel": self.keyCancel,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft
		}, -1)

		self['title'] = Label("ARD-Mediathek")
		self['name'] = Label("Auswahl der Kategorie")
		self['handlung'] = Label(helpText)
		self['Pic'] = Pixmap()

		self.genreliste = []
		self.keyLocked = True
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['List'] = self.chooseMenuList

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		if self.gF == "1":
			self['name'].setText("Auswahl des Buchstabens")
			self.genreliste = []
			for c in xrange(26): # ABC, Radio+TV
				self.genreliste.append((chr(ord('A') + c), None))
			self.genreliste.insert(0, ('0-9', None))
			self.chooseMenuList.setList(map(ARDBody, self.genreliste))
			self.keyLocked = False
		elif self.gF == "3" or self.gF == "6":
			self.genreliste = []
			if self.gF == "6": # Extra-Kategorien, nur Radio
				self.genreliste.append(("Tipps der Redaktion", "1"))
				self.genreliste.append((decodeHtml("H&ouml;rspiel"), "2"))
			if self.gF == "3" or self.gF == "6": # Extra-Kategorien, Radio+TV
				self.genreliste.append(("Neueste Clips", "3"))
				self.genreliste.append(("Meistabgerufene Clips (heute)", "4"))
				self.genreliste.append(("Meistabgerufene Clips (gesamt)", "5"))
				self.genreliste.append(placeHolder)
				self.genreliste.append(("Nachrichten", "7"))	# Ab hier (incl.) Standard-Kategorien, Radio+TV
				self.genreliste.append(("Politik & Zeitgeschehen", "8"))
				self.genreliste.append((decodeHtml("Wirtschaft & B&ouml;rse"), "9"))
				self.genreliste.append(("Sport", "10"))
				self.genreliste.append(("Ratgeber & Technik", "11"))
				self.genreliste.append((decodeHtml("Gesundheit & Ern&auml;hrung"), "12"))
				self.genreliste.append(("Kultur & Gesellschaft", "13"))
				self.genreliste.append(("Musik", "14"))
				self.genreliste.append(("Literatur", "15"))
				self.genreliste.append(("Medien", "16"))
				self.genreliste.append(("Filme & Serien", "17"))
				self.genreliste.append(("Unterhaltung & Lifestyle", "18"))
				self.genreliste.append(("Comedy & Satire", "19"))
				self.genreliste.append(("Wissen & Bildung", "20"))
				self.genreliste.append(("Natur & Freizeit", "21"))
				self.genreliste.append(("Kinder & Familie", "22"))
				self.genreliste.append(("Religion & Kirche", "23"))
				self.genreliste.append(("In der Region", "24"))
				self.chooseMenuList.setList(map(ARDBody, self.genreliste))
				self.keyLocked = False
		elif self.gF == "10": # Einzelne Sender
			self['name'].setText("Auswahl des Senders")
			self.genreliste = []
			self.genreliste.append(("ARD - Das Erste", "30", "Das%20Erste", "Das%20Erste"))
			self.genreliste.append(placeHolder)
			self.genreliste.append(("BR - Bayerischer Rundfunk", "31", "Bayerischer%20Rundfunk", "br"))
			self.genreliste.append(("HR - Hessischer Rundfunk", "32", "Hessischer%20Rundfunk", "hr"))
			self.genreliste.append(("MDR - Mitteldeutscher Rundfunk", "33", "Mitteldeutscher%20Rundfunk", "mdr"))
			self.genreliste.append(("NDR - Norddeutscher Rundfunk", "34", "Norddeutscher%20Rundfunk", "ndr"))
			self.genreliste.append(("RB - Radio Bremen", "35", "dummy", "Radio+Bremen"))
			self.genreliste.append(("RBB - Rundfunk Berlin-Brandenburg", "36", "Rundfunk+Berlin-Brandenburg", "rbb"))
			self.genreliste.append((decodeHtml("SR - Saarl&auml;ndischer Rundfunk"), "37", "Saarl%C3%A4ndischer+Rundfunk", "sr"))
			self.genreliste.append((decodeHtml("SWR - S&uuml;dwestrundfunk"), "38", "S%C3%BCdwestrundfunk", "swr"))
			self.genreliste.append(("WDR - Westdeutscher Rundfunk", "39", "Westdeutscher+Rundfunk", "wdr"))
			self.genreliste.append(placeHolder)
			self.genreliste.append(("BR-alpha", "40", "dummy", "br-alpha"))
			self.genreliste.append(("DW - Deutsche Welle", "41", "Deutsche%20Welle", "dw"))
			self.genreliste.append(("EinsFestival", "42","dummy", "einsfestival"))
			self.genreliste.append(("EinsPlus", "43", "dummy", "einsplus"))
			self.genreliste.append(("Tagesschau", "44", "dummy", "dummy"))
			self.chooseMenuList.setList(map(ARDBody, self.genreliste))
			self.keyLocked = False

	def dataError(self, error):
		printl(error,self,"E")

	def keyOK(self):
		if self.keyLocked:
			return
		auswahl = self['List'].getCurrent()[0][0]
		extra = self['List'].getCurrent()[0][1]
		if extra == "99":
			return
		if self.gF == "3" and int(extra) <= 5:	# Extra-Kategorien TV
			if extra == '3': # Neueste Clips
				streamLink = "%s/ard/servlet/ajax-cache/3516220/view=list" % mainLink
				self.session.open(ARDStreamScreen,streamLink,auswahl,"dummy")
			elif extra == '4': # Meistabgerufene Clips, heute
				streamLink = "%s/ard/servlet/ajax-cache/3516210/view=list/show=recent" % mainLink
				self.session.open(ARDStreamScreen,streamLink,auswahl,"dummy")
			elif extra == '5': # Meistabgerufene Clips, gesamt
				streamLink = "%s/ard/servlet/ajax-cache/3516210/view=list/show=all" % mainLink
				self.session.open(ARDStreamScreen,streamLink,auswahl,"dummy")
		elif self.gF == "6" and int(extra) <= 5: # Extra-Kategorien Radio
			if extra == '1': # Tipps der Redaktion
				streamLink = "%s/ard/servlet/ajax-cache/3474772/view=list" % mainLink
				self.session.open(ARDStreamScreen,streamLink,auswahl,"dummy")
			elif extra == '2': # Hörspiel
				streamLink = "%s/ard/servlet/ajax-cache/5407526/view=list" % mainLink
				self.session.open(ARDStreamScreen,streamLink,auswahl,"dummy")
			elif extra == '3': # Neueste Clips
				streamLink = "%s/ard/servlet/ajax-cache/3516222/view=list" % mainLink
				self.session.open(ARDStreamScreen,streamLink,auswahl,"dummy")
			elif extra == '4': # Meistabgerufene Clips, heute
				streamLink = "%s/ard/servlet/ajax-cache/3516212/view=list/show=recent" % mainLink
				self.session.open(ARDStreamScreen,streamLink,auswahl,"dummy")
			elif extra == '5': # Meistabgerufene Clips, gesamt
				streamLink = "%s/ard/servlet/ajax-cache/3516212/view=list/show=all" % mainLink
				self.session.open(ARDStreamScreen,streamLink,auswahl,"dummy")
		elif self.gF == "10": # Einzelne Sender
			sender = self['List'].getCurrent()[0][2]
			such = self['List'].getCurrent()[0][3]
			self.session.open(ARDPreSelectSender,auswahl,extra,sender,such)
		else:
			if self.gF == "1": # ABC (TV oder Radio)
				self.gN = auswahl
			else:
				self.gN = auswahl
				auswahl = extra
			self.session.open(ARDPostSelect,auswahl,self.gN,self.gF, "dummy")

	def keyLeft(self):
		self['List'].pageUp()

	def keyRight(self):
		self['List'].pageDown()

	def keyUp(self):
		self['List'].up()

	def keyDown(self):
		self['List'].down()

	def keyCancel(self):
		self.close()

class ARDPreSelectSender(Screen):

	def __init__(self,session,genreName,genreFlag,sender,such):
		self.session = session
		self.gN = genreName
		self.gF = genreFlag
		self.sender = sender
		self.such = such
		path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/%s/RTLnowGenreScreen.xml" % config.mediaportal.skin.value
		if not fileExists(path):
			path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/original/RTLnowGenreScreen.xml"
		with open(path, "r") as f:
			self.skin = f.read()
			f.close()

		Screen.__init__(self, session)

		self["actions"]  = ActionMap(["OkCancelActions", "ShortcutActions", "WizardActions", "ColorActions", "SetupActions", "NumberActions", "MenuActions"], {
			"ok"    : self.keyOK,
			"cancel": self.keyCancel,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft
		}, -1)

		self['title'] = Label("ARD-Mediathek")
		self['name'] = Label("Auswahl der Medien")
		self['handlung'] = Label(helpText)
		self['Pic'] = Pixmap()

		self.genreliste = []
		self.keyLocked = True
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['List'] = self.chooseMenuList
		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.genreliste = []
		if  self.gF != "41" and self.gF != "44":
			self.genreliste.append(("TV", "1"))
		if self.gF != "32" and self.gF != "37" and self.gF != "44":
			self.genreliste.append(("Podcast TV", "2"))
		if self.gF != "30" and self.gF != "40" and self.gF != "42" and self.gF != "43" and self.gF != "44":
			self.genreliste.append(("Podcast Radio", "3"))
		if self.gF == "44":
			self.genreliste.append(("Tagesschau-Sendungen - TV", "1"))
			self.genreliste.append(("Tagesschau24 (Sport) - TV", "2"))
		self.chooseMenuList.setList(map(ARDBody, self.genreliste))
		self.keyLocked = False

	def dataError(self, error):
		printl(error,self,"E")

	def keyOK(self):
		if self.keyLocked:
			return
		auswahl = self['List'].getCurrent()[0][0]
		extra = self['List'].getCurrent()[0][1]
		urlbuild = mainLink + "/suche?rundfunk=%s&sender=select&detail=%s&s=%s&kategorien=all&inhalt=%s&goto="
		if  extra == "1":
			detail = "10"
			inhalt = "tv"
		elif extra == "2":
			detail = "20"
			inhalt = "tv"
		elif extra == "3":
			detail = "20"
			inhalt = "radio"
		if self.gF == "35" or self.gF == "40" or self.gF == "42" or self.gF == "43":
			url = mainLink + "/suche/?s="+self.such+"&detail="+detail+"&kategorien=all&inhalt="+inhalt+"&goto="
			self.session.open(ARDPostSelect,url,self.gN,self.gF,extra)
		elif self.gF == "44" and extra == "1":
			url = mainLink+"/ard/servlet/ajax-cache/3516962/view=list/documentId=4326/goto=1"
			self.session.open(ARDStreamScreen,url,auswahl,self.gF)
		elif self.gF == "44" and extra == "2":
			url = mainLink+"/ard/servlet/ajax-cache/3516962/view=list/documentId=6753968/goto=1"
			self.session.open(ARDStreamScreen,url,auswahl,self.gF)
		else:
			url = urlbuild % (self.sender,detail,self.such,inhalt)
			self.session.open(ARDPostSelect,url,self.gN,self.gF,extra)

	def keyLeft(self):
		self['List'].pageUp()

	def keyRight(self):
		self['List'].pageDown()

	def keyUp(self):
		self['List'].up()

	def keyDown(self):
		self['List'].down()

	def keyCancel(self):
		self.close()

class ARDPostSelect(Screen):

	def __init__(self,session,auswahl,genreName,genreFlag,mediaFlag):
		self.session = session
		self.auswahl = auswahl
		self.gN = genreName
		self.gF = genreFlag
		self.mF = mediaFlag
		path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/%s/RTLnowGenreScreen.xml" % config.mediaportal.skin.value
		if not fileExists(path):
			path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/original/RTLnowGenreScreen.xml"
		with open(path, "r") as f:
			self.skin = f.read()
			f.close()

		Screen.__init__(self, session)

		self["actions"]  = ActionMap(["OkCancelActions", "ShortcutActions", "WizardActions", "ColorActions", "SetupActions", "NumberActions", "MenuActions", "EPGSelectActions"], {
			"ok"    : self.keyOK,
			"cancel": self.keyCancel,
			"info" : self.keyInfo,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft,
			"nextBouquet" : self.keyPageUp,
			"prevBouquet" : self.keyPageDown
		}, -1)

		self['title'] = Label("ARD-Mediathek")
		self['name'] = Label("Auswahl der Inhalte - Bitte warten...")
		self['handlung'] = Label("")
		self['Pic'] = Pixmap()
		self.keyLocked = True
		self.genreliste = []
		self.page = 1
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['List'] = self.chooseMenuList

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		if self.gF == "3": # Standard-Kategorien TV
			ua = "%s/ard/servlet/ajax-cache/3516706/view=list/clipFilter=fernsehen/content=fernsehen/documentId=" % mainLink
		elif self.gF == "6": # Standard-Kategorien Radio
			ua = "%s/ard/servlet/ajax-cache/3516706/view=list/clipFilter=radio/content=radio/documentId=" % mainLink
		ue = "/goto=%s/index.html" % self.page
		if self.auswahl == '7':
			url = "%s506%s" % (ua,ue)
		elif self.auswahl == '8':
			url = "%s206%s" % (ua,ue)
		elif self.auswahl == '9':
			url = "%s726%s" % (ua,ue)
		elif self.auswahl == '10':
			url = "%s618%s" % (ua,ue)
		elif self.auswahl == '11':
			url = "%s636%s" % (ua,ue)
		elif self.auswahl == '12':
			url = "%s548%s" % (ua,ue)
		elif self.auswahl == '13':
			url = "%s564%s" % (ua,ue)
		elif self.auswahl == '14':
			url = "%s1062%s" % (ua,ue)
		elif self.auswahl == '15':
			url = "%s1228%s" % (ua,ue)
		elif self.auswahl == '16':
			url = "%s1230%s" % (ua,ue)
		elif self.auswahl == '17':
			url = "%s546%s" % (ua,ue)
		elif self.auswahl == '18':
			url = "%s1232%s" % (ua,ue)
		elif self.auswahl == '19':
			url = "%s544%s" % (ua,ue)
		elif self.auswahl == '20':
			url = "%s568%s" % (ua,ue)
		elif self.auswahl == '21':
			url = "%s920%s" % (ua,ue)
		elif self.auswahl == '22':
			url = "%s608%s" % (ua,ue)
		elif self.auswahl == '23':
			url = "%s678%s" % (ua,ue)
		elif self.auswahl == '24':
			url = "%s550%s" % (ua,ue)
		if self.gF == "7":	# Dossiers
			self['name'].setText("Auswahl des Dossiers - Bitte warten...")
			url = "%s/ard/servlet/ajax-cache/3516154/view=switch/goto=%s/index.html" % (mainLink,self.page)
		if self.gF == "1":	# ABC
			url = "%s/ard/servlet/ajax-cache/3474820/view=list/initial=%s/goto=%s/index.html" % (mainLink,self.auswahl,self.page)
		if int(self.gF) >= 30 and int(self.gF) <= 43:	# Einzelne Sender
			self['handlung'].setText(suchDef)
			url = self.auswahl + str(self.page)
		getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.loadPageData).addErrback(self.dataError)

	def loadPageData(self, data):
		self.keyLocked = True
		self.genreliste = []
		if "<option" in data: # Sammle Seitenanzahl
			seiten = re.findall('selected.*?>(.*?)<.*?<span> von (.*?)</span>', data, re.S)
			if seiten:
				for (a,b) in seiten:
					seite = "Seite   %s / %s" % (a,b)
		else: # keine Seitenanzahl gefunden, ergo: Gibt nur eine
			seite = "Seite   1 / 1"
		if self.gF == "7":	# Dossiers
			sendungen = re.findall('href="(.*?)documentId=(.*?)".*?</span>\s+(.*?)\s+</a>.*?count">(.*?) .*?verf', data, re.S)
			if sendungen:
				for (sub,id,title,ausgaben) in sendungen:
					url = "%s/ard/servlet/ajax-cache/3517004/view=list/documentId=%s" % (mainLink,id)
					suburl = "%s%sdocumentId=%s" % (mainLink,sub,id)
					sender = "Diverse"
					media = "Audio+Video"
					self.gN = "Dossiers"
					handlung = "Media:\t%s\nGenre:\t%s\nSender:\t%s\nClips:\t%s\t\t\t\t%s" % (media,self.gN,sender,ausgaben,seite)
					self.genreliste.append((decodeHtml(title),url,handlung,suburl))
			else:
				self.genreliste.append((isWeg,None,None,None))
		else:	# Alles andere
			if int(self.gF) >= 30 and int(self.gF) <= 43:
				sendungen = re.findall('"mt-title".*?href="(.*?)documentId=(.*?)".*?>(.*?)<.*?count">(.*?) .*?verf.*?channel">(.*?)<', data, re.S)
			else:
				sendungen = re.findall('"mt-title".*?href="(.*?)documentId=(.*?)".*?>\s+(.*?)\s+<.*?count">(.*?) .*?verf.*?channel">(.*?)<', data, re.S)
			if sendungen:
				for (sub,id,title,ausgaben,sender) in sendungen:
					if not ausgaben:
						ausgaben = tDef
					podFound = 0
					if "/podcast/" in sub:
						title = title.replace("|","-")
						podFound = 1
						url = "%s/ard/servlet/ajax-cache/3516992/view=list/documentId=%s" % (mainLink,id)
					else:
						url = "%s/ard/servlet/ajax-cache/3516962/view=list/documentId=%s" % (mainLink,id)
					suburl = "%s%sdocumentId=%s" % (mainLink,sub,id)
					if self.gF == "5" or self.gF == "6":
						media = "Radio"
					else:
						media = "TV"
					if podFound == 1:
						media = "Podcast"
					if self.mF == "1":	# Einzelne Sender
						media = "TV"
					elif self.mF == "2":
						media = "Podcast TV"
					elif self.mF == "3":
						media = "Podcast Radio"
					handlung = "Media:\t%s\nGenre:\t%s\nSender:\t%s\nClips:\t%s\t\t\t\t%s" % (media,self.gN,sender,ausgaben,seite)
					self.genreliste.append((decodeHtml(title),url,handlung,suburl))
			else:
				self.genreliste.append((isWeg,None,None,None))
		self.chooseMenuList.setList(map(ARDBody, self.genreliste))
		self.keyLocked = False
		self.loadPic()

	def dataError(self,error):
		printl(error,self,"E")

	def loadPic(self):
		url = self['List'].getCurrent()[0][3]
		getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.handlePicAndTxt).addErrback(self.dataError)

	def handlePicAndTxt(self, data):
		gefunden = re.findall('<meta name="description" content="(.*?)".*?<meta name="gsaimg512" content="(.*?)"', data, re.S)
		if gefunden:
			for (itxt,streamPic) in gefunden:
				itxttmp = itxt.split("|")
				itxt = itxttmp[-1]
				itxt = decodeHtml(itxt)
				if itxt[:1] == " ":
					itxt = itxt[1:]
				if itxt == "":
					itxt = tDef
		if textTrigger == 1:
			streamHandlung = itxt
		elif textTrigger == 0:
			streamHandlung = self['List'].getCurrent()[0][2]
		self['handlung'].setText(streamHandlung)
		streamName = self['List'].getCurrent()[0][0]
		self['name'].setText(streamName)
		if streamPic:
			CoverHelper(self['Pic']).getCover(streamPic)

	def keyOK(self):
		if self.keyLocked:
			return
		if self['List'].getCurrent()[0][0] == isWeg:
			self.close()
		global textTrigger
		textTrigger = 0
		streamLink = self['List'].getCurrent()[0][1]
		if streamLink == None:
			return
		self.session.open(ARDStreamScreen,streamLink,self.gN,self.gF)

	def keyLeft(self):
		if self.keyLocked:
			return
		self['List'].pageUp()
		self.loadPic()

	def keyRight(self):
		if self.keyLocked:
			return
		self['List'].pageDown()
		self.loadPic()

	def keyUp(self):
		if self.keyLocked:
			return
		self['List'].up()
		self.loadPic()

	def keyDown(self):
		if self.keyLocked:
			return
		self['List'].down()
		self.loadPic()

	def keyPageDown(self):
		if self.keyLocked:
			return
		if not self.page < 1:
			self.page -= 1
			self.loadPage()

	def keyPageUp(self):
		if self.keyLocked:
			return
		self.page += 1
		self.loadPage()

	def keyInfo(self):
		if self.keyLocked:
			return
		if textTrigger == 0:
			global textTrigger
			textTrigger = 1
		elif textTrigger == 1:
			global textTrigger
			textTrigger = 0
		self.loadPic()

	def keyCancel(self):
		if self.keyLocked:
			return
		global textTrigger
		textTrigger = 0
		self.close()

class ARDStreamScreen(Screen):

	def __init__(self, session,streamLink,genreName,genreFlag):
		self.session = session
		self.streamLink = streamLink
		self.gN = genreName
		self.gF = genreFlag
		path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/%s/RTLnowGenreScreen.xml" % config.mediaportal.skin.value
		if not fileExists(path):
			path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/original/RTLnowGenreScreen.xml"
		print path
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
			"info" : self.keyInfo
			}, -1)

		self['title'] = Label("ARD-Mediathek")
		if self.gF == "2" or self.gF == "5":
			self['name'] = Label("Suche - Bitte warten")
			self['handlung'] = Label(suchDef)
		else:
			self['name'] = Label("Auswahl des Clips - Bitte warten...")
			self['handlung'] = Label("")
		self['Pic'] = Pixmap()
		self.page = 1
		self.keyLocked = True
		self.filmliste = []
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['List'] = self.chooseMenuList

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		if self.gF == "2" or self.gF == "5" or self.gF == "8" or self.gF == "9":
			url = self.streamLink % (self.page)
		else:
			url = "%s/goto=%s" % (self.streamLink,self.page)
		getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.loadPageData).addErrback(self.dataError)

	def dataError(self, error):
		printl(error,self,"E")

	def loadPageData(self, data):
		self.keyLocked = True
		self.filmliste = []
		if "<option" in data:
			seiten = re.findall('selected.*?>(.*?)<.*?<span> von (.*?)</span>', data, re.S)
			if seiten:
				for (a,b) in seiten:
					seite = "Seite   %s / %s" % (a,b)
		else:
			seite = "Seite   1 / 1"
		folgen = re.findall('mt-media.*?mt-icon_(.*?)i.*?<a href="(.*?)".*?">(.*?)<.*?<p class=".*?">(.*?)<.*?time">(.*?)</span>.*?>(.*?)</', data, re.S)
		if folgen:
			for (media,url,title,sendung,airtime,sender) in folgen:
				url = "%s%s" % (mainLink,url)
				sendung = sendung.replace('aus: ', '')
				sendung = sendung.replace('|', '-')
				media = media.replace("v","Video")
				media = media.replace("aud","Audio")
				media = media.replace("l","Live-Tipp")
				if airtime:
					if len(airtime) == 0:
						date = tDef
						dur = "-"
					elif len(airtime) == 8:
						date = "%s" % (airtime)
						dur = "-"
					else:
						date = airtime[:8]
						if self.gF == "2" or self.gF == "5":	# Suche
							dur = airtime[12:]
						else:
							dur = airtime[9:]
				handlung = "Media:\t%s\nGenre:\t%s\nSendung:\t%s\nClip-Datum:\t%s\nSender:\t%s\nDauer:\t%s\t\t\t\t%s" % (media,self.gN,decodeHtml(sendung),date,sender,dur,seite)
				self.filmliste.append((decodeHtml(title),url,handlung))
				self.chooseMenuList.setList(map(ARDBody, self.filmliste))
		else:
			self.filmliste.append((isWeg, None, None, None))
			self.chooseMenuList.setList(map(ARDBody, self.filmliste))
		self.keyLocked = False
		self.loadPic()

	def loadPic(self):
		url = self['List'].getCurrent()[0][1]
		getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.handlePicAndTxt).addErrback(self.dataError)

	def handlePicAndTxt(self, data):
		if '<div><p>' in data:
			ergebnis = re.findall('<meta name="gsaimg512" content="(.*?)".*?<div><p>(.*?)</p></div>', data, re.S)
			if ergebnis:
				for (streamPic,itxt) in ergebnis:
					if not itxt or len(itxt) == 0:
						itxt = tDef
					else:
						itxt = decodeHtml(itxt)
		else:
			ergebnis = re.findall('<meta name="description" content="(.*?)".*?<meta name="gsaimg512" content="(.*?)"', data, re.S)
			if ergebnis:
				for (itxt,streamPic) in ergebnis:
					if not itxt or len(itxt) == 0:
						itxt = tDef
					else:
						title = self['List'].getCurrent()[0][0]
						itxttmp = itxt.split(title)
						itxt = itxttmp[-1]
						itxt = decodeHtml(itxt)
						if itxt[:2] == ": ":
							itxt = itxt[2:]
						if itxt == "":
							itxt = tDef
		if textTrigger == 1:
			streamHandlung = itxt
		elif textTrigger == 0:
			streamHandlung = self['List'].getCurrent()[0][2]
		self['handlung'].setText(streamHandlung)
		streamName = self['List'].getCurrent()[0][0]
		self['name'].setText(streamName)
		if streamPic:
			CoverHelper(self['Pic']).getCover(streamPic)

	def keyOK(self):
		if self.keyLocked:
			return
		self.streamName = self['List'].getCurrent()[0][0]
		if self.streamName == isWeg:
			self.close()
		self['name'].setText("Bitte warten...")
		url = self['List'].getCurrent()[0][1]
		if url == None:
			return
		else:
			getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.get_Link).addErrback(self.dataError)

	def dataError(self, error):
		printl(error,self,"E")

	def get_Link(self, data):
		self.keyLocked = True
		fsk = re.search('class="fsk">(.*?)</div>', data, re.S)
		if fsk:
			message = self.session.open(MessageBox, _(fsk.group(1)), MessageBox.TYPE_INFO, timeout=7)
			self.keyLocked = False
			return
		qualitycheck = re.findall('mediaCollection.addMediaStream\((.*?),\s+(.*?),\s+"(.*?)",\s+"(.*?)",.*?\)', data, re.S)

		if qualitycheck:
			Q0P = ""
			Q1P = ""
			Q2P = ""
			Q3P = ""
			Q0H = ""
			Q1H = ""
			Q2H = ""
			Q3H = ""
			htP = ""
			rtH = ""
			rtP = ""
			contentExists = 0

			for (a,b,c,d) in qualitycheck:
				if "?sen=" in d:	# Für ARD-Links, sonst wird von rtmp auf http geschwenkt - "?sen=[...]" vermutlich wegen Untertitel für Hörgeschädigte in PC-Browser
					d = d.split("?")[0]
				if ".mp3" in (d.lower()):	# Checke Abspielarten und übersehe nachfolgend keine Upper-Cases, zB. beim SR
					art = ".mp3"
				elif ".mp4" in (d.lower()):
					art = ".mp4"
				elif ".f4v" in (d.lower()):
					art = ".f4v"
				if int(a+b) >= 30:	# QualityCheck
					if (d[-4:].lower()) == art:
						Q3H = c
						Q3P = d
				elif int(a+b) >= 20 and int(a+b) < 24:
					if (d[-4:].lower()) == art:
						Q2H = c
						Q2P = d
				elif int(a+b) >= 10 and int(a+b) < 14:
					if (d[-4:].lower()) == art:
						Q1H = c
						Q1P = d
				elif int(a+b) > 0 and  int(a+b) < 4:
					if (d[-4:].lower()) == art:
						Q0H = c
						Q0P = d

			if len(Q0P+Q0H+Q1P+Q1H+Q2P+Q2H+Q3P+Q3H) == 0:	# Hier stimmt gar nichts!
				message = self.session.open(MessageBox, _("\n' "+self.streamName+decodeHtml(" '\n\n"+alienFound)), MessageBox.TYPE_INFO, timeout=15)
				self.keyLocked = False
				return
			if len(Q0P) > 0 or len(Q0H) > 0:
				if "http://" in Q0P:
					htP = Q0P
				if Q0H != "":
					rtH = Q0H
					rtP = Q0P
			if len(Q1P) > 0 or len(Q1H) > 0:
				if "http://" in Q1P:
					htP = Q1P
				if Q1H != "":
					rtH = Q1H
					rtP = Q1P
			if len(Q2P) > 0 or len(Q2H) > 0:
				if "http://" in Q2P:
					htP = Q2P
				if Q2H != "":
					rtH = Q2H
					rtP = Q2P
			if len(Q3P) > 0 or len(Q3H) > 0:
				if "http://" in Q3P:
					htP = Q3P
				if Q3H != "":
					rtH = Q3H
					rtP = Q3P
			# Sonderlocken
			if "geode_" in rtP:	# rtmp-Links mit ardgeofs/geode_ im URI dürfen aus rechtlichen Gründen nur in Deutschland gestreamt werden + müssen auf http umgebaut werden, da sie sonst auch in D nicht laufen.
				geoP = re.search('mp4:.*?/.*?/.*?/(.*?).mp4', rtP, re.S)
				geoP = geoP.group(1).replace("geode_","")
				htP = "http://mvideos.daserste.de/videoportal/Film/"+geoP+".mp4"
				rtP = ""
				rtH = ""
			if "bie_webl_ard" in htP:	# Large/Small-Quali von Börse im Ersten läuft auch am PC nicht (alle Clips); nur Medium + nur http angeboten.
				htP = htP.replace("bie_webl_ard","bie_ard")

			if htP == "" and rtH != "":	# Wenn kein einziger http-Link vorhanden (ausschliesslich rtmp-Links), umgehe nachfolgende http-Abfrage, und "vertraue darauf" dass Content existiert. Beispiel, bei dem es misslingt: "2 Mann für alle Gänge"... Nur rtmp, aber gleichzeitig nicht mehr vorhanden...
				contentExists = 1
			if htP != "":	# http-Abfrage, ob Content existiert. Wenn ja, und es werden ebenfalls rtmp-Links angeboten, dann existieren immer beide Contents! Eine rtmp-Abfrage wäre zu kompliziert.
				try:
					url = urllib2.urlopen(htP)
				except IOError:
					message = self.session.open(MessageBox, _("\n' "+self.streamName+" '\n\n"+isWeg), MessageBox.TYPE_INFO, timeout=7)
					self.keyLocked = False
					return
				else:
					contentExists = 1

			self.keyLocked = False

			if contentExists == 1:
				if rtH != "":
					if "fc-ondemand.radiobremen.de" in rtH:	# Sonderlocken
						host = rtH.split('mediabase/')[0]
						playpath1 = rtH.split('/mediabase/')[1]
						playpath2 = rtP[4:]
						playpath = "mp4:mediabase/%s/%s" % (playpath1,playpath2)
					else:
						host = rtH
						playpath = rtP
					playpath = playpath.replace('&amp;','&')
					if config.mediaportal.useRtmpDump.value:
						final = "%s' --playpath=%s'" % (host, playpath)
						movieinfo = [final,self.streamName]
						self.session.open(PlayRtmpMovie, movieinfo, self.streamName)
					else:
						final = "%s playpath=%s" % (host, playpath)
						playlist = []
						playlist.append((self.streamName, final))
						print "Via rtmp: "+self.streamName
						self.session.open(SimplePlayer, playlist, showPlaylist=False, ltype='ard')
				else:
					playpath = htP
					playlist = []
					playlist.append((self.streamName, playpath))
					print "Via http: "+self.streamName
					self.session.open(SimplePlayer, playlist, showPlaylist=False, ltype='ard')
			else:
				message = self.session.open(MessageBox, _("\n' "+self.streamName+" '\n\n"+alienFound), MessageBox.TYPE_INFO, timeout=15)
				self.keyLocked = False
				return
		self['name'].setText("Auswahl des Clips")

	def keyLeft(self):
		if self.keyLocked:
			return
		self['List'].pageUp()
		self.loadPic()

	def keyRight(self):
		if self.keyLocked:
			return
		self['List'].pageDown()
		self.loadPic()

	def keyUp(self):
		if self.keyLocked:
			return
		self['List'].up()
		self.loadPic()

	def keyDown(self):
		if self.keyLocked:
			return
		self['List'].down()
		self.loadPic()

	def keyPageDown(self):
		if self.keyLocked:
			return
		if not self.page < 1:
			self.page -= 1
			self.loadPage()

	def keyPageUp(self):
		if self.keyLocked:
			return
		self.page += 1
		self.loadPage()

	def keyInfo(self):
		if self.keyLocked:
			return
		if textTrigger == 0:
			global textTrigger
			textTrigger = 1
		elif textTrigger == 1:
			global textTrigger
			textTrigger = 0
		self.loadPic()

	def keyCancel(self):
		global textTrigger
		textTrigger = 0
		self.close()
