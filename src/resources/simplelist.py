from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.simpleplayer import SimplePlayer, SimplePlaylistIO
from Components.FileList import FileList
if fileExists('/usr/lib/enigma2/python/Plugins/Extensions/SerienFilm/MovieSelection.pyo'):
	from Plugins.Extensions.SerienFilm.MovieSelection import MovieSelection
else:
	from Screens.MovieSelection import MovieSelection

def simplelistListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 50, 0, 830, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry[0])
		]

class simplelistGenreScreen(Screen):

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
			"menu": self.keyMenu,
			"red": self.keyCancel,
			"green": self.loadFileList,
			"yellow": self.globalList,
			"blue": self.deleteEntry
		}, -1)

		#hole mediainfo download path
		if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/mediainfo/plugin.pyo"):
			self.filelist_path = config.plugins.mediainfo.savetopath.value
			print "Lade Mediainfo download path."
		else:
			self.filelist_path = "/media/hdd/movie/"
			print "Kein Mediainfo installiert."

		self.keyLocked = True
		self['title'] = Label("SimpleList")
		self['ContentTitle'] = Label("%s" % self.filelist_path)
		self['name'] = Label("Auswahl:")
		self['F1'] = Label("Exit")
		self['F2'] = Label("FileList")
		self['F3'] = Label("GlobalList")
		self['F4'] = Label("Löschen")
		self['F4'].hide()

		self.last_pl_number = config.mediaportal.sp_pl_number.value
		self.last_videodir = config.movielist.last_videodir.value
		config.movielist.last_videodir.value = self.filelist_path
		self.last_selection = None
		self.filelist = []
		self.ltype = ''
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['genreList'] = self.chooseMenuList

		self.onClose.append(self._onClose)
		self.onFirstExecBegin.append(self.globalList)

	def loadFileList(self):
		self.ltype = 'sl_movies'
		self['F4'].hide()
		self.session.openWithCallback(self.getSelection, MovieSelection, selectedmovie=self.last_selection)
		"""
		self['ContentTitle'].setText("%s" % self.filelist_path)
		self.filelist_raw = FileList(self.filelist_path, matchingPattern = "(?i)^.*\.(mp2|mp3|ogg|ts|wav|wave|m3u|pls|e2pls|mpg|vob|avi|divx|m4v|mkv|mp4|m4a|dat|flac|mov|m2ts|flv|dts|3gp|3g2|mts)", useServiceRef = True, additionalExtensions = "4098:m3u 4098:e2pls 4098:pls").getFileList()
		self.filelist = []
		if len(self.filelist_raw) != 0:
			for file in self.filelist_raw:
				# check ob file oder dir.
				if not file[0][1]:
					title = file[1][7]
					sref_play = "/media/hdd/movie/%s" % title
					self.filelist.append((decodeHtml(title), sref_play))

		if len(self.filelist) != 0:
			self.keyLocked = False
		else:
			self.keyLocked = True
			self.filelist.append(("Keine Movieliste gefunden.", "dump"))
		self.chooseMenuList.setList(map(simplelistListEntry, self.filelist))
		"""

	def getSelection(self, current):
		print "getSelection:",current
		if not current:
			self.globalList()
		else:
			self.last_selection = current
			url = current.getPath()
			fn = current.getName()
			#print fn
			#print url
			self.session.openWithCallback(self.loadFileList, SimplePlayer, [(fn, url)], showPlaylist=False, ltype=self.ltype)

	def globalList(self):
		self.ltype = 'sl_glob_playlist'
		self['ContentTitle'].setText("Global Playlist-%02d" % config.mediaportal.sp_pl_number.value)
		self['F4'].show()
		self.filelist == []
		self.filelist = SimplePlaylistIO.getPL('mp_global_pl_%02d' % config.mediaportal.sp_pl_number.value)
		if self.filelist == []:
			self.keyLocked = True
			self['F4'].hide()
			self.filelist.append(("Keine Einträge gefunden.", "dump"))
		else:
			self['F4'].show()
			self.keyLocked = False
		self.chooseMenuList.setList(map(simplelistListEntry, self.filelist))

	def deleteEntry(self):
		if self.ltype != 'sl_glob_playlist' or not len(self.filelist):
			return
		idx = self['genreList'].getSelectedIndex()
		SimplePlaylistIO.delEntry('mp_global_pl_%02d' % config.mediaportal.sp_pl_number.value, self.filelist, idx)
		self.chooseMenuList.setList(map(simplelistListEntry, self.filelist))

	def keyMenu(self):
		self.session.openWithCallback(self.cb_Menu, SimplelistConfig)

	def cb_Menu(self):
		print "cb_menu:",config.mediaportal.sp_pl_number.value
		if config.mediaportal.sp_pl_number.value != self.last_pl_number and self.ltype == 'sl_glob_playlist':
			self.last_pl_number = config.mediaportal.sp_pl_number.value
			self.globalList()

	def keyOK(self):
		if self.keyLocked:
			return
		"""
		if self.ltype == 'sl_movies':
			title = self['genreList'].getCurrent()[0][0]
			sref_play = self['genreList'].getCurrent()[0][1]
			print title, sref_play
			if title.endswith('.ts'):
				t = title.split(' - ')
				if len(t) > 2:
					title = sep = ''
					for x in range(2, len(t)):
						title += sep + t[x]
						sep = ' - '
					title = title.split('.ts')[0]

			self.session.open(SimplePlayer, [(title, sref_play)], showPlaylist=False, ltype=self.ltype)
		else:
			idx = self['genreList'].getSelectedIndex()
			self.session.open(SimplePlayer, [], playIdx=idx, playList2=self.filelist, plType='global', ltype=self.ltype, playAll=True)
		"""
		idx = self['genreList'].getSelectedIndex()
		self.session.open(SimplePlayer, [], playIdx=idx, playList2=self.filelist, plType='global', ltype=self.ltype, playAll=True)

	def _onClose(self):
		config.movielist.last_videodir.value = self.last_videodir

	def keyCancel(self):
		self.close()

class SimplelistConfig(ConfigListScreen, Screen):
	skin = '\n\t\t<screen position="center,center" size="500,300" title="MP SimpleList Konfiguration">\n\t\t\t<widget name="config" position="10,10" size="480,290" scrollbarMode="showOnDemand" />\n\t\t</screen>'

	def __init__(self, session):
		Screen.__init__(self, session)
		self.session = session
		self.list = []
		self.list.append(getConfigListEntry('Glob. playlist number', config.mediaportal.sp_pl_number))
		ConfigListScreen.__init__(self, self.list)
		self['setupActions'] = ActionMap(['SetupActions'],
		{
			'ok': 		self.keySave,
			'cancel': 	self.keyCancel
		},-2)

