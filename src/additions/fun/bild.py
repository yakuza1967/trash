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

def decodeBild(text):
	text = text.replace('<span>','')
	text = text.replace('</span>',' ')
	return text

class bildFirstScreen(Screen):

	def __init__(self, session):
		self.session = session
		path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/%s/defaultGenreScreen.xml" % config.mediaportal.skin.value
		if not fileExists(path):
			path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/defaultGenreScreen.xml"
		print path
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
		self['name'] = Label("v0.3")
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
		path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/%s/defaultGenreScreen.xml" % config.mediaportal.skin.value
		if not fileExists(path):
			path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/defaultGenreScreen.xml"
		print path
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
		self['name'] = Label("v0.3")
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
		self.filmliste.append(("Berlin", "http://www.bild.de/video/clip/berlin-regional/berlin-15717736.bild.html"))
		self.filmliste.append(("Bremen", "http://www.bild.de/video/clip/bremen-regional/bremen-15717790.bild.html"))
		self.filmliste.append(("Dresden", "http://www.bild.de/video/clip/dresden-regional/dresden-15717824.bild.html"))
		self.filmliste.append(("Düsseldorf", "http://www.bild.de/video/clip/duesseldorf-regional/duesseldorf-15717846.bild.html"))
		self.filmliste.append(("Frankfurt", "http://www.bild.de/video/clip/frankfurt-regional/frankfurt-15717874.bild.html"))
		self.filmliste.append(("Hamburg", "http://www.bild.de/video/clip/hamburg-regional/hamburg-15717766.bild.html"))
		self.filmliste.append(("Hannover", "http://www.bild.de/video/clip/hannover-regional/hannover-15717900.bild.html"))
		self.filmliste.append(("Köln", "http://www.bild.de/video/clip/koeln-regional/koeln-15717928.bild.html"))
		self.filmliste.append(("Leipzig", "http://www.bild.de/video/clip/leipzig-regional/leipzig-15717952.bild.html"))
		self.filmliste.append(("München", "http://www.bild.de/video/clip/muenchen-regional/muenchen-15717974.bild.html"))
		self.filmliste.append(("Ruhrgebiet", "http://www.bild.de/video/clip/ruhrgebiet-regional/ruhrgebiet-16989232.bild.html"))
		self.filmliste.append(("Stuttgart", "http://www.bild.de/video/clip/stuttgart-regional/stuttgart-15718002.bild.html"))
		
		self.chooseMenuList.setList(map(bildEntry, self.filmliste))

	def keyOK(self):
		bildName = self['genreList'].getCurrent()[0][0]
		bildLink = self['genreList'].getCurrent()[0][1]
		self.session.open(bildSecondScreen, bildLink, bildName)

	def keyCancel(self):
		self.close()

class bildWissenScreen(Screen):

	def __init__(self, session):
		self.session = session
		path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/%s/defaultGenreScreen.xml" % config.mediaportal.skin.value
		if not fileExists(path):
			path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/defaultGenreScreen.xml"
		print path
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
		self['name'] = Label("v0.3")
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
		self.filmliste.append(("Übersicht", "http://www.bild.de/video/clip/bild-de-wissen/wissen-uebersicht-20423868.bild.html"))
		self.filmliste.append(("Medizin", "http://www.bild.de/video/clip/bild-de-wissen-medizin/wissen-medizin-20424074.bild.html"))
		self.filmliste.append(("Technik", "http://www.bild.de/video/clip/bild-de-wissen-technik/wissen-technik-20424140.bild.html"))
		self.filmliste.append(("Panorama", "http://www.bild.de/video/clip/bild-de-wissen-panorama/wissen-panorama-20424026.bild.html"))
		self.filmliste.append(("Natur", "http://www.bild.de/video/clip/bild-de-wissen-natur/wissen-natur-20424092.bild.html"))
		self.filmliste.append(("Geschichte", "http://www.bild.de/video/clip/bild-de-wissen-geschichte/wissen-geschichte-20424050.bild.html"))

		self.chooseMenuList.setList(map(bildEntry, self.filmliste))

	def keyOK(self):
		bildName = self['genreList'].getCurrent()[0][0]
		bildLink = self['genreList'].getCurrent()[0][1]
		self.session.open(bildSecondScreen, bildLink, bildName)

	def keyCancel(self):
		self.close()

class bildSecondScreen(Screen):

	def __init__(self, session, bildLink, bildName):
		self.session = session
		self.bildLink = bildLink
		self.bildName = bildName

		path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/%s/defaultListScreen.xml" % config.mediaportal.skin.value
		if not fileExists(path):
			path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/original/defaultListScreen.xml"
		print path
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
		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		url = self.bildLink
		getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.parseData).addErrback(self.dataError)

	def parseData(self, data):
		lastpage = re.findall('<li class="pagLast">.*?page=(.*?),isVideoStartseite', data)
		if lastpage:
			self['page'].setText("%s / %s" % (str(self.page +1), str(lastpage[0])))
		else:
			self['page'].setText(str(self.page +1))

		if self.bildName == "Geschichte" or self.bildName == "Natur":
			raw = re.findall('Alle Videos</h2>(.*?)</section></div></div>', data, re.S)
			if raw:
				categorys = re.findall('class="hentry.*?href="(.*?)".*?src="(.*?)".*?class="kicker">(.*?)<.*?class="headline">(.*?)</h3>', raw[0], re.S)
				self.filmliste = []
				for (bildUrl, bildImage, bildTitle, handlung) in categorys:
					self.filmliste.append((decodeHtml(bildTitle), bildUrl, bildImage,(decodeBild(handlung))))
				self.chooseMenuList.setList(map(bildEntry1, self.filmliste))
				self.keyLocked = False
				self.showInfos()
		elif self.bildName == "Panorama" or self.bildName == "Technik" or self.bildName == "Medizin" or self.bildName == "Übersicht":
			raw = re.findall('Alle Videos</h2>(.*?)</section></div></div>', data, re.S)
			if raw:
				seasons = re.findall('class="active">.*?data-ajax-href="(.*?)page=.*?,(.*?)"', raw[0], re.S)
				vid_id1 = seasons[0][0]
				vid_id2 = seasons[0][1]
				nexturl = "http://www.bild.de/" + vid_id1 + "page=" + str(self.page) + "," + vid_id2
				getPage(nexturl, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.parseData2).addErrback(self.dataError)
		elif self.bildName == "Stuttgart":
			raw = re.findall('Aktuellste Videos</h2>(.*?)</section></div></div>', data, re.S)
			if raw:
				seasons = re.findall('class="active">.*?data-ajax-href="(.*?)page=.*?,(.*?)"', raw[0], re.S)
				vid_id1 = seasons[0][0]
				vid_id2 = seasons[0][1]
				nexturl = "http://www.bild.de/" + vid_id1 + "page=" + str(self.page) + "," + vid_id2
				getPage(nexturl, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.parseData2).addErrback(self.dataError)	
		else:
			raw = re.findall('Neueste Videos</h2>(.*?)</section></div></div>', data, re.S)
			if raw:
				seasons = re.findall('class="active">.*?data-ajax-href="(.*?)page=.*?,(.*?)"', raw[0], re.S)
				vid_id1 = seasons[0][0]
				vid_id2 = seasons[0][1]
				nexturl = "http://www.bild.de/" + vid_id1 + "page=" + str(self.page) + "," + vid_id2
				getPage(nexturl, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.parseData2).addErrback(self.dataError)

	def parseData2(self, data):
		categorys =  re.findall('class="hentry.*?href="(.*?)".*?src="(.*?)".*?class="kicker">(.*?)<.*?class="headline">(.*?)</h3>', data, re.S)
		self.filmliste = []
		for (bildUrl, bildImage, bildTitle, handlung) in categorys:
			self.filmliste.append((decodeHtml(bildTitle), bildUrl, bildImage,(decodeBild(handlung))))
		self.chooseMenuList.setList(map(bildEntry1, self.filmliste))
		self.keyLocked = False
		self.showInfos()

	def dataError(self, error):
		printl(error,self,"E")

	def showInfos(self):
		coverUrl = self['liste'].getCurrent()[0][2]
		ImageUrl = "%s" % coverUrl
		CoverHelper(self['coverArt']).getCover(ImageUrl)

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
		self.page += 1
		self.loadPage()

	def keyOK(self):
		bildName = self['liste'].getCurrent()[0][0]
		bildLink = self['liste'].getCurrent()[0][1]
		self.bildLink = "http://www.bild.de" + bildLink
		self.bildName = bildName
		getPage(self.bildLink, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.parseVideoData).addErrback(self.dataError)

	def parseVideoData(self, data):
		xmllink = re.findall('longdesc="(.*?)"', data, re.S)
		if xmllink:
			getxml = "http://www.bild.de" + xmllink[0]
			getPage(getxml, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.playVideo).addErrback(self.dataError)

	def playVideo(self, data):
		streamlink = re.findall('<video.*?src="(.*?)" ', data, re.S)
		if streamlink:
			self.session.open(SimplePlayer, [(self.bildName, streamlink[0])], showPlaylist=False, ltype='Bild.de')

	def keyCancel(self):
		self.close()