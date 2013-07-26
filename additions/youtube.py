#	-*-	coding:	utf-8	-*-

from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.youtubeplayer import YoutubePlayer
from Plugins.Extensions.MediaPortal.resources.coverhelper import CoverHelper

YT_Version = "Youtube Search v1.00 (experimental)"

YT_siteEncoding = 'utf-8'

def YT_menuListentry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 20, 0, 860, 25, 0, RT_HALIGN_CENTER | RT_VALIGN_CENTER, entry[0])
		]

class youtubeGenreScreen(Screen):

	def __init__(self, session):
		self.session = session

		self.plugin_path = mp_globals.pluginPath
		self.skin_path =  mp_globals.pluginPath + "/skins"

		path = "%s/%s/ytSearchScreen.xml" % (self.skin_path, config.mediaportal.skin.value)
		if not fileExists(path):
			path = self.skin_path + "/original/ytSearchScreen.xml"

		print path
		with open(path, "r") as f:
			self.skin = f.read()
			f.close()

		Screen.__init__(self, session)

		self["actions"] = ActionMap(["OkCancelActions", "ShortcutActions", "WizardActions", "ColorActions", "SetupActions", "NumberActions", "MenuActions", "EPGSelectActions"], {
			"ok"    : self.keyOK,
			"cancel": self.keyCancel,
			"up"	: self.keyUp,
			"down"	: self.keyDown,
			"left"	: self.keyLeft,
			"right"	: self.keyRight,
			"red"	: self.keyRed,
			#"green"	: self.keyGreen,
			"yellow": self.keyYellow
		}, -1)

		self['title'] = Label(YT_Version)
		self['ContentTitle'] = Label("VIDEOSUCHE")
		self['name'] = Label("")
		self['F1'] = Label("Parameter")
		self['F2'] = Label("")
		self['F3'] = Label("Edit")
		self['F4'] = Label("")
		self['Query'] = Label("Suchanfrage")
		self['query'] = Label("")
		self['Time'] = Label("Zeitbereich")
		self['time'] = Label("")
		self['Metalang'] = Label("Meta Sprache")
		self['metalang'] = Label("")
		self['Regionid'] = Label("Suchregion")
		self['regionid'] = Label("")
		self['Author'] = Label("Uploader")
		self['author'] = Label("")
		self['Keywords'] = Label("")
		self['keywords'] = Label("")
		self['Parameter'] = Label("Parameter")
		self['ParameterToEdit'] = Label("Edit:")
		self['parametertoedit'] = Label("")
		self['3D'] = Label("3D Suche")
		self['3d'] = Label("")
		self['Duration'] = Label("Laufzeit")
		self['duration'] = Label("")
		self['Reserve1'] = Label("")
		self['reserve1'] = Label("")
		self['Reserve2'] = Label("")
		self['reserve2'] = Label("")

		self.param_qr = ""
		self.param_lr_idx = 0
		self.param_kw = ""
		self.param_regionid_idx = 0
		self.param_time_idx = 0
		self.param_meta_idx = 0
		self.paramListIdx = 0
		self.param_author = ""
		self.param_3d_idx = 0
		self.param_duration_idx = 0
		self.old_mainidx = -1

		self.menuLevel = 0
		self.menuMaxLevel = 2
		self.menuIdx = [0,0,0]
		self.keyLocked = True
		self.genreSelected = False
		self.menuListe = []
		self.baseUrl = "http://gdata.youtube.com/feeds/api"
		self.genreName = ["","","",""]
		self.genreUrl = ["","","",""]
		self.genreBase = ""
		self.genreTitle = ""
		#self.keckse = {}
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['genreList'] = self.chooseMenuList

		#self.param_restriction = ['restriction=DE']
		self.param_safesearch = ['&safeSearch=none']
		self.param_format = '&format=5'

		self.subCat = [
			('Keine Kategorie', ''),
			('Autos & Fahrzeuge', 'Autos'),
			('Bildung', 'Education'),
			('Comedy', 'Comedy'),
			('Film & Animation', 'Film'),
			('Hilfen / Anleitungen', 'Howto'),
			('Musik', 'Music'),
			('Nachrichten & Politik', 'News'),
			('Leute & Blogs', 'People'),
			('Reisen & Veranstaltungen', 'Travel'),
			('Sport', 'Sports'),
			('Tiere', 'Pets'),
			('Unterhaltung', 'Entertainment'),
			('Wissenschaft & Technik', 'Tech')
			]

		self.subGenre_0 = [
			("Top bewertet", "/top_rated"),
			("Top Favoriten", "/top_favorites"),
			("Meist populär", "/most_popular"),
			("Meist diskutiert", "/most_discussed"),
			("Meist geantwortet", "/most_responded"),
			("Meist gesehen", "/most_viewed")
			]

		self.param_time = [
			("Alle", "time=all_time"),
			("Diese Woche", "time=this_week"),
			("Diesen Monat", "time=this_month"),
			("Heute", "time=today")
			]

		self.param_metalang = [
			('Englisch', '&lr=en'),
			('Deutsch', '&lr=de'),
			('Französisch', '&lr=fr'),
			('Italienisch', '&lr=it'),
			('Alle', '')
			]

		self.param_regionid = [
			('Ganze Welt', ''),
			('England', '/EN'),
			('Deutschland', '/DE'),
			('Frankreich', '/FR'),
			('Italien', '/IT')
			]

		self.param_duration = [
			('Alle', ''),
			('< 4 Min', '&duration=short'),
			('4..20 Min', '&duration=medium'),
			('> 20 Min', '&duration=long')
			]

		self.param_3d = [
			('AUS', ''),
			('EIN', '&3d=true')
			]

		self.paramList = [
			('Suchanfrage', self.paraQuery, [0,1,2,3,4]),
			('Zeitbereich', self.paraTime, [0,1]),
			('Meta Sprache', self.paraMeta, [1]),
			('Uploader', self.paraAuthor, [1]),
			('3D Suche', self.para3D, [0,1]),
			('Laufzeit', self.paraDuration, [0,1]),
			('Suchregion', self.paraRegionID, [0])
			#('Schlüsselworte', self.paraKey)
			]

		self.genreMenu = [
			[
			('Standard feeds', '/standardfeeds'),
			('Video feeds', '/videos'),
			('Playlist feeds', '/playlists/snippets'),
			('Channel feeds', '/channels'),
			('Favoriten', '')
			],
			[
			self.subGenre_0, self.subCat, None, None, None
			],
			[
			[self.subCat,self.subCat,self.subCat,self.subCat,self.subCat,self.subCat],
			[None,None,None,None,None,None,None,None,None,None,None,None,None,None],
			None,
			None,
			None
			]
			]

		"""
			[
			self.param_time,self.param_time,self.param_time2,self.param_time,self.param_time,self.param_time,self.param_time,self.param_time
			],
			[None]
			]
		"""

		self.onLayoutFinish.append(self.loadMenu)

	def paraQuery(self):
		self.session.openWithCallback(self.cb_paraQuery, VirtualKeyBoard, title = (_("Suchanfrage")), text = self.param_qr)

	def cb_paraQuery(self, callback = None, entry = None):
		if callback != None:
			self.param_qr = callback.strip()
			self.showParams()

	def paraTime(self):
		self.param_time_idx += 1
		if self.param_time_idx not in range(0, len(self.param_time)):
			self.param_time_idx = 0

	def para3D(self):
		self.param_3d_idx += 1
		if self.param_3d_idx not in range(0, len(self.param_3d)):
			self.param_3d_idx = 0

	def paraDuration(self):
		self.param_duration_idx += 1
		if self.param_duration_idx not in range(0, len(self.param_duration)):
			self.param_duration_idx = 0

	def paraMeta(self):
		self.param_meta_idx += 1
		if self.param_meta_idx not in range(0, len(self.param_metalang)):
			self.param_meta_idx = 0

	def paraRegionID(self):
		self.param_regionid_idx += 1
		if self.param_regionid_idx not in range(0, len(self.param_regionid)):
			self.param_regionid_idx = 0

	def paraAuthor(self):
		self.session.openWithCallback(self.cb_paraAuthor, VirtualKeyBoard, title = (_("Author")), text = self.param_author)

	def cb_paraAuthor(self, callback = None, entry = None):
		if callback != None:
			self.param_author = callback.strip()
			self.showParams()

	def paraKey(self):
		self.session.openWithCallback(self.cb_paraKey, VirtualKeyBoard, title = (_("Suchschlüssel")), text = self.param_kw)

	def cb_paraKey(self, callback = None, entry = None):
		if callback != None:
			self.param_kw = callback.strip()
			self.showParams()

	def showParams(self):
		self['query'].setText(self.param_qr)
		self['time'].setText(self.param_time[self.param_time_idx][0])
		self['metalang'].setText(self.param_metalang[self.param_meta_idx][0])
		self['regionid'].setText(self.param_regionid[self.param_regionid_idx][0])
		self['3d'].setText(self.param_3d[self.param_3d_idx][0])
		self['duration'].setText(self.param_duration[self.param_duration_idx][0])
		self['author'].setText(self.param_author)
		self['keywords'].setText(self.param_kw)
		self['parametertoedit'].setText(self.paramList[self.paramListIdx][0])
		self.paramShowHide()

	def paramShowHide(self):
		if self.old_mainidx == self.menuIdx[0]:
			return
		else:
			self.old_mainidx = self.menuIdx[0]

		if self.menuIdx[0] in self.paramList[0][2]:
			self['query'].show()
			self['Query'].show()
		else:
			self['query'].hide()
			self['Query'].hide()

		if self.menuIdx[0] in self.paramList[1][2]:
			self['time'].show()
			self['Time'].show()
		else:
			self['time'].hide()
			self['Time'].hide()

		if self.menuIdx[0] in self.paramList[2][2]:
			self['metalang'].show()
			self['Metalang'].show()
		else:
			self['metalang'].hide()
			self['Metalang'].hide()

		if self.menuIdx[0] in self.paramList[6][2]:
			self['regionid'].show()
			self['Regionid'].show()
		else:
			self['regionid'].hide()
			self['Regionid'].hide()

		if self.menuIdx[0] in self.paramList[4][2]:
			self['3d'].show()
			self['3D'].show()
		else:
			self['3d'].hide()
			self['3D'].hide()

		if self.menuIdx[0] in self.paramList[5][2]:
			self['duration'].show()
			self['Duration'].show()
		else:
			self['duration'].hide()
			self['Duration'].hide()

		if self.menuIdx[0] in self.paramList[3][2]:
			self['author'].show()
			self['Author'].show()
		else:
			self['author'].hide()
			self['Author'].hide()

	def setGenreStrTitle(self):
		print "setGenreStrTitle:"
		genreName = self['genreList'].getCurrent()[0][0]
		genreLink = self['genreList'].getCurrent()[0][1]
		print "genreName: ", genreName
		print "genreLink: ", genreLink
		if self.menuLevel in range(self.menuMaxLevel+1):
			if self.menuLevel == 0:
				self.genreName[self.menuLevel] = genreName
			else:
				self.genreName[self.menuLevel] = ':'+genreName

			self.genreUrl[self.menuLevel] = genreLink

		self.genreTitle = "%s%s%s" % (self.genreName[0],self.genreName[1],self.genreName[2])
		self['name'].setText("Genre: "+self.genreTitle)
		print "genreTitle: ", self.genreTitle

		self.keyRed(0)

		"""
		if self.genreSelected:
			print "Genre selected"
			self['F2'].setText("Start")
		else:
			self['F2'].setText("")
		"""

	def loadMenu(self):
		print "Youtube:"
		self.showParams()
		self.setMenu(0, True)
		self.keyLocked = False

	def keyRed(self, inc=1):
		old_idx = self.paramListIdx
		self.paramListIdx += inc

		c= len(self.paramList)
		while True:
			if self.paramListIdx not in range(0, c):
				self.paramListIdx = 0

			if self.menuIdx[0] in self.paramList[self.paramListIdx][2]:
				break
			else:
				self.paramListIdx += 1

			if old_idx == self.paramListIdx:
				break

		self.showParams()

	def openListScreen(self):
		if self.genreSelected:
			print "Genre selected"
			qr = '&q='+urllib.quote(self.param_qr)
			tm = self.param_time[self.param_time_idx][1]
			lr = self.param_metalang[self.param_meta_idx][1]
			regionid = self.param_regionid[self.param_regionid_idx][1]
			_3d = self.param_3d[self.param_3d_idx][1]
			dura = self.param_duration[self.param_duration_idx][1]

			if re.match('Favoriten', self.genreTitle):
				genreurl = ''
			elif re.match('Standard', self.genreTitle):
				stdGenre = self.genreUrl[2]
				if stdGenre != '':
					stdGenre = '_'+stdGenre
				genreurl = self.baseUrl+self.genreUrl[0]+regionid+self.genreUrl[1]+stdGenre+'?'+tm+lr+qr+self.param_format+self.param_safesearch[0]+_3d+dura+'&'
			else:
				if self.genreUrl[1] != '':
					c = '/-/'+self.genreUrl[1]
				else:
					c = ''

				if re.match('Video', self.genreTitle) and self.param_author != '':
					at = '&author=' + urllib.quote(self.param_author)
				else:
					at = ''

				genreurl = self.baseUrl+self.genreUrl[0]+c+'?'+tm+lr+qr+self.param_format+self.param_safesearch[0]+at+_3d+dura+'&'

			#print "genreurl: ", genreurl
			self.session.open(YT_ListScreen, genreurl, self.genreTitle)

	def keyYellow(self):
		if self.menuIdx[0] in self.paramList[self.paramListIdx][2]:
			self.paramList[self.paramListIdx][1]()
			self.showParams()

	def keyUp(self):
		self['genreList'].up()
		self.menuIdx[self.menuLevel] = self['genreList'].getSelectedIndex()
		self.setGenreStrTitle()

	def keyDown(self):
		self['genreList'].down()
		self.menuIdx[self.menuLevel] = self['genreList'].getSelectedIndex()
		self.setGenreStrTitle()

	def keyMenuUp(self):
		print "keyMenuUp:"
		if self.keyLocked:
			return
		self.menuIdx[self.menuLevel] = self['genreList'].getSelectedIndex()
		self.setMenu(-1)

	def keyRight(self):
		self['genreList'].pageDown()
		self.menuIdx[self.menuLevel] = self['genreList'].getSelectedIndex()
		self.setGenreStrTitle()

	def keyLeft(self):
		self['genreList'].pageUp()
		self.menuIdx[self.menuLevel] = self['genreList'].getSelectedIndex()
		self.setGenreStrTitle()

	def keyOK(self):
		print "keyOK:"
		if self.keyLocked:
			return

		self.menuIdx[self.menuLevel] = self['genreList'].getSelectedIndex()
		self.setMenu(1)

		if self.genreSelected:
			print "Genre selected"
			#self['F2'].setText("Start")
			self.openListScreen()

	def setMenu(self, levelIncr, menuInit=False):
		print "setMenu: ",levelIncr
		self.genreSelected = False
		if (self.menuLevel+levelIncr) in range(self.menuMaxLevel+1):
			if levelIncr < 0:
				self.genreName[self.menuLevel] = ""

			self.menuLevel += levelIncr

			if levelIncr > 0 or menuInit:
				self.menuIdx[self.menuLevel] = 0

			if self.menuLevel == 0:
				print "level-0"
				if self.genreMenu[0] != None:
					self.menuListe = []
					for (Name,Url) in self.genreMenu[0]:
						self.menuListe.append((Name,Url))
					self.chooseMenuList.setList(map(YT_menuListentry, self.menuListe))
					self['genreList'].moveToIndex(self.menuIdx[0])
				else:
					self.genreName[self.menuLevel] = ""
					self.genreUrl[self.menuLevel] = ""
					print "No menu entrys!"
			elif self.menuLevel == 1:
				print "level-1"
				if self.genreMenu[1][self.menuIdx[0]] != None:
					self.menuListe = []
					for (Name,Url) in self.genreMenu[1][self.menuIdx[0]]:
						self.menuListe.append((Name,Url))
					self.chooseMenuList.setList(map(YT_menuListentry, self.menuListe))
					self['genreList'].moveToIndex(self.menuIdx[1])
				else:
					self.genreName[self.menuLevel] = ""
					self.genreUrl[self.menuLevel] = ""
					self.menuLevel -= levelIncr
					self.genreSelected = True
					print "No menu entrys!"
			elif self.menuLevel == 2:
				print "level-2"
				if self.genreMenu[2][self.menuIdx[0]][self.menuIdx[1]] != None:
					self.menuListe = []
					for (Name,Url) in self.genreMenu[2][self.menuIdx[0]][self.menuIdx[1]]:
						self.menuListe.append((Name,Url))
					self.chooseMenuList.setList(map(YT_menuListentry, self.menuListe))
					self['genreList'].moveToIndex(self.menuIdx[2])
				else:
					self.genreName[self.menuLevel] = ""
					self.genreUrl[self.menuLevel] = ""
					self.menuLevel -= levelIncr
					self.genreSelected = True
					print "No menu entrys!"
		else:
			print "Entry selected"
			self.genreSelected = True

		print "menuLevel: ",self.menuLevel
		print "mainIdx: ",self.menuIdx[0]
		print "subIdx_1: ",self.menuIdx[1]
		print "subIdx_2: ",self.menuIdx[2]
		print "genreSelected: ",self.genreSelected
		print "menuListe: ",self.menuListe
		print "genreUrl: ",self.genreUrl

		self.setGenreStrTitle()

	def keyCancel(self):
		if self.menuLevel == 0:
			self.close()
		else:
			self.keyMenuUp()


def YT_ListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 20, 0, 860, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry[0]+entry[1])
		]

class YT_ListScreen(Screen):

	def __init__(self, session, stvLink, stvGenre):
		self.session = session
		self.stvLink = stvLink
		self.genreName = stvGenre

		self.plugin_path = mp_globals.pluginPath
		self.skin_path =  mp_globals.pluginPath + "/skins"

		path = "%s/%s/dokuListScreen.xml" % (self.skin_path, config.mediaportal.skin.value)
		if not fileExists(path):
			path = self.skin_path + "/original/dokuListScreen.xml"

		print path
		with open(path, "r") as f:
			self.skin = f.read()
			f.close()

		Screen.__init__(self, session)

		self["actions"]  = ActionMap(["OkCancelActions", "ShortcutActions", "WizardActions", "ColorActions", "SetupActions", "NumberActions", "MenuActions", "EPGSelectActions"], {
			"ok" 		: self.keyOK,
			"cancel"	: self.keyCancel,
			"up" 		: self.keyUp,
			"down" 		: self.keyDown,
			"right" 	: self.keyRight,
			"left" 		: self.keyLeft,
			"nextBouquet": self.keyPageUpFast,
			"prevBouquet": self.keyPageDownFast,
			"red" 		:  self.keyTxtPageUp,
			"blue" 		:  self.keyTxtPageDown,
			"yellow"	: self.keyYellow,
			"green"		: self.keyGreen,
			"1" 		: self.key_1,
			"3" 		: self.key_3,
			"4" 		: self.key_4,
			"6" 		: self.key_6,
			"7" 		: self.key_7,
			"9" 		: self.key_9
		}, -1)

		self.favoGenre = re.match('Favoriten', self.genreName)
		self.playlistGenre = re.match('Playlist', self.genreName)
		self.channelGenre = re.match('Channel', self.genreName)

		self['title'] = Label(YT_Version)
		self['ContentTitle'] = Label(self.genreName)
		self['name'] = Label("")
		self['handlung'] = ScrollLabel("")
		self['page'] = Label("")
		if not self.favoGenre:
			self['F1'] = Label("Text-")
			self['F2'] = Label("Favorit")
			self['F3'] = Label("")
			self['F4'] = Label("Text+")
		else:
			self['F1'] = Label("Löschen")
			self['F2'] = Label("")
			self['F3'] = Label("")
			self['F4'] = Label("")

		self['VideoPrio'] = Label("")
		self['vPrio'] = Label("")
		self['Page'] = Label("Page")
		self['coverArt'] = Pixmap()

		self.keyLocked = True
		self.baseUrl = "http://www.youtube.com"

		self.videoPrio = int(config.mediaportal.youtubeprio.value)
		self.videoPrioS = ['L','M','H']
		self.setVideoPrio()

		self.favo_path = config.mediaportal.watchlistpath.value + "mp_yt_favorites.xml"
		self.keckse = {}
		self.filmliste = []
		self.start_idx = 1
		self.max_res = 12
		self.total_res = 0
		self.pages = 0
		self.page = 0
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['liste'] = self.chooseMenuList

		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.loadPageData()

	def loadPageData(self):
		self.keyLocked = True
		print "getPage: ",self.stvLink

		self.filmliste = []
		self.filmliste.append(('Bitte warten...','','','','',''))
		self.chooseMenuList.setList(map(YT_ListEntry, self.filmliste))

		if self.favoGenre:
			self.getFavos()
		else:
			url = self.stvLink+"start-index=%d&max-results=%d&v=2" % (self.start_idx, self.max_res)
			print "YT-Url: ",url
			getPage(url, cookies=self.keckse, agent=std_headers, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.genreData).addErrback(self.dataError)

	def genreData(self, data):
		print "genreData:"
		if not self.pages:
			m = re.search('totalResults>(.*?)</', data)
			if m:
				a = int(m.group(1))
				self.pages = a // self.max_res
				if a % self.max_res:
					self.pages += 1
				if self.pages > 83:
					self.pages = 83
				self.page = 1

		a = 0
		l = len(data)
		self.filmliste = []
		if self.playlistGenre:
			while a < l:
				mg = re.search('<entry gd:etag=(.*?)</entry>', data[a:], re.S)
				if mg:
					a += mg.end()
					m1 = re.search('<summary>(.*?)</summary>', mg.group(1), re.S)
					m2 = re.search('<title>(.*?)</title>.*?src=\'(.*?)\'.*?url=\'(.*?)\'.*?height=\'180\'', mg.group(1), re.S)
					if m2:
						title = decodeHtml(m2.group(1))
						if m1:
							desc = decodeHtml(m1.group(1))
						else:
							desc = "Keine weiteren Info's vorhanden."
						url = m2.group(2)
						img = m2.group(3)

						self.filmliste.append(('', title, url, img, desc, 'P'))
				else:
					a = l

			if len(self.filmliste) == 0:
				print "No playlist found!"
				self.pages = 0
				self.filmliste.append(('Keine Playlists gefunden !','','','','',''))
				self.keyLocked = True
			else:
				#self.filmliste.sort(key=lambda t : t[0].lower())
				menu_len = len(self.filmliste)
				print "Playlists found: ",menu_len
				self.keyLocked = False

		elif self.channelGenre:
			while a < l:
				mg = re.search('<entry gd:etag=(.*?)</entry>', data[a:], re.S)
				if mg:
					a += mg.end()
					m1 = re.search('<summary>(.*?)</summary>', mg.group(1), re.S)
					m2 = re.search('<author>.*?<name>(.*?)</name>.*?<uri>(.*?)</uri>'\
						'.*?<media:thumbnail.*?url=\'(.*?)\'', mg.group(1), re.S)
					if m2:
						title = m2.group(1)
						if m1:
							desc = decodeHtml(m1.group(1))
						else:
							desc = "Keine weiteren Info's vorhanden."
						url = m2.group(2) + "/uploads?"
						img = m2.group(3)

						self.filmliste.append(('', title, url, img, desc, 'C'))
				else:
					a = l

			if len(self.filmliste) == 0:
				print "No channel found!"
				self.pages = 0
				self.filmliste.append(('Keine Channels gefunden !','','','','',''))
				self.keyLocked = True
			else:
				#self.filmliste.sort(key=lambda t : t[0].lower())
				menu_len = len(self.filmliste)
				print "Channels found: ",menu_len
				self.keyLocked = False

		else:
			while a < l:
				mg = re.search('<media:group>(.*?)</media:group>', data[a:], re.S)
				if mg:
					a += mg.end()
					m1 = re.search('description type=\'plain\'>(.*?)</', mg.group(1), re.S)
					if m1:
						desc = decodeHtml(m1.group(1))
						desc = urllib.unquote(desc)
					else:
						desc = "Keine weiteren Info's vorhanden."

					m2 = re.search('<media:player url=.*?/watch\?v=(.*?)&amp;feature=youtube_gdata_player.*?'\
						'<media:thumbnail url=\'(.*?)\'.*?<media:title type=\'plain\'>(.*?)</.*?<yt:duration seconds=\'(.*?)\'', mg.group(1), re.S)
					if m2:
						vid = m2.group(1)
						img = m2.group(2)
						dura = int(m2.group(4))
						vtim = str(datetime.timedelta(seconds=dura))
						title = decodeHtml(m2.group(3))
						self.filmliste.append((vtim+' ', title, vid, img, desc, ''))
				else:
					a = l

			if len(self.filmliste) == 0:
				print "No video found!"
				self.pages = 0
				self.filmliste.append(('Keine Videos gefunden !','','','','',''))
				self.keyLocked = True
			else:
				#self.filmliste.sort(key=lambda t : t[0].lower())
				menu_len = len(self.filmliste)
				print "Videos found: ",menu_len
				self.keyLocked = False

		self.chooseMenuList.setList(map(YT_ListEntry, self.filmliste))
		self.showInfos()

	def dataError(self, error):
		print "dataError: ",error
		self['handlung'].setText("Lesefehler !\n"+str(error))

	def showInfos(self):
		self['page'].setText("%d / %d" % (self.page,self.pages))
		stvTitle = self['liste'].getCurrent()[0][1]
		stvImage = self['liste'].getCurrent()[0][3]
		desc = self['liste'].getCurrent()[0][4]
		print "Img: ",stvImage
		self['name'].setText(stvTitle)
		self['handlung'].setText(desc)
		CoverHelper(self['coverArt']).getCover(stvImage)

	def youtubeErr(self, error):
		print "youtubeErr: ",error
		self['handlung'].setText("Das Video kann leider nicht abgespielt werden !\n"+str(error))

	def setVideoPrio(self):
		self.videoPrio = int(config.mediaportal.youtubeprio.value)
		self['vPrio'].setText(self.videoPrioS[self.videoPrio])

	def delFavo(self):
		print "addFavo:"

		i = self['liste'].getSelectedIndex()
		c = j = 0
		l = len(self.filmliste)
		print l
		try:
			f1 = open(self.favo_path, 'w')
			while j < l:
				if j != i:
					c += 1
					dura = self.filmliste[j][0]
					dhTitle = self.filmliste[j][1]
					dhVideoId = self.filmliste[j][2]
					dhImg = self.filmliste[j][3]
					desc = urllib.quote(self.filmliste[j][4])
					gid = self.filmliste[j][5]
					wdat = '<i>%d</i><n>%s</n><v>%s</v><im>%s</im><d>%s</d><g>%s</g><desc>%s</desc>\n' % (c, dhTitle, dhVideoId, dhImg, dura, gid, desc)
					f1.write(wdat)

				j += 1

			f1.close()
			self.getFavos()

		except IOError, e:
			print "Fehler:\n",e
			print "eCode: ",e
			self['handlung'].setText("Fehler !\n"+str(e))
			f1.close()

	def addFavo(self):
		print "addFavo:"

		dura = self['liste'].getCurrent()[0][0]
		dhTitle = self['liste'].getCurrent()[0][1]
		dhVideoId = self['liste'].getCurrent()[0][2]
		dhImg = self['liste'].getCurrent()[0][3]
		gid = self['liste'].getCurrent()[0][5]
		desc = urllib.quote(self['liste'].getCurrent()[0][4])

		try:
			if not fileExists(self.favo_path):
				f1 = open(self.favo_path, 'w')
				f_new = True
			else:
				f_new = False
				f1 = open(self.favo_path, 'a+')

			max_i = 0
			if not f_new:
				data = f1.read()
				m = re.findall('<i>(\d*?)</i>.*?<v>(.*?)</v>', data)
				if m:
					v_found = False
					for (i, v) in m:
						ix = int(i)
						if ix > max_i:
							max_i = ix
						if v == dhVideoId:
							v_found = True
							break

					if v_found:
						f1.close()
						self.session.open(MessageBox, _("Favorit schon vorhanden"), MessageBox.TYPE_INFO, timeout=5)
						return

			wdat = '<i>%d</i><n>%s</n><v>%s</v><im>%s</im><d>%s</d><g>%s</g><desc>%s</desc>\n' % (max_i + 1, dhTitle, dhVideoId, dhImg, dura, gid, desc)
			f1.write(wdat)
			f1.close()
			self.session.open(MessageBox, _("Favorit hinzugefügt"), MessageBox.TYPE_INFO, timeout=5)

		except IOError, e:
			print "Fehler:\n",e
			print "eCode: ",e
			self['handlung'].setText("Fehler !\n"+str(e))
			f1.close()

	def getFavos(self):
		print "getFavos:"

		self.filmliste = []
		try:
			if not fileExists(self.favo_path):
				f_new = True
			else:
				f_new = False
				f1 = open(self.favo_path, 'r')

			if not f_new:
				data = f1.read()
				f1.close()
				m = re.findall('<n>(.*?)</n><v>(.*?)</v><im>(.*?)</im><d>(.*?)</d><g>(.*?)</g><desc>(.*?)</desc>', data)
				if m:
					for (n, v, img, dura, gid, desc) in m:
						self.filmliste.append((dura, n, v, img, urllib.unquote(desc), gid))

			if len(self.filmliste) == 0:
				print "No video found!"
				self.pages = self.page = 0
				self.filmliste.append(('Keine Videos gefunden !','','','','',''))
				self.keyLocked = True
				if not f_new and len(data) > 0:
					os.remove(self.favo_path)

			else:
				self.pages = self.page = 1
				self.keyLocked = False

			self.chooseMenuList.setList(map(YT_ListEntry, self.filmliste))
			self.showInfos()

		except IOError, e:
			print "Fehler:\n",e
			print "eCode: ",e
			self['handlung'].setText("Fehler !\n"+str(e))
			f1.close()

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
		i = self['liste'].getSelectedIndex()
		if not i:
			self.keyPageDownFast()

		self['liste'].up()
		self.showInfos()

	def keyDown(self):
		if self.keyLocked:
			return
		i = self['liste'].getSelectedIndex()
		l = len(self.filmliste) - 1
		#print "i, l: ",i,l
		if l == i:
			self.keyPageUpFast()

		self['liste'].down()
		self.showInfos()

	def keyTxtPageUp(self):
		if self.keyLocked:
			return
		if self.favoGenre:
			self.delFavo()
		else:
			self['handlung'].pageUp()

	def keyTxtPageDown(self):
		if self.keyLocked:
			return
		self['handlung'].pageDown()

	def keyPageUpFast(self,step=1):
		if self.keyLocked:
			return
		#print "keyPageUp: "
		oldpage = self.page
		if (self.page + step) <= self.pages:
			self.page += step
			self.start_idx += self.max_res * step
		else:
			self.page = 1
			self.start_idx = 1
		#print "Page %d/%d" % (self.page,self.pages)
		if oldpage != self.page:
			self.loadPageData()

	def keyPageDownFast(self,step=1):
		if self.keyLocked:
			return
		print "keyPageDown: "
		oldpage = self.page
		if (self.page - step) >= 1:
			self.page -= step
			self.start_idx -= self.max_res * step
		else:
			self.page = self.pages
			self.start_idx = self.max_res * (self.pages - 1) + 1
		#print "Page %d/%d" % (self.page,self.pages)
		if oldpage != self.page:
			self.loadPageData()

	def keyYellow(self):
		self.setVideoPrio()

	def key_1(self):
		#print "keyPageDownFast(2)"
		self.keyPageDownFast(2)

	def keyGreen(self):
		if self.keyLocked:
			return
		if self.favoGenre:
			return

		#if not (self.playlistGenre or self.channelGenre):
		self.addFavo()

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

	def keyOK(self):
		if self.keyLocked:
			return

		gid = self['liste'].getCurrent()[0][5]
		if gid == 'P' or gid == 'C':
			dhTitle = 'Videos: ' + self['liste'].getCurrent()[0][1]
			genreurl = re.sub('v=2', '', self['liste'].getCurrent()[0][2])
			if self.favoGenre:
				self.session.openWithCallback(self.getFavos, YT_ListScreen, genreurl, dhTitle)
			else:
				self.session.open(YT_ListScreen, genreurl, dhTitle)
		else:
			self.session.openWithCallback(
			self.setVideoPrio,
				YoutubePlayer,
				self.filmliste,
				self['liste'].getSelectedIndex(),
				playAll = True,
				listTitle = self.genreName,
				plType='local',
				title_inr=1
				)

	def keyCancel(self):
		self.close()