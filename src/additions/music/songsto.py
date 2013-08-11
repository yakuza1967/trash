#	-*-	coding:	utf-8	-*-

from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.simpleplayer import SimplePlayer
from Plugins.Extensions.MediaPortal.resources.songstolink import SongstoLink

def SongstoListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 20, 0, 860, 25, 0, RT_HALIGN_CENTER | RT_VALIGN_CENTER, entry[0])
		]
class showSongstoGenre(Screen):

	def __init__(self, session):
		self.session = session
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

		self["actions"]  = ActionMap(["OkCancelActions", "ShortcutActions", "WizardActions", "ColorActions", "SetupActions", "NumberActions", "MenuActions", "MoviePlayerActions"], {
			"ok"    : self.keyOK,
			"cancel": self.keyCancel
		}, -1)

		self["title"] = Label("Songs.to Music Player")
		self['ContentTitle'] = Label('Music Tops')
		self['name'] = Label("Auswahl:")
		self['F1'] = Label("Exit")
		self['F2'] = Label("")
		self['F3'] = Label("")
		self['F4'] = Label("")

		self.streamList = []
		self.streamMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.streamMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.streamMenuList.l.setItemHeight(25)
		self["genreList"] = self.streamMenuList

		self.keyLocked = False
		self.playing = False
		self.lastservice = session.nav.getCurrentlyPlayingServiceReference()

		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.keyLocked = True
		scGenre = [("Songs Top 500", "http://songs.to/json/songlist.php?top=all"),
			("Singles Top 100", "http://songs.to/json/songlist.php?charts=music_single_de"),
			("Dance Top 50", "http://songs.to/json/songlist.php?charts=music_dance_de"),
			("Black Top 20", "http://songs.to/json/songlist.php?charts=music_black_de"),
			("Singles US Top 20", "http://songs.to/json/songlist.php?charts=music_single_us"),
			("Singles UK Top 40", "http://songs.to/json/songlist.php?charts=music_single_uk"),
			("Metal-Rock Top 15", "http://songs.to/json/songlist.php?charts=music_album_mrc"),
			("Schlager Top 30", "http://songs.to/json/songlist.php?charts=music_schlager_de"),
			("Singles Jahr 2011", "http://songs.to/json/songlist.php?charts=music_year2011_de"),
			("Singles Jahr 2012", "http://songs.to/json/songlist.php?charts=music_year2012_de"),
			("Album Top 50", "http://songs.to/json/songlist.php?charts=music_album_de")]

		for (scName, scUrl) in scGenre:
			self.streamList.append((scName, scUrl))
		self.streamMenuList.setList(map(SongstoListEntry, self.streamList))
		self.keyLocked = False

	def keyOK(self):
		if self.keyLocked:
			return
		scName = self['genreList'].getCurrent()[0][0]
		scUrl = self['genreList'].getCurrent()[0][1]
		if scName == "Songs Top 500":
			print scName, "showAll"
			self.session.open(showSongstoAll, scUrl, scName)
		else:
			print scName, "showTop"
			self.session.open(showSongstoTop, scUrl, scName)

	def keyCancel(self):
		self.close()

class showSongstoAll(Screen):

	def __init__(self, session, link, name):
		self.session = session
		self.scLink = link
		self.scGuiName = name
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

		self["actions"]  = ActionMap(["OkCancelActions", "ShortcutActions", "WizardActions", "ColorActions", "SetupActions", "NumberActions", "MenuActions", "EPGSelectActions"], {
			"ok" : self.keyOK,
			"cancel" : self.keyCancel
		}, -1)

		self["title"] = Label("Songs.to Music Player")
		self['ContentTitle'] = Label(self.scGuiName)
		self['name'] = Label("Auswahl:")
		self['F1'] = Label("Exit")
		self['F2'] = Label("")
		self['F3'] = Label("")
		self['F4'] = Label("")

		self.streamList = []
		self.streamMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.streamMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.streamMenuList.l.setItemHeight(25)
		self["genreList"] = self.streamMenuList

		self.keyLocked = False

		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.keyLocked = True
		if self.scGuiName != "Songs Top 500":
			print "data:",self.scLink
			self.scData(self.scLink)
		else:
			getPage(self.scLink, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.scData).addErrback(self.dataError)

	def scData(self, data):
		findSongs = re.findall('"hash":"(.*?)","title":"(.*?)","artist":"(.*?)","album":"(.*?)".*?"cover":"(.*?)"', data, re.S)
		if findSongs:
			for (scHash,scTitle,scArtist,scAlbum,scCover) in findSongs:
				self.streamList.append((decodeHtml(scTitle), decodeHtml(scArtist), scAlbum, scCover, scHash))
			self.streamMenuList.setList(map(self.streamListEntry, self.streamList))
			self.keyLocked = False

	def streamListEntry(self, entry):
		title = entry[1] + " - " + entry[0]
		return [entry,
			(eListboxPythonMultiContent.TYPE_TEXT, 50, 0, 830, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, title)
			]

	def dataError(self, error):
		printl(error,self,"E")

	def keyOK(self):
		if self.keyLocked:
			print self.keyLocked
			return

		idx = self["genreList"].getSelectedIndex()
		self.session.open(SongstoPlayer, self.streamList, 'songstoall', int(idx), self.scGuiName)

	def keyCancel(self):
		self.close()

class showSongstoTop(Screen):

	def __init__(self, session, link, name):
		self.session = session
		self.scLink = link
		self.scGuiName = name
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

		self["actions"]  = ActionMap(["OkCancelActions", "ShortcutActions", "WizardActions", "ColorActions", "SetupActions", "NumberActions", "MenuActions", "EPGSelectActions"], {
			"ok" : self.keyOK,
			"cancel" : self.keyCancel
		}, -1)

		self["title"] = Label("Songs.to Music Player")
		self['ContentTitle'] = Label(self.scGuiName)
		self['name'] = Label("Auswahl:")
		self['F1'] = Label("Exit")
		self['F2'] = Label("")
		self['F3'] = Label("")
		self['F4'] = Label("")

		self.streamList = []
		self.streamMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.streamMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.streamMenuList.l.setItemHeight(25)
		self["genreList"] = self.streamMenuList

		self.keyLocked = False

		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.keyLocked = True
		getPage(self.scLink, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.scDataGet).addErrback(self.dataError)

	def scDataGet(self, data):
		findSongs = re.findall('name1":"(.*?)","name2":"(.*?)"', data, re.S)
		if findSongs:
			for (scArtist, scTitle) in findSongs:
				self.streamList.append((decodeHtml(scTitle), decodeHtml(scArtist)))
			self.streamMenuList.setList(map(self.streamListEntry, self.streamList))
			self.keyLocked = False

	def streamListEntry(self, entry):
		title = entry[1] + " - " + entry[0]
		return [entry,
			(eListboxPythonMultiContent.TYPE_TEXT, 50, 0, 830, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, title)
			]

	def scDataPost(self, data):
		self.keyLocked = False
		self.session.open(showSongstoAll, data, self.artist + ' - ' + self.album)
		
	def dataError(self, error):
		printl(error,self,"E")

	def keyOK(self):
		if self.keyLocked:
			return

		if self.scGuiName == "Album Top 50":
			self.keyLocked = True
			self.artist = self['genreList'].getCurrent()[0][1]
			self.album = self['genreList'].getCurrent()[0][0]
			url = "http://songs.to/json/songlist.php?quickplay=1"
			dataPost = "data=%7B%22data%22%3A%5B%7B%22artist%22%3A%22"+self.artist+"%22%2C%20%22album%22%3A%22"+self.album+"%22%2C%20%22title%22%3A%22%22%7D%5D%7D"
			#print "datapost:",dataPost
			getPage(url, method='POST', postdata=dataPost, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.scDataPost).addErrback(self.dataError)
		else:
			idx = self["genreList"].getSelectedIndex()
			self.session.open(SongstoPlayer, self.streamList, 'songstotop', int(idx), self.scGuiName)

	def keyCancel(self):
		self.close()

class SongstoPlayer(SimplePlayer):

	def __init__(self, session, playList, songsto_type, playIdx=0, listTitle=None):
		print "SongstoPlayer:"
		self.songsto_type = songsto_type

		SimplePlayer.__init__(self, session, playList, playIdx=playIdx, playAll=True, listTitle=listTitle, ltype='songsto', cover=True, autoScrSaver=True, listEntryPar=[20, 0, 860, 25, 0, ' - ', 1, 0])

		self.onLayoutFinish.append(self.getVideo)

	def getVideo(self):
		sc_artist = self.playList[self.playIdx][1]
		sc_title = self.playList[self.playIdx][self.title_inr]
		if self.songsto_type == 'songstotop':
			sc_album = ''
			token = ''
			imgurl = ''
		else:
			sc_album = self.playList[self.playIdx][2]
			token = self.playList[self.playIdx][4]
			imgurl = self.playList[self.playIdx][3]
			imgurl = "http://songs.to/covers/"+imgurl

		SongstoLink(self.session).getLink(self.playStream, self.dataError, sc_title, sc_artist, sc_album, token, imgurl)
