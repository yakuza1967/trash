from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.simpleplayer import SimplePlayer, SimplePlaylistIO
from Components.FileList import FileList

def simplelistGenreListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 50, 0, 800, 25, 0, RT_HALIGN_CENTER | RT_VALIGN_CENTER, entry[0])
		]

def simplelistListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 50, 0, 800, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry[0])
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
		self['name'] = Label("")
		self['F1'] = Label("Exit")
		self['F2'] = Label("FileList")
		self['F3'] = Label("GlobalList")
		self['F4'] = Label("Löschen")
		self['F4'].hide()

		self.filelist = []
		self.ltype = ''
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['genreList'] = self.chooseMenuList

		self.onLayoutFinish.append(self.globalList)

	def loadFileList(self):
		self.ltype = 'sl_movies'
		self['F4'].hide()
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
	
	def globalList(self):
		self.ltype = 'sl_glob_playlist'
		self['ContentTitle'].setText("Global Playlist")

		self.filelist = SimplePlaylistIO.getPL('mp_global_pl_01')
		if self.filelist == []:
			self.keyLocked = True
			self['F4'].hide()
			self.filelist.append(("Keine globale Playlist gefunden.", "dump"))
		else:
			self['F4'].show()
			self.chooseMenuList.setList(map(simplelistListEntry, self.filelist))
			self.keyLocked = False

	def deleteEntry(self):
		if self.ltype != 'sl_glob_playlist' or not len(self.filelist):
			return
		idx = self['genreList'].getSelectedIndex()
		SimplePlaylistIO.delEntry('mp_global_pl_01', self.filelist, idx)
		self.chooseMenuList.setList(map(simplelistListEntry, self.filelist))
		
	def keyOK(self):
		if self.keyLocked:
			return
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

	def keyCancel(self):
		self.close()
