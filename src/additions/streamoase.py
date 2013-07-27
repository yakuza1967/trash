from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.captcha import *
from Plugins.Extensions.MediaPortal.resources.simpleplayer import SimplePlayer
from Plugins.Extensions.MediaPortal.resources.coverhelper import CoverHelper

ck = {}

def oasetvGenreListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 20, 0, 900, 25, 0, RT_HALIGN_CENTER | RT_VALIGN_CENTER, entry[0])
		]
class oasetvGenreScreen(Screen):

	def __init__(self, session):
		self.session = session
		path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/%s/oldGenreScreen.xml" % config.mediaportal.skin.value
		if not fileExists(path):
			path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/original/oldGenreScreen.xml"
		print path
		with open(path, "r") as f:
			self.skin = f.read()
			f.close()

		Screen.__init__(self, session)

		self["actions"]  = ActionMap(["OkCancelActions", "ShortcutActions", "WizardActions", "ColorActions", "SetupActions", "NumberActions", "MenuActions"], {
			"ok"    : self.keyOK,
			"cancel": self.keyCancel
		}, -1)

		self['title'] = Label("Stream-Oase.tv")
		self['name'] = Label("Genre Auswahl")
		self['coverArt'] = Pixmap()

		self.genreliste = []
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['genreList'] = self.chooseMenuList

		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.genreliste.append(("Neuesten", "http://stream-oase.tv/index.php/hd-oase/video/latest?start="))
		self.genreliste.append(("Action", "http://stream-oase.tv/index.php/hd-oase/category/action?start="))
		self.genreliste.append(("Abenteuer", "http://stream-oase.tv/index.php/hd-oase/category/abenteuer?start="))
		self.genreliste.append(("Drama", "http://stream-oase.tv/index.php/hd-oase/category/drama?start="))
		self.genreliste.append(("Krieg", "http://stream-oase.tv/index.php/hd-oase/category/krieg?start="))
		self.genreliste.append(("Thriller", "http://stream-oase.tv/index.php/hd-oase/category/thriller?start="))
		self.genreliste.append(("Horror", "http://stream-oase.tv/index.php/hd-oase/category/horror?start="))
		self.genreliste.append(("Komoedie", "http://stream-oase.tv/index.php/hd-oase/category/komoedie?start="))
		self.genreliste.append(("Zeichentrick", "http://stream-oase.tv/index.php/hd-oase/category/zeichentrick?start="))
		self.genreliste.append(("Sci-fi", "http://stream-oase.tv/index.php/hd-oase/category/sci-fi?start="))
		self.genreliste.append(("Dokus", "http://stream-oase.tv/index.php/hd-oase/category/doku-s?start="))
		self.chooseMenuList.setList(map(oasetvGenreListEntry, self.genreliste))

	def keyOK(self):
		streamGenreLink = self['genreList'].getCurrent()[0][1]
		print streamGenreLink
		self.session.open(oasetvFilmListeScreen, streamGenreLink)

	def keyCancel(self):
		self.close()

def oaseFilmListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 20, 0, 900, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry[0])
		]
class oasetvFilmListeScreen(Screen):

	def __init__(self, session, streamGenreLink):
		self.session = session
		self.streamGenreLink = streamGenreLink
		path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/%s/oasetvFilmListeScreen.xml" % config.mediaportal.skin.value
		if not fileExists(path):
			path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/original/oasetvFilmListeScreen.xml"
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
			"prevBouquet" : self.keyPageDown
		}, -1)

		self['title'] = Label("Stream-Oase.tv")
		self['name'] = Label("Film Auswahl")
		self['handlung'] = Label("")
		self['page'] = Label("")
		self['coverArt'] = Pixmap()

		self.keyLocked = True
		self.filmliste = []
		self.keckse = {}
		self.page = 0
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['filmList'] = self.chooseMenuList

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		url = "%s%s" % (self.streamGenreLink, str(self.page))
		print url
		getPage(url, agent=std_headers, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.loadPageData).addErrback(self.dataError)

	def dataError(self, error):
		printl(error,self,"E")

	def loadPageData(self, data):
		print "daten bekommen"
		raw = re.findall('<div id="system-message-container">(.*?)<div style="clear:both"></div>', data, re.S)
		if raw:
			filme = re.findall('<a ondragstart="return false;" href="(/index.php/hd-oase/.*?)".*?<img ondragstart="return false;" class="image" src="(.*?)".*?title="Click to View : (.*?)"', raw[0], re.S)
			if filme:
				self.filmliste = []
				for (url,image,title) in filme:
					url = "http://stream-oase.tv" + url
					self.filmliste.append((decodeHtml(title), url, image))
				self.chooseMenuList.setList(map(oaseFilmListEntry, self.filmliste))
				self.keyLocked = False
				self.loadPic()

		if re.match('.*?title="Ende">Ende<', data, re.S):
			totalpages = re.findall('\?start=(.*?\d)"', data, re.S)
			if totalpages:
				if int(self.page) == 0:
					print totalpages[-1]
					pagenr = "1 / %s" % totalpages[-1]
					self['page'].setText(pagenr)
				else:
					print totalpages[-1]
					pagenr = "%s / %s" % ((int(self.page) / 56) + 1, totalpages[-1])
					self['page'].setText(pagenr)
		else:
			if int(self.page) == 0:
				self['page'].setText("1")
			else:
				pagenr = (int(self.page) / 56) + 1
				self['page'].setText(str(pagenr))

	def loadPic(self):
		streamName = self['filmList'].getCurrent()[0][0]
		streamFilmLink = self['filmList'].getCurrent()[0][1]
		self['name'].setText(streamName)
		streamPic = self['filmList'].getCurrent()[0][2]
		getPage(streamFilmLink, agent=std_headers, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.loadPageInfos).addErrback(self.dataError)
		CoverHelper(self['coverArt']).getCover(streamPic)

	def loadPageInfos(self, data):
		if re.match('.*?<strong>Inhalt:</strong></p>\r\n<p>', data, re.S):
			handlung = re.findall('<strong>Inhalt:</strong></p>\r\n<p>(.*?)</p>', data, re.S|re.I)
			if handlung:
				self['handlung'].setText(decodeHtml(handlung[0]))
			else:
				self['handlung'].setText("Keine Infos gefunden.")
		else:
			self['handlung'].setText("Keine Infos gefunden.")

	def keyOK(self):
		if self.keyLocked:
			return
		streamLink = self['filmList'].getCurrent()[0][1]
		print streamLink
		self.keyLocked = True
		getPage(streamLink, agent=std_headers, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.findStream).addErrback(self.dataError)

	def findStream(self, data):
		stream_list = []
		stream_name = self['filmList'].getCurrent()[0][0]
		streamPic = self['filmList'].getCurrent()[0][2]
		mighty = re.findall('(http://www.mightyupload.com/embed.*?)"', data, re.S)
		if mighty:
			print mighty[0]
			stream_list.append(("MightyUpload", mighty[0]))

		get_vidplay = re.findall('(http://vidplay.net/embed.*?)"', data, re.S)
		if get_vidplay:
			url = get_vidplay[0]
			print url
			stream_list.append(("vidplay", url))

		get_wupfile = re.findall('(http://wupfile.com.*?)"', data, re.S)
		if get_wupfile:
			print get_wupfile[0]
			stream_list.append(("Wupfile", get_wupfile[0]))

		self.keyLocked = False
		self.session.open(oasetvCDListeScreen, stream_list, stream_name, streamPic)

	def keyLeft(self):
		if self.keyLocked:
			return
		self['filmList'].pageUp()
		self.loadPic()

	def keyRight(self):
		if self.keyLocked:
			return
		self['filmList'].pageDown()
		self.loadPic()

	def keyUp(self):
		if self.keyLocked:
			return
		self['filmList'].up()
		self.loadPic()

	def keyDown(self):
		if self.keyLocked:
			return
		self['filmList'].down()
		self.loadPic()

	def keyPageDown(self):
		print "PageDown"
		if self.keyLocked:
			return
		if not self.page < 56:
			self.page -= 56
			self.loadPage()

	def keyPageUp(self):
		print "PageUp"
		if self.keyLocked:
			return
		self.page += 56
		self.loadPage()

	def keyCancel(self):
		self.close()

def oasetvCDListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 20, 0, 900, 25, 0, RT_HALIGN_CENTER | RT_VALIGN_CENTER, entry[0])
		]
class oasetvCDListeScreen(Screen):

	def __init__(self, session, parts, stream_name, image_url):
		self.session = session
		self.streamParts = parts
		self.stream_name = stream_name
		self.imageUrl = image_url
		path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/%s/oasetvCDListeScreen.xml" % config.mediaportal.skin.value
		if not fileExists(path):
			path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/original/oasetvCDListeScreen.xml"
		print path
		with open(path, "r") as f:
			self.skin = f.read()
			f.close()

		Screen.__init__(self, session)

		self["actions"]  = ActionMap(["OkCancelActions", "ShortcutActions", "WizardActions", "ColorActions", "SetupActions", "NumberActions", "MenuActions"], {
			"ok"    : self.keyOK,
			"cancel": self.keyCancel
		}, -1)

		self['title'] = Label("Stream-Oase.tv")
		self['name'] = Label("Part Auswahl")
		self['coverArt'] = Pixmap()

		self.keyLocked = False
		self.keckse = {}
		self.filmliste = []
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['filmList'] = self.chooseMenuList

		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		for (name,url) in self.streamParts:
			print name, url
			self.filmliste.append((name, url))
		self.chooseMenuList.setList(map(oasetvCDListEntry, self.filmliste))

	def keyOK(self):
		if self.keyLocked:
			return

		name = self['filmList'].getCurrent()[0][0]
		streamLink = self['filmList'].getCurrent()[0][1]
		self.keyLocked = True
		if name == "vidplay":
			getPage(streamLink, agent=std_headers, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.readPostData, streamLink).addErrback(self.dataError)
		elif name == "Wupfile":
			getPage(streamLink, agent=std_headers, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.postData).addErrback(self.dataError)
		elif name == "MightyUpload":
			getPage(streamLink, agent=std_headers, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.postData2).addErrback(self.dataError)
		else:
			message = self.session.open(MessageBox, _("No Supported Streamhoster."), MessageBox.TYPE_INFO, timeout=3)
			self.keyLocked = False

	def readPostData(self, data, url):
		self.vidplay_url = url
		solvemedia = re.search('<iframe src="(http://api.solvemedia.com.+?)"', data)
		url2 = solvemedia.group(1)
		data2 = urllib.urlopen(url2).read()
		self.hugekey = re.search('id="adcopy_challenge" value="(.+?)">', data2).group(1)
		print self.hugekey
		burl = "http://api.solvemedia.com%s" % re.search('<img src="(.+?)"', data2).group(1)
		#downloadPage(burl, "/tmp/captcha.jpg").addCallback(self.dowloadCatpchaDone)
		urllib.urlretrieve(burl, "/tmp/captcha.jpg")
		print "ok"
		self.data_p = {}
		r = re.findall('<input type="hidden".*?name="(.*?)".*?value="(.*?)"', data, re.S)
		if r:
			for name, value in r:
				self.data_p[name] = value
				print name, value

		print self.data_p
		self.session.openWithCallback(self.captchaCallback, VirtualKeyBoardmod, title = (_("Captcha Eingabe:")), text = "")

	def captchaCallback(self, callback = None, entry = None):
		if callback != None or callback != "":
			print callback
			self.data_p.update({'adcopy_challenge': self.hugekey,'adcopy_response': callback})
			print self.data_p
			print self.vidplay_url
			getPage(self.vidplay_url, method='POST', postdata=urlencode(self.data_p), headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.got_vidplay).addErrback(self.dataError)

		self.keyLocked = False

	def got_vidplay(self, data):
		print "data empfangen.."
		print data
		stream_url = re.findall("file: '(.*?)'", data, re.S)
		if stream_url:
			print stream_url
			self.session.open(SimplePlayer, [(self.stream_name, stream_url[0], self.imageUrl)], showPlaylist=False, ltype='streamoase', cover=True)

	def readPostData3(self, data, url):
		dataPost = {}
		r = re.findall('input type="hidden".*?name="(.*?)".*?value="(.*?)"', data, re.S)
		for name, value in r:
			dataPost[name] = value

		print urlencode(dataPost)
		getPage(url, method='POST', agent=std_headers, postdata=urlencode(dataPost), headers={'Content-Type':'application/x-www-form-urlencoded', 'referer':url}).addCallback(self.postData).addErrback(self.dataError)

	def postData(self, data):
		print data
		get_packedjava = re.findall("eval.function(.*?)</script>", data, re.S)
		print get_packedjava
		if get_packedjava:
			sUnpacked = cJsUnpacker().unpackByString(get_packedjava[1])
		if sUnpacked:
			stream_url = re.findall("'file','(.*?)'", sUnpacked)
			if stream_url:
				print stream_url[0]
				self.keyLocked = False
				self.session.open(SimplePlayer, [(self.stream_name, stream_url[0], self.imageUrl)], showPlaylist=False, ltype='streamoase', cover=True)
			else:
				message = self.session.open(MessageBox, _("Stream not found."), MessageBox.TYPE_INFO, timeout=3)
		else:
			message = self.session.open(MessageBox, _("Stream not found."), MessageBox.TYPE_INFO, timeout=3)

	def postData2(self, data):
		get_packedjava = re.findall("<script type=.text.javascript.>eval.function(.*?)</script>", data, re.S|re.DOTALL)
		if get_packedjava:
			sUnpacked = cJsUnpacker().unpackByString(get_packedjava[1])
		if sUnpacked:
			stream_url = re.findall("'file','(.*?)'", sUnpacked)
			if stream_url:
				print stream_url[0]
				self.keyLocked = False
				self.session.open(SimplePlayer, [(self.stream_name, stream_url[0], self.imageUrl)], showPlaylist=False, ltype='streamoase', cover=True)
			else:
				message = self.session.open(MessageBox, _("Stream not found."), MessageBox.TYPE_INFO, timeout=3)
		else:
			message = self.session.open(MessageBox, _("Stream not found."), MessageBox.TYPE_INFO, timeout=3)

	def dataError(self, error):
		self.keyLocked = False
		printl(error,self,"E")

	def keyCancel(self):
		self.close()