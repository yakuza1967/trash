from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.simpleplayer import SimplePlayer

def laolaLiveListEntry(entry):
	date_time = re.findall('(.*?,.*?),(.*?)$', entry[3], re.S)
	info = re.findall('(.*?,.*?),(.*?)$', entry[0], re.S)
	(time, date) = date_time[0]
	print time, date
	(sport, teams) = info[0]
	print sport, teams
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 20, 0, 150, 25, 0, RT_HALIGN_RIGHT | RT_VALIGN_CENTER, time),
		(eListboxPythonMultiContent.TYPE_TEXT, 20, 25, 150, 25, 0, RT_HALIGN_RIGHT | RT_VALIGN_CENTER, date),
		(eListboxPythonMultiContent.TYPE_TEXT, 200, 0, 560, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, sport),
		(eListboxPythonMultiContent.TYPE_TEXT, 200, 25, 560, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, teams)
		]

def laolaVideosListEntry(entry):
	date_time = re.findall('(.*?,.*?)$', entry[3], re.S)
	#print "date_time: "
	#print date_time
	info = re.findall('(.*?),(.*?)$', entry[0], re.S)
	#print info
	#print date_time[0]
	(sport, teams) = info[0]
	#print sport, teams
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 25, 0, 150, 25, 0, RT_HALIGN_RIGHT | RT_VALIGN_CENTER, date_time[0]),
		(eListboxPythonMultiContent.TYPE_TEXT, 200, 0, 560, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, sport),
		(eListboxPythonMultiContent.TYPE_TEXT, 200, 25, 560, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, teams)
		]

def laolaOverviewListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 0, 0, 800, 25, 0, RT_HALIGN_CENTER | RT_VALIGN_CENTER, entry[1])
		]

def laolaSubOverviewListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 0, 0, 800, 25, 0, RT_HALIGN_CENTER | RT_VALIGN_CENTER, entry[1])
		]

class laolaVideosOverviewScreen(Screen):

	def __init__(self, session):
		print 'laolaVideosOverviewScreen'
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
			"red": self.keyCancel,
			"green": self.keyLocale
		}, -1)

		self.lastservice = session.nav.getCurrentlyPlayingServiceReference()
		self.playing = False

		self.keyLocked = True

		self.locale = config.mediaportal.laola1locale.value
		print 'self.locale'
		print self.locale

		self['title'] = Label("Laola1.tv")

		if self.locale == "de":
			self['ContentTitle'] = Label("Auswahl Deutschland:")
		elif self.locale == "at":
			self['ContentTitle'] = Label("Auswahl Österreich:")
		else:
			self['ContentTitle'] = Label("Auswahl International:")
		self['name'] = Label("")
		self['F1'] = Label("Exit")
		self['F2'] = Label("Land")
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
		print 'loadPage'
		menuUrl = "http://www.laola1.tv/server/menu.php?menu=seochannels&geo=only_deu&lang=DE&ucs=style"
		if self.locale == "at":
			menuUrl = "http://www.laola1.tv/server/menu.php?menu=seochannels&geo=only_aut&lang=DE&ucs=style"
		elif self.locale == "int":
			menuUrl = "http://www.laola1.tv/server/menu.php?menu=seochannels&geo=grp_int&lang=DE&ucs=style"

		getPage(menuUrl, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.getMenuUrl).addErrback(self.dataError)

	def getMenuUrl(self, data):
		self.genreliste = re.findall('<a\shref="(.*?)"\sclass="channel1"><h2\sstyle="margin-top:inherit;\sfont-size:inherit;">(.*?)</h2>', data, re.S)
		print self.genreliste
		print len(self.genreliste)
		if self.locale == "de":
			self.genreliste.insert(0, ('http://www.laola1.tv/de/de/neueste-videos/video/0-617-.html', 'Neueste Videos'))
		if self.locale == "at":
			self.genreliste.insert(0, ('http://www.laola1.tv/de/at/neueste-videos/video/0-249-.html', 'Neueste Videos'))
		elif self.locale == "int":
			self.genreliste.insert(0, ('http://www.laola1.tv/en/int/latest-videos/video/0-878-.html', 'Neueste Videos'))

		if self.locale == "de":
			self.genreliste.insert(0, ('http://www.laola1.tv/de/de/upcoming-livestreams/video/0-1369-.html', 'Live'))
		elif self.locale == "at":
			self.genreliste.insert(0, ('http://www.laola1.tv/de/at/upcoming-livestreams/video/0-1087-.html', 'Live'))
		elif self.locale == "int":
			self.genreliste.insert(0, ('http://www.laola1.tv/en/int/upcoming-livestreams/video/0-989-.html', 'Live'))

		self.chooseMenuList.setList(map(laolaOverviewListEntry, self.genreliste))
		self['ContentTitle'].setText("Auswahl Deutschland:")
		if self.locale == "at":
			self['ContentTitle'].setText("Auswahl Österreich:")
		elif self.locale == "int":
			self['ContentTitle'].setText("Auswahl International:")
		self.keyLocked = False

	def keyOK(self):
		if self.keyLocked:
			return
		auswahl = self['genreList'].getCurrent()[0][1]
		print 'Auswahl: ' + auswahl

		self.overviewUrl = self['genreList'].getCurrent()[0][0]
		self.overviewSelection = auswahl

		getPage(self.overviewUrl, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.getUrl).addErrback(self.dataError)

	def keyCancel(self):
		self.close()

	def keyLocale(self):
		print 'keyLocale'
		if self.keyLocked:
			return
		self.keyLocked = True
		if self.locale == "de":
			self.locale = "at"
			config.mediaportal.laola1locale.value = "at"
		elif self.locale == "at":
			self.locale = "int"
			config.mediaportal.laola1locale.value = "int"
		elif self.locale == "int":
			self.locale = "de"
			config.mediaportal.laola1locale.value = "de"

		config.mediaportal.laola1locale.save()
		configfile.save()
		self.loadPage()

	def getUrl(self, data):
		print 'getUrl init'
		laUrl = self.overviewUrl
		print 'getUrl laUrl: '
		print laUrl

		if self.overviewSelection == "Neueste Videos":
			laolaTopVideosScreen.startUrl = laUrl.split('.html')[0] + ".html"
			laolaTopVideosScreen.isLive = "false"
			self.session.open(laolaTopVideosScreen)
		elif self.overviewSelection == "Live":
			laolaTopVideosScreen.startUrl = laUrl.split('.html')[0] + ".html"
			laolaTopVideosScreen.isLive = "true"
			self.session.open(laolaTopVideosScreen)
		else:
			getPage(laUrl.split('.html')[0] + ".html", headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.getSubUrl).addErrback(self.dataError)

	def getSubUrl(self, data):
		print 'getSuburl init'
		searchString = '<a href="(.*?)" style="color:#ffffff; font-weight:bold; font-size:12pt;">(.*?)<'
		print 'searchString: '+ searchString
		laUrl = re.findall(searchString, data)
		print 'getUrl laUrl: '
		print laUrl
		laolaVideosSubOverviewScreen.genreliste = laUrl
		self.session.open(laolaVideosSubOverviewScreen)

	def dataError(self, error):
		printl(error,self,"E")

class laolaVideosSubOverviewScreen(Screen):

	def __init__(self, session):
		print 'laolaVideosSubOverviewScreen'
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

		self.lastservice = session.nav.getCurrentlyPlayingServiceReference()
		self.playing = False

		self.keyLocked = True
		self['title'] = Label("Laola1.tv")
		self['ContentTitle'] = Label("Auswahl:")
		self['name'] = Label("")
		self['F1'] = Label("Exit")
		self['F2'] = Label("")
		self['F3'] = Label("")
		self['F4'] = Label("")
		self['F3'].hide()
		self['F4'].hide()

		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['genreList'] = self.chooseMenuList
		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.chooseMenuList.setList(map(laolaSubOverviewListEntry, self.genreliste))
		self.keyLocked = False

	def keyOK(self):
		if self.keyLocked:
			return
		auswahl = self['genreList'].getCurrent()[0][0]
		print 'Auswahl: ' + auswahl

		self.overviewUrl = auswahl
		laolaTopVideosScreen.startUrl = self.overviewUrl
		laolaTopVideosScreen.isLive = "false"
		self.session.open(laolaTopVideosScreen)

	def keyCancel(self):
		self.close()

class laolaTopVideosScreen(Screen):

	def __init__(self, session):
		self.session = session
		print 'Starturl:' + self.startUrl
		path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/%s/laolaScreen.xml" % config.mediaportal.skin.value
		if not fileExists(path):
			path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/original/laolaScreen.xml"
		print path
		with open(path, "r") as f:
			self.skin = f.read()
			f.close()

		Screen.__init__(self, session)

		self["actions"]  = ActionMap(["OkCancelActions", "ShortcutActions", "WizardActions", "ColorActions", "SetupActions", "NumberActions", "MenuActions", "EPGSelectActions"], {
			"ok"    : self.keyOK,
			"cancel": self.keyCancel,
			"up"    : self.keyUp,
			"down"  : self.keyDown,
			"left"  : self.keyLeft,
			"right" : self.keyRight,
			"nextBouquet" : self.keyPageUp,
			"prevBouquet" : self.keyPageDown
		}, -1)

		self.keyLocked = True
		self.page = 1
		self['title'] = Label("Laola1.tv")
		self['roflPic'] = Pixmap()
		self['name'] = Label("")
		self.laListe = []
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(50)
		self['roflList'] = self.chooseMenuList

		self.onLayoutFinish.append(self.loadNewPageData)

	#def loadPage(self):
	#	self.keyLocked = True
	#	url = "http://www.laola1.tv/"
	#	print url
	#	getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.loadNewPageData).addErrback(self.dataError)

	#def loadNewPageData(self, data):
	def loadNewPageData(self):
		self.keyLocked = True
		#laNewest = re.findall('<a href="(http://www.laola1.tv/de/at/neueste-videos/video/.*?)">', data, re.S)
		laNewest = self.startUrl
		print 'laNewest'
		print laNewest
		if laNewest:
			if self.page > 1:
				print 'newest video site: ' + laNewest.split('.html')[0] + '0-' + str(self.page) + '.html'
				getPage(laNewest.split('.html')[0] + '0-' + str(self.page) + '.html', headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.loadPageData).addErrback(self.dataError)
			else:
				print 'newest video site: ' + laNewest
				getPage(laNewest, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.loadPageData).addErrback(self.dataError)

	def loadPageData(self, data):
		if self.isLive == 'false':
			laStreams = re.findall('<div class="teaser_bild_video" title="(.*?)"><a href="(http://www.laola1.tv/.*?)"><img src="(.*?.jpg)" border="0" />.*?<div class="teaser_head_video".*?>(.*?)<', data, re.S)
			if laStreams:
				self.laListe = []
				for (laTitle,laUrl,laImage,laTime) in laStreams:
					#print 'title: ' + laTitle
					#print 'url: ' + laUrl
					#print 'image: ' + laImage
					#print 'time: ' + laTime
					self.laListe.append((laTitle,laUrl,laImage,laTime))
				self.chooseMenuList.setList(map(laolaVideosListEntry, self.laListe))
				self.showPic()
		else:
			laStreams = re.findall('<div class="teaser_bild_live" title="LIVE:.(.*?)"><a href="(http://www.laola1.tv/.*?)"><img src="(.*?.jpg)" border="0" />.*?<div class="teaser_head_live".*?>(.*?)<', data, re.S)
			if laStreams:
				self.laListe = []
				for (laTitle,laUrl,laImage,laTime) in laStreams:
					self.laListe.append((laTitle,laUrl,laImage,laTime))
				self.chooseMenuList.setList(map(laolaLiveListEntry, self.laListe))
				self.keyLocked = False
				self.showPic()
		self.keyLocked = False

	def dataError(self, error):
		printl(error,self,"E")

	def showPic(self):
		laTitle = self['roflList'].getCurrent()[0][0]
		laPicLink = self['roflList'].getCurrent()[0][2]
		self['name'].setText(laTitle)
		downloadPage(laPicLink, "/tmp/laPic.jpg").addCallback(self.roflCoverShow)

	def roflCoverShow(self, data):
		if fileExists("/tmp/laPic.jpg"):
			self['roflPic'].instance.setPixmap(gPixmapPtr())
			self.scale = AVSwitch().getFramebufferScale()
			self.picload = ePicLoad()
			size = self['roflPic'].instance.size()
			self.picload.setPara((size.width(), size.height(), self.scale[0], self.scale[1], False, 1, "#FF000000"))
			if self.picload.startDecode("/tmp/laPic.jpg", 0, 0, False) == 0:
				ptr = self.picload.getData()
				if ptr != None:
					self['roflPic'].instance.setPixmap(ptr)
					self['roflPic'].show()
					del self.picload

	def keyPageDown(self):
		print "PageDown"
		if self.keyLocked:
			return
		print self.page
		if not self.page < 2:
			self.page -= 1
			self.loadNewPageData()

	def keyPageUp(self):
		print "PageUP"
		if self.keyLocked:
			return
		self.page += 1
		print self.page
		self.loadNewPageData()

	def keyLeft(self):
		if self.keyLocked:
			return
		self['roflList'].pageUp()
		self.showPic()

	def keyRight(self):
		if self.keyLocked:
			return
		self['roflList'].pageDown()
		self.showPic()

	def keyUp(self):
		if self.keyLocked:
			return
		self['roflList'].up()
		self.showPic()

	def keyDown(self):
		if self.keyLocked:
			return
		self['roflList'].down()
		self.showPic()

	def keyOK(self):
		if self.keyLocked:
			return
		laUrl = self['roflList'].getCurrent()[0][1]
		print 'laUrl' + laUrl
		getPage(laUrl, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.parseData).addErrback(self.dataError)

	def parseData(self, data):
		if self.isLive == 'true':
			if re.match('.*?Dieser Stream ist bereits beendet', data, re.S):
				print "Dieser Stream ist bereits beendet."
				message = self.session.open(MessageBox, _("Dieser Stream ist bereits beendet."), MessageBox.TYPE_INFO, timeout=3)
			elif re.match('.*?(Dieser Stream beginnt am|This stream starts at)', data, re.S):
				print "Dieser Stream wurde noch nicht gestartet."
				message = self.session.open(MessageBox, _("Dieser Stream wurde noch nicht gestartet."), MessageBox.TYPE_INFO, timeout=3)
			else:
				id = re.findall('streamid=(.*?)&', data, re.S)
				xml = 'http://streamaccess.unas.tv/hdflash/1/hdlaola1_%s.xml?t=.smil&partnerid=1&streamid=%s' % (id[0], id[0])
				if xml:
					getPage(xml, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.parseXML).addErrback(self.dataError)
		else:
			id = re.findall('streamid=(.*?)&', data, re.S)
			hdUrl = "http://www.laola1.tv/server/hd_video.php?play=%s&partner=22&portal=2" % id[0]
			print 'hdUrl: ' + hdUrl
			if hdUrl:
				getPage(hdUrl, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.parseHdUrl).addErrback(self.dataError)

	def parseHdUrl(self, data):
			streamAccessUrl = re.findall('<url>(.*?)</url>', data, re.S)
			print 'streamAccessUrl: ' + streamAccessUrl[0].replace('&amp;','&')
			if streamAccessUrl[0]:
				getPage(streamAccessUrl[0].replace('&amp;','&'), headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.parseXML).addErrback(self.dataError)

	def parseXML(self, data):
		if self.isLive == 'true':
			laTitle = self['roflList'].getCurrent()[0][0]
			main_url = re.findall('<meta name="httpBase" content="(.*?)"', data)
			url_string = re.findall('<video src="(.*?)" system-bitrate="(.*?)"', data, re.S)
			if main_url and url_string:
				x = len(url_string)-1
				stream_url = "%s%s%s" % (main_url[0], url_string[x][0], url_string[x][1])
				print stream_url
				self.session.open(SimplePlayer, [(laTitle, stream_url)], showPlaylist=False, ltype='laola1')
		else:
			laTitle = self['roflList'].getCurrent()[0][0]
			main_url = re.findall('<meta name="httpBase" content="(.*?)"', data)
			print 'main_url: ' + main_url[0]
			url_string = re.findall('<meta name="vod" content="true" value="(.*?)"', data)
			print 'url_string: ' + url_string[0]
			params = re.findall('<video src="(.*?)"', data, re.S)
			print 'params: ' + params[0]
			if main_url and url_string and params:
				url_params = params[0].split('?')
				print 'url_params: ' + url_params[1].replace('&amp;','&')
				stream_url = "%s%s%s%s%s" % (main_url[0], url_string[0][1:] + "/bitrate=0?", url_params[1].replace('&amp;','&'), "&v=2.11.3&fp=WIN%2011,7,700,202", "&r=AAAAA"+"&g=BBBBBBBBBBBB")
				print 'stream_url: ' + stream_url
				self.session.open(SimplePlayer, [(laTitle, stream_url)], showPlaylist=False, ltype='laola1')

	def keyCancel(self):
		self.close()