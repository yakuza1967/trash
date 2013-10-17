# -*- coding: utf-8 -*-
from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.simpleplayer import SimplePlayer
from Plugins.Extensions.MediaPortal.resources.coverhelper import CoverHelper

def bildEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 20, 0, 860, 25, 0, RT_HALIGN_CENTER | RT_VALIGN_CENTER, entry[0])
		]

def bildEntry1(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 20, 0, 860, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry[0]+" - "+entry[3])
		]

class bildFirstScreen(Screen):

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
			"ok"	: self.keyOK,
			"cancel": self.keyCancel
		}, -1)

		self['title'] = Label("Bild.de")
		self['ContentTitle'] = Label("Genre:")
		self['name'] = Label("Auswahl:")
		self['F1'] = Label("Exit")
		self['F2'] = Label("")
		self['F3'] = Label("")
		self['F4'] = Label("")
		self['F2'].hide()
		self['F3'].hide()
		self['F4'].hide()
		self['coverArt'] = Pixmap()
		self.keyLocked = True
		self.filmliste = []
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['genreList'] = self.chooseMenuList

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		url = "http://www.bild.de/video/startseite/bildchannel-home/video-home-15713248.bild.html"
		getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.parseData).addErrback(self.dataError)

	def parseData(self, data):
		raw = re.findall('<h2>Top-Videos</h2>(.*?)</ol>', data, re.S)
		if raw:
			categorys = re.findall('<li><a href="(.*?)">(.*?)</a></li>', raw[0], re.S)
			self.filmliste = []
			for (bildUrl, bildTitle) in categorys:
				self.filmliste.append((decodeHtml(bildTitle), bildUrl))
			self.chooseMenuList.setList(map(bildEntry, self.filmliste))
			self.keyLocked = False

	def dataError(self, error):
		printl(error,self,"E")

	def getTriesEntry(self):
		return config.ParentalControl.retries.setuppin

	def pincheckok(self, pincode):
		bildName = self['genreList'].getCurrent()[0][0]
		Link = self['genreList'].getCurrent()[0][1]
		bildLink = "http://www.bild.de" + Link
		if pincode:
			self.session.open(bildSecondScreen, bildLink, bildName)

	def keyOK(self):
		bildName = self['genreList'].getCurrent()[0][0]
		Link = self['genreList'].getCurrent()[0][1]
		bildLink = "http://www.bild.de" + Link
		if bildName == "Wissen":
			self.session.open(bildWissenScreen)
		elif bildName == "Regional":
			self.session.open(bildRegionalScreen)
		elif bildName == "Erotik":
			if config.mediaportal.pornpin.value:
				self.session.openWithCallback(self.pincheckok, PinInput, pinList = [(config.mediaportal.pincode.value)], triesEntry = self.getTriesEntry(), title = _("Please enter the correct pin code"), windowTitle = _("Enter pin code"))
			else:
				self.session.open(bildSecondScreen, bildLink, bildName)
		else:
			self.session.open(bildSecondScreen, bildLink, bildName)

	def keyCancel(self):
		self.close()

class bildRegionalScreen(Screen):

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
			"ok"	: self.keyOK,
			"cancel": self.keyCancel
		}, -1)

		self['title'] = Label("Bild.de")
		self['ContentTitle'] = Label("Genre:")
		self['name'] = Label("Auswahl:")
		self['F1'] = Label("Exit")
		self['F2'] = Label("")
		self['F3'] = Label("")
		self['F4'] = Label("")
		self['F2'].hide()
		self['F3'].hide()
		self['F4'].hide()
		self['coverArt'] = Pixmap()
		self.keyLocked = True

		self.filmliste = []
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['genreList'] = self.chooseMenuList

		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.filmliste.append(("Berlin", "berlin-regional/berlin-15717736"))
		self.filmliste.append(("Bremen", "bremen-regional/bremen-15717790"))
		self.filmliste.append(("Dresden", "dresden-regional/dresden-15717824"))
		self.filmliste.append(("Düsseldorf", "duesseldorf-regional/duesseldorf-15717846"))
		self.filmliste.append(("Frankfurt", "frankfurt-regional/frankfurt-15717874"))
		self.filmliste.append(("Hamburg", "hamburg-regional/hamburg-15717766"))
		self.filmliste.append(("Hannover", "hannover-regional/hannover-15717900"))
		self.filmliste.append(("Köln", "koeln-regional/koeln-15717928"))
		self.filmliste.append(("Leipzig", "leipzig-regional/leipzig-15717952"))
		self.filmliste.append(("München", "muenchen-regional/muenchen-15717974"))
		self.filmliste.append(("Ruhrgebiet", "ruhrgebiet-regional/ruhrgebiet-16989232"))
		self.filmliste.append(("Stuttgart", "stuttgart-regional/stuttgart-15718002"))

		self.chooseMenuList.setList(map(bildEntry, self.filmliste))

	def keyOK(self):
		bildName = self['genreList'].getCurrent()[0][0]
		bildLink = "http://www.bild.de/video/clip/" + self['genreList'].getCurrent()[0][1] + ".bild.html"
		self.session.open(bildSecondScreen, bildLink, bildName)

	def keyCancel(self):
		self.close()

class bildWissenScreen(Screen):

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
			"ok"	: self.keyOK,
			"cancel": self.keyCancel
		}, -1)

		self['title'] = Label("Bild.de")
		self['ContentTitle'] = Label("Genre:")
		self['name'] = Label("Auswahl:")
		self['F1'] = Label("Exit")
		self['F2'] = Label("")
		self['F3'] = Label("")
		self['F4'] = Label("")
		self['F2'].hide()
		self['F3'].hide()
		self['F4'].hide()
		self['coverArt'] = Pixmap()
		self.keyLocked = True

		self.filmliste = []
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['genreList'] = self.chooseMenuList

		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.filmliste.append(("Übersicht", "/wissen-uebersicht-20423868"))
		self.filmliste.append(("Medizin", "-medizin/wissen-medizin-20424074"))
		self.filmliste.append(("Technik", "-technik/wissen-technik-20424140"))
		self.filmliste.append(("Panorama", "-panorama/wissen-panorama-20424026"))
		self.filmliste.append(("Natur", "-natur/wissen-natur-20424092"))
		self.filmliste.append(("Geschichte", "-geschichte/wissen-geschichte-20424050"))
		self.chooseMenuList.setList(map(bildEntry, self.filmliste))

	def keyOK(self):
		bildName = self['genreList'].getCurrent()[0][0]
		bildLink = "http://www.bild.de/video/clip/bild-de-wissen" + self['genreList'].getCurrent()[0][1] + ".bild.html"
		self.session.open(bildSecondScreen, bildLink, bildName)

	def keyCancel(self):
		self.close()

class bildSecondScreen(Screen):

	def __init__(self, session, bildLink, bildName):
		self.session = session
		self.bildLink = bildLink
		self.bildName = bildName
		self.plugin_path = mp_globals.pluginPath
		self.skin_path =  mp_globals.pluginPath + "/skins"

		path = "%s/%s/defaultListScreen.xml" % (self.skin_path, config.mediaportal.skin.value)
		if not fileExists(path):
			path = self.skin_path + "/original/defaultListScreen.xml"

		with open(path, "r") as f:
			self.skin = f.read()
			f.close()

		Screen.__init__(self, session)

		self["actions"] = ActionMap(["OkCancelActions", "ShortcutActions", "WizardActions", "ColorActions", "SetupActions", "NumberActions", "MenuActions", "EPGSelectActions"], {
		"ok"	: self.keyOK,
		"cancel": self.keyCancel,
		"up" : self.keyUp,
		"down" : self.keyDown,
		"right" : self.keyRight,
		"left" : self.keyLeft,
		"nextBouquet" : self.keyPageUp,
		"prevBouquet" : self.keyPageDown
		}, -1)

		self['title'] = Label("Bild.de")
		self['ContentTitle'] = Label("Genre: %s" % self.bildName)
		self['name'] = Label("")
		self['F1'] = Label("Exit")
		self['F2'] = Label("")
		self['F3'] = Label("")
		self['F4'] = Label("")
		self['F2'].hide()
		self['F3'].hide()
		self['F4'].hide()
		self['coverArt'] = Pixmap()
		self['Page'] = Label("Page: ")
		self['page'] = Label("")
		self['handlung'] = Label("")

		self.keyLocked = True
		self.filmliste = []
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['liste'] = self.chooseMenuList
		self.page = 0
		self.lastpage = 0
		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		url = self.bildLink
		getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.parseData).addErrback(self.dataError)

	def parseData(self, data):
		lastpage = re.search('<li\sclass="pagLast">.*?page=(.*),isVideoStartseite', data)
		if lastpage:
			self.lastpage = int(lastpage.group(1))+1
			self['page'].setText("%s / %s" % (str(self.page+1), str(self.lastpage)))
		else:
			parse = re.search('class="pag">(.*)weiter</a>', data, re.S)
			if parse:
				lastpage = re.findall('>([\d]+)</a></li>', parse.group(1), re.S)
				if lastpage:
					self.lastpage = int(lastpage[-1])
					self['page'].setText("%s / %s" % (str(self.page+1), str(self.lastpage)))
			else:
				self.lastpage = 0
				self['page'].setText("%s / 1" % str(self.page+1))

		raw = re.search('(Aktuellste|Neueste|Alle)\sVideos</h2>(.*)</section></div></div>', data, re.S).groups()
		if raw:
			seasons = re.findall('class="active">.*?data-ajax-href="(.*?)page=.*?,(.*?)"', raw[1], re.S)
			if seasons:
				vid_id1 = seasons[0][0]
				vid_id2 = seasons[0][1]
				nexturl = "http://www.bild.de/" + vid_id1 + "page=" + str(self.page) + "," + vid_id2
				getPage(nexturl, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.parseData2).addErrback(self.dataError)
			else:
				self.parseData2(raw[1])

	def parseData2(self, data):
		categorys =  re.findall('class="hentry.*?<a\shref="([^#].*?)".*?src="(.*?)".*?class="kicker">(.*?)<.*?class="headline">(.*?)</h3>', data, re.S)
		self.filmliste = []
		for (bildUrl, bildImage, bildTitle, handlung) in categorys:
			handlung = handlung.replace('</span><span>',' ').replace('<span>','').replace('</span>','')
			self.filmliste.append((decodeHtml(bildTitle), bildUrl, bildImage, handlung))
		self.chooseMenuList.setList(map(bildEntry1, self.filmliste))
		self.keyLocked = False
		self.showInfos()

	def dataError(self, error):
		printl(error,self,"E")

	def showInfos(self):
		coverUrl = self['liste'].getCurrent()[0][2]
		CoverHelper(self['coverArt']).getCover(coverUrl)

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
		if self.page+1 < self.lastpage:
			self.page += 1
			self.loadPage()

	def keyOK(self):
		if self.keyLocked:
			return
		bildLink = self['liste'].getCurrent()[0][1]
		self.bildLink = "http://www.bild.de" + bildLink
		self.bildName = self['liste'].getCurrent()[0][0] + " - " + self['liste'].getCurrent()[0][3]
		getPage(self.bildLink, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.parseVideoData).addErrback(self.dataError)

	def parseVideoData(self, data):
		xmllink = re.search('longdesc="(.*?)"', data, re.S)
		if xmllink:
			getxml = "http://www.bild.de" + xmllink.group(1)
			getPage(getxml, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.playVideo).addErrback(self.dataError)

	def playVideo(self, data):
		streamlink = re.search('<video\ssrc="(.*?)"', data, re.S)
		if streamlink:
			if re.match('.*?\/ondemand\/', streamlink.group(1)):
				host = streamlink.group(1).split('ondemand/')[0]
				playpath = streamlink.group(1).split('ondemand/')[1]
				final = "%sondemand/ playpath=mp4:%s swfVfy=1" % (host, playpath)
			else:
				final = streamlink.group(1)
			print "Final: " + final
			self.session.open(SimplePlayer, [(self.bildName, final)], showPlaylist=False, ltype='Bild.de')

	def keyCancel(self):
		self.close()