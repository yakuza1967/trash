#	-*-	coding:	utf-8	-*-

from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.simpleplayer import SimplePlayerMenu, SimplePlaylistIO

def eightiesGenreListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 50, 0, 800, 25, 0, RT_HALIGN_CENTER | RT_VALIGN_CENTER, entry[0])
		]

def eightiesListEntry(entry):
	#TYPE_TEXT, x, y, width, height, fnt, flags, string [, color, backColor, backColorSelected, borderWidth, borderColor])
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 50, 0, 800, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry[0])
		]

class eightiesGenreScreen(Screen):

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

		self.lastservice = session.nav.getCurrentlyPlayingServiceReference()
		self.playing = False

		self.keyLocked = True
		self['title'] = Label("80smusicvids.com / 90smusicvidz.com")
		self['ContentTitle'] = Label("Genre:")
		self['name'] = Label("")
		self['F1'] = Label("Exit")
		self['F2'] = Label("")
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
		self.genreliste = [('80s Music',"http://www.80smusicvids.com/"),
							('90s Music',"http://www.90smusicvidz.com/")]

		self.chooseMenuList.setList(map(eightiesGenreListEntry, self.genreliste))
		self.keyLocked = False

	def keyOK(self):
		if self.keyLocked:
			return
		eightiesName = self['genreList'].getCurrent()[0][0]
		eightiesUrl = self['genreList'].getCurrent()[0][1]

		print eightiesName, eightiesUrl
		self.session.open(eightiesMusicListeScreen, eightiesName, eightiesUrl)


	def keyCancel(self):
		self.session.nav.stopService()
		self.session.nav.playService(self.lastservice)
		self.playing = False
		self.close()

class eightiesMusicListeScreen(Screen, InfoBarBase, InfoBarSeek):

	def __init__(self, session, genreName, genreLink):
		self.session = session
		self.genreLink = genreLink
		self.genreName = genreName
		self.plugin_path = mp_globals.pluginPath
		self.skin_path =  mp_globals.pluginPath + "/skins"

		path = "%s/%s/showSongstoAll.xml" % (self.skin_path, config.mediaportal.skin.value)
		if not fileExists(path):
			path = self.skin_path + "/original/showSongstoAll.xml"

		with open(path, "r") as f:
			self.skin = f.read()
			f.close()

		Screen.__init__(self, session)
		InfoBarBase.__init__(self)
		InfoBarSeek.__init__(self)

		self["actions"]  = ActionMap(["OkCancelActions", "ShortcutActions", "WizardActions", "ColorActions", "SetupActions", "NumberActions", "MenuActions", "EPGSelectActions"], {
			"input_date_time" : self.openMenu,
			"ok"    : self.keyOK,
			"cancel": self.keyCancel
		}, -1)

		self.token = ''
		self.keyLocked = True
		self["title"] = Label("eighties.to - %s" % self.genreName)
		self["coverArt"] = Pixmap()
		self["songtitle"] = Label ("")
		self["artist"] = Label ("")
		self["album"] = Label ("%s" % self.genreName)
		self['F1'] = Label("")
		self['F2'] = Label("")
		self['F3'] = Label("")
		self['F4'] = Label("")

		self.filmliste = []
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['streamlist'] = self.chooseMenuList

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.keyLocked = True
		print self.genreLink

		if re.match('.*?80smusicvids.com', self.genreLink, re.S):
			self.baseurl = "http://www.80smusicvids.com/"
			self.token = '80'
		else:
			self.baseurl = "http://www.90smusicvidz.com/"
			self.token = '90'

		getPage(self.genreLink, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.loadPageData).addErrback(self.dataError)

	def loadPageData(self, data):
		print "drin"
		vids = re.findall('<a target="_self" href="(.*?)">(.*?)</a><br>', data, re.S)
		if vids:
			for url,title in vids:
				url = "%s%s" % (self.baseurl, url)
				self.filmliste.append((decodeHtml(title),url))
			self.chooseMenuList.setList(map(eightiesListEntry, self.filmliste))
			self.keyLocked = False

	def dataError(self, error):
		printl(error,self,"E")

	def openMenu(self):
		self.session.openWithCallback(self.cb_Menu, SimplePlayerMenu, 'extern')

	def cb_Menu(self, data):
		print "cb_Menu:"
		if data != []:
			if data[0] == 2:
				playinfos = self['streamlist'].getCurrent()[0][0]
				if re.match('.*?-', playinfos):
					playinfos = playinfos.split(' - ')
					if playinfos:
						if len(playinfos) == 2:
							scArtist = playinfos[0]
							scTitle = playinfos[1]
							self["artist"].setText(playinfos[0])
							self["songtitle"].setText(playinfos[1])
					else:
						playinfos = playinfos.split('-')
						if playinfos:
							if len(playinfos) == 2:
								scArtist = playinfos[0]
								scTitle = playinfos[1]
								self["artist"].setText(playinfos[0])
								self["songtitle"].setText(playinfos[1])
				else:
					self["artist"].setText(playinfos)
					scArtist = ''
					scTitle = playinfos

				url = self['streamlist'].getCurrent()[0][1]
				ltype = 'eighties'
				token = self.token
				album = self.genreName
				entry = [scTitle, url, scArtist, album, ltype, token, '']

				res = SimplePlaylistIO.addEntry(data[1], entry)
				if res == 1:
					self.session.open(MessageBox, _("Eintrag hinzugefügt"), MessageBox.TYPE_INFO, timeout=5)
				elif res == 0:
					self.session.open(MessageBox, _("Eintrag schon vorhanden"), MessageBox.TYPE_INFO, timeout=5)
				else:
					self.session.open(MessageBox, _("Fehler!"), MessageBox.TYPE_INFO, timeout=5)

	def keyOK(self):
		if self.keyLocked:
			return
		eightiesName = self['streamlist'].getCurrent()[0][0]
		eightiesUrl = self['streamlist'].getCurrent()[0][1]

		playinfos = self['streamlist'].getCurrent()[0][0]
		if re.match('.*?-', playinfos):
			playinfos = playinfos.split(' - ')
			if playinfos:
				if len(playinfos) == 2:
					scArtist = playinfos[0]
					scTitle = playinfos[1]
					self["artist"].setText(playinfos[0])
					self["songtitle"].setText(playinfos[1])
			else:
				playinfos = playinfos.split('-')
				if playinfos:
					if len(playinfos) == 2:
						scArtist = playinfos[0]
						scTitle = playinfos[1]
						self["artist"].setText(playinfos[0])
						self["songtitle"].setText(playinfos[1])
		else:
			self["artist"].setText(playinfos)
			scArtist = ''
			scTitle = playinfos

		print eightiesName, eightiesUrl
		getPage(eightiesUrl, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.getVid).addErrback(self.dataError)

	def getVid(self, data):
		stream_url = re.findall('(/vid/.*?.flv)', data, re.S)
		if stream_url:
			stream_url = "%s%s" % (self.baseurl, stream_url[0])
			print stream_url
			sref = eServiceReference(0x1001, 0, stream_url)
			self.session.nav.playService(sref)
			self.playing = True

	def doEofInternal(self, playing):
		print "Play Next Song.."
		self['streamlist'].down()
		self.keyOK()

	def seekFwd(self):
		self['streamlist'].pageDown()

	def seekBack(self):
		self['streamlist'].pageUp()

	def lockShow(self):
		pass

	def unlockShow(self):
		pass

	def keyCancel(self):
		self.close()
