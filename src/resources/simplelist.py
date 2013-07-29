from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.simpleplayer import SimplePlayer
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
			"yellow": self.globalList
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
		self['F4'] = Label("")
		self['F4'].hide()
			
		self.filelist = []
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['genreList'] = self.chooseMenuList

		self.onLayoutFinish.append(self.loadFileList)

	def loadFileList(self):
		self['ContentTitle'].setText("%s" % self.filelist_path)
		self.filelist_raw = FileList(self.filelist_path, matchingPattern = "(?i)^.*\.(mp2|mp3|ogg|ts|wav|wave|m3u|pls|e2pls|mpg|vob|avi|divx|m4v|mkv|mp4|m4a|dat|flac|mov|m2ts|flv|dts|3gp|3g2|mts)", useServiceRef = True, additionalExtensions = "4098:m3u 4098:e2pls 4098:pls").getFileList()
		if len(self.filelist_raw) != 0:
			self.filelist = []
			for file in self.filelist_raw:
				# check ob file oder dir.
				if not file[0][1]:
					title = file[1][7]
					sref_play = "/media/hdd/movie/%s" % title
					self.filelist.append((decodeHtml(title), sref_play))
					
			if len(self.filelist) != 0:
				self.chooseMenuList.setList(map(simplelistListEntry, self.filelist))
				self.keyLocked = False
				
	def globalList(self):
		self['ContentTitle'].setText("Global Playlist")
		if fileExists("/etc/enigma2/mp_global_pl_01"):
			self.filelist = []
			self.filelist = self.readGlobalFile()
			if len(self.filelist) != 0:
				self.chooseMenuList.setList(map(simplelistListEntry, self.filelist))
				self.keyLocked = False
		else:
			self.filelist = []
			self.filelist.append((decodeHtml("Keine Globale Simpleplayer List gefunden."), "dump"))
			self.chooseMenuList.setList(map(simplelistListEntry, self.filelist))

			
	def readGlobalFile(self):
		read = open("/etc/enigma2/mp_global_pl_01", "r")
		slist = []
		for rawData in read.readlines():
			data = re.findall('<title>(.*?)</<url>(.*?)</', rawData, re.S)
			(title, stream_url) = data[0]
			slist.append((title, stream_url))
		return slist
	
	def keyOK(self):
		if self.keyLocked:
			return
		title = self['genreList'].getCurrent()[0][0]
		sref_play = self['genreList'].getCurrent()[0][1]
		print title, sref_play
		
		self.session.open(SimplePlayer, [(title, sref_play)], showPlaylist=False, ltype='simplelist')

	def keyCancel(self):
		self.close()
		