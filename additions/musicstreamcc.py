#	-*-	coding:	utf-8	-*-

from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.simpleplayer import SimplePlayer

MSCC_Version = "Musicstream.cc v0.92 (experimental)"

MSCC_siteEncoding = 'utf-8'

def show_MSCC_GenreListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 20, 0, 860, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry[1])
		]

class show_MSCC_Genre(Screen):

	R_COMP_01 = re.compile('="list_td_right"><a href="(.*?)".*?<img alt="(.*?)"')

	def __init__(self, session, url='/index.php?pwd=&d=0', ctitle="Album Auswahl"):
		self.session = session
		self.genre_url = url
		self.ctitle = ctitle

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

		self["actions"]  = ActionMap(["OkCancelActions", "ShortcutActions", "WizardActions", "ColorActions", "SetupActions", "NumberActions", "MenuActions"], {
			"ok"    : self.keyOK,
			"cancel": self.keyCancel
		}, -1)


		self['title'] = Label(MSCC_Version)
		self['ContentTitle'] = Label(self.ctitle)
		self['name'] = Label("")
		self['F1'] = Label("")
		self['F2'] = Label("")
		self['F3'] = Label("")
		self['F4'] = Label("")

		self.base_url = 'http://musicstream.cc'
		self.keylock = True
		self.genreliste = []
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['genreList'] = self.chooseMenuList

		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		getPage(self.base_url + self.genre_url, agent=std_headers, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.parseData).addErrback(self.dataError)

	def parseData(self, data):
		#liste = re.findall('="list_td_right"><a href="(.*?)".*?<img alt="(.*?)"', data)
		liste = re.findall(self.R_COMP_01, data)
		if liste:
			for (u, a) in liste:
				self.genreliste.append((decodeHtml(u), decodeHtml(a)))

		if not self.genreliste:
			self.genreliste.append(('', 'Keine Alben gefunden !'))
		else:
			self.keylock = False

		self.chooseMenuList.setList(map(show_MSCC_GenreListEntry, self.genreliste))

	def dataError(self, error):
		print "dataError: ",error

	def keyOK(self):
		if self.keylock:
			return

		album = self['genreList'].getCurrent()[0][1]
		url = self['genreList'].getCurrent()[0][0]

		if '(Sammlung ->)' in album:
			self.session.open(show_MSCC_Genre, url, 'Auswahl aus %s' % album)
		else:
			self.session.open(show_MSCC_ListScreen, url, album)

	def keyCancel(self):
		self.close()

def show_MSCC_ListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 20, 0, 860, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry[0]+entry[1])
		]

class show_MSCC_ListScreen(Screen):

	R_COMP_01 = re.compile('="list_td_right">.*?/index.php.*?id=(.*?)\'.*?="file">(.*?)</span>')

	def __init__(self, session, album_url, album):
		print "showMusicstreamccList:"

		self.session = session
		self.album_url = album_url
		self.album = album

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
			"ok" 		: self.keyOK,
			"cancel"	: self.keyCancel,
		}, -1)

		p = self.album.find('(')
		if p > 5:
			self.ctitle = self.album[:p].strip()
		else:
			self.ctitle = self.album

		self['title'] = Label(MSCC_Version)
		self['ContentTitle'] = Label(self.ctitle)
		self['name'] = Label("")
		self['F1'] = Label("")
		self['F2'] = Label("")
		self['F3'] = Label("")
		self['F4'] = Label("")

		self.keyLocked = True
		self.baseUrl = "http://musicstream.cc"

		self.filmliste = []
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['genreList'] = self.chooseMenuList

		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		print "layoutFinished:"
		url = self.baseUrl + self.album_url
		print "url: ",url
		getPage(url, agent=std_headers, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.parseData).addErrback(self.dataError)

	def parseData(self, data):
		print "parseData:"
		m = re.search('="albumimg".*?src="(.*?)"', data)
		if m:
			img = m.group(1).replace('&amp;', '&')
		else:
			img = ''

		list = re.findall(self.R_COMP_01, data)
		if list:
			for (u, t) in list:
				t = t.replace('_', ' ')
				t.replace('.mp3', '')
				self.filmliste.append(('', decodeHtml(t), self.ctitle, u.replace('&amp;', '&'), img))
				#print "t: ",t
				#print "u: ",u
				#print "img: ",img

		if len(self.filmliste) == 0:
			print "No music titles found!"
			self.filmliste.append(('', 'Keine Titel gefunden !','','',''))
		else:
			menu_len = len(self.filmliste)
			print "Music titles found: ",menu_len
			self.keyLocked = False

		self.chooseMenuList.setList(map(show_MSCC_ListEntry, self.filmliste))

	def dataError(self, error):
		print "dataError: ",error

	def keyOK(self):
		if self.keyLocked:
			return
		self.session.open(
			MusicstreamccPlayer,
			self.filmliste,
			self['genreList'].getSelectedIndex(),
			playAll = True,
			listTitle = self.ctitle
			)

	def keyCancel(self):
		self.close()

class MusicstreamccPlayer(SimplePlayer):

	def __init__(self, session, playList, playIdx=0, playAll=True, listTitle=None):
		print "MusicstreamccPlayer:"
		self.base_url = 'http://musicstream.cc'
		self.play_url = mp_globals.mscc_play_url

		SimplePlayer.__init__(self, session, playList, playIdx=playIdx, playAll=playAll, listTitle=listTitle, title_inr=1, ltype='musicstreamcc', autoScrSaver=True, cover=True)

	def getVideo(self):
		title = self.playList[self.playIdx][1]
		album = self.playList[self.playIdx][2]
		url = self.play_url % self.playList[self.playIdx][3]
		img = self.base_url + self.playList[self.playIdx][4]

		scArtist = ''
		scAlbum = album
		p = album.find(' - ')
		if p > 0:
			scArtist = album[:p].strip()
			scAlbum = album[p+3:].strip()

		p = title.find(' - ')
		if p > 0:
			scTitle = title[:p].strip()
		else:
			scTitle = title

		self.playStream(scTitle, url, scAlbum, scArtist, img)

