from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.simpleplayer import SimplePlayer
from Plugins.Extensions.MediaPortal.resources.myvideolink import MyvideoLink

def myvideoTop100GenreListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 20, 0, 860, 25, 0, RT_HALIGN_CENTER | RT_VALIGN_CENTER, entry[0])
		]

def myvideoTop100ListEntry(entry):
	#TYPE_TEXT, x, y, width, height, fnt, flags, string [, color, backColor, backColorSelected, borderWidth, borderColor])
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 50, 0, 800, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry[0])
		]

class myvideoTop100GenreScreen(Screen):

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
		self['title'] = Label("myvideo.de")
		self['ContentTitle'] = Label("Charts:")
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
		self.genreliste = [('Top100 Single Charts',"http://www.myvideo.de/Top_100/Top_100_Single_Charts"),
							('Top100 Pop',"http://www.myvideo.de/Musik/Musik_Charts/Top_100_Pop"),
							('Top100 Rock',"http://www.myvideo.de/Musik/Musik_Charts/Top_100_Rock"),
							('Top100 Rap & RnB',"http://www.myvideo.de/Musik/Musik_Charts/Top_100_Rap/R%26B"),
							('Top100 Diverse',"http://www.myvideo.de/Musik/Musik_Charts/Top_100_Diverse")]

		self.chooseMenuList.setList(map(myvideoTop100GenreListEntry, self.genreliste))
		self.keyLocked = False

	def keyOK(self):
		if self.keyLocked:
			return
		myvideoTop100Name = self['genreList'].getCurrent()[0][0]
		myvideoTop100Url = self['genreList'].getCurrent()[0][1]

		print myvideoTop100Name, myvideoTop100Url
		self.session.open(myvideoTop100SongListeScreen, myvideoTop100Name, myvideoTop100Url)

	def keyCancel(self):
		self.close()

class myvideoTop100SongListeScreen(Screen):

	def __init__(self, session, genreName, genreLink):
		self.session = session
		self.genreLink = genreLink
		self.genreName = genreName
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
			"cancel": self.keyCancel
		}, -1)

		self.keyLocked = True
		self['title'] = Label("myvideo.de")
		self['ContentTitle'] = Label("Charts: %s" % self.genreName)
		self['name'] = Label("")
		self['F1'] = Label("Exit")
		self['F2'] = Label("")
		self['F3'] = Label("")
		self['F4'] = Label("")
		self['F3'].hide()
		self['F4'].hide()

		self.filmliste = []
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['genreList'] = self.chooseMenuList

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.keyLocked = True
		print self.genreLink
		getPage(self.genreLink, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.loadPageData).addErrback(self.dataError)

	def loadPageData(self, data):
		print "drin"
		charts = re.findall("<a href='/watch/.*?' title='(.*?)'><img id='i(\d+)'.*?longdesc='(.*?.jpg)'.*?<span class='vViews'>(.*?)</span>.*?<span class='chartTop.*?'>(.*?)</span>", data, re.S)
		if charts:
			self.filmliste = []
			#'Le Kid -- We are young', '9047978', 'http://img5.myvideo.de/web/138/movie35/35/thumbs/9047978_1.jpg', '03:28 min', '77'
			for (title, id, image, min, place) in charts:
				title = "%s. %s" % (place, decodeHtml(title))
				"""
				url = "http://www.myvideo.de/dynamic/get_player_video_xml.php?flash_playertype=D&ID=%s&_countlimit=4&autorun=yes" % id
				"""
				url = "http://www.myvideo.de/dynamic/get_player_video_xml.php?flash_playertype=D&ID=%s" % id
				self.filmliste.append((title,url,id,image))
			self.chooseMenuList.setList(map(myvideoTop100ListEntry, self.filmliste))
			self.keyLocked = False

	def dataError(self, error):
		printl(error,self,"E")

	def keyOK(self):
		if self.keyLocked:
			return
		myvideoTop100Name = self['genreList'].getCurrent()[0][0]
		myvideoTop100Url = self['genreList'].getCurrent()[0][1]
		idx = self['genreList'].getSelectedIndex()

		print idx, myvideoTop100Name, myvideoTop100Url
		self.session.open(myvideoTop100Player, self.filmliste, int(idx) , True, self.genreName)

	def keyCancel(self):
		self.close()

class myvideoTop100Player(SimplePlayer):

	def __init__(self, session, playList, playIdx=0, playAll=True, listTitle=None):
		print "myvideoTop100Player:"
		print listTitle

		SimplePlayer.__init__(self, session, playList, playIdx=playIdx, playAll=playAll, listTitle=listTitle, ltype='myvideo')

		self.onLayoutFinish.append(self.getVideo)

	def getVideo(self):
		titel = self.playList[self.playIdx][self.title_inr]
		url = self.playList[self.playIdx][1]
		token = self.playList[self.playIdx][2]
		imgurl = self.playList[self.playIdx][3]
		print titel, url, token

		MyvideoLink(self.session).getLink(self.playStream, self.dataError, titel, url, token, imgurl=imgurl)