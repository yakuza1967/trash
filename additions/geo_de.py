#	-*-	coding:	utf-8	-*-

from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.simpleplayer import SimplePlayer, SimplePlaylist

STV_Version = "GEO.de v0.91"

STV_siteEncoding = 'utf-8'

def GEOdeListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 20, 0, 860, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry[0] + entry[1])
		] 
		
class GEOdeGenreScreen(Screen):
	
	def __init__(self, session):
		self.session = session
		
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
			"ok" : self.keyOK,
			"cancel" : self.keyCancel,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft
		}, -1)

		self['title'] = Label(STV_Version)
		self['ContentTitle'] = Label("GEOaudio - Hören und Reisen")
		self['name'] = Label("")
		self['handlung'] = ScrollLabel("")
		self['page'] = Label("")
		self['F1'] = Label("Text-")
		self['F2'] = Label("")
		self['F3'] = Label("")
		self['F4'] = Label("Text+")
		self['VideoPrio'] = Label("")
		self['vPrio'] = Label("")
		self['Page'] = Label("Page")
		self['coverArt'] = Pixmap()
		
		self.keyLocked = True
		self.baseUrl = "http://www.geo.de"
		
		self.filmliste = []
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['liste'] = self.chooseMenuList
		
		self.onLayoutFinish.append(self.layoutFinished)
		
	def layoutFinished(self):
		self.keyLocked = True
		stvLink = self.baseUrl + '/GEO/reisen/podcast/reise-podcast-geoaudio-hoeren-und-reisen-5095.html'
		print "getPage: ",stvLink
		getPage(stvLink, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.genreData).addErrback(self.dataError)
	
	def genreData(self, data):
		print "genreData:"
		stvDaten = re.findall('id:"(.*?)".*?name:"(.*?)".*?mp3:"(.*?)".*?iption:"(.*?)".*?poster: "(.*?)"', data, re.S)
		if stvDaten:
			print "Podcasts found"
			for (id, name, mp3, desc, img) in stvDaten:
				self.filmliste.append(("%s. " % id, iso8859_Decode(name), mp3, iso8859_Decode(desc),img))
			self.keyLocked = False
		else:
			self.filmliste.append(('Keine Podcasts gefunden !','','','',''))
		
		self.chooseMenuList.setList(map(GEOdeListEntry, self.filmliste))
		self.showInfos()
	
	def dataError(self, error):
		print "dataError: ",error

	def showInfos(self):
		stvTitle = self['liste'].getCurrent()[0][1]
		stvImage = self['liste'].getCurrent()[0][4]
		stvDesc = self['liste'].getCurrent()[0][3]
		print stvImage
		self['name'].setText(stvTitle)
		self['handlung'].setText(stvDesc)
		if stvImage != '':
			downloadPage(stvImage, "/tmp/Icon.jpg").addCallback(self.ShowCover)
		
	def ShowCover(self, picData):
		if fileExists("/tmp/Icon.jpg"):
			self['coverArt'].instance.setPixmap(gPixmapPtr())
			self.scale = AVSwitch().getFramebufferScale()
			self.picload = ePicLoad()
			size = self['coverArt'].instance.size()
			self.picload.setPara((size.width(), size.height(), self.scale[0], self.scale[1], False, 1, "#FF000000"))
			if self.picload.startDecode("/tmp/Icon.jpg", 0, 0, False) == 0:
				ptr = self.picload.getData()
				if ptr != None:
					self['coverArt'].instance.setPixmap(ptr)
					self['coverArt'].show()
					del self.picload
	
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
		self['liste'].up()
		self.showInfos()
		
	def keyDown(self):
		if self.keyLocked:
			return
		self['liste'].down()
		self.showInfos()
		
	def keyOK(self):
		if self.keyLocked:
			return
		self.session.open(
			GEOdePlayer,
			self.filmliste,
			playIdx = self['liste'].getSelectedIndex()
			)
			
	def keyCancel(self):
		self.close()
		
class GEOdePlayer(SimplePlayer):

	def __init__(self, session, playList, playIdx):
		print "GEOdePlayer:"

		SimplePlayer.__init__(self, session, playList, playIdx=playIdx, playAll=True, listTitle="GEOaudio - Hören und Reisen", autoScrSaver=True, ltype='geo.de')
		
	def getVideo(self):
		stvLink = self.playList[self.playIdx][2]
		stvTitle = "%s%s" % (self.playList[self.playIdx][0], self.playList[self.playIdx][1])
		self.playStream(stvTitle, stvLink)

	def openPlaylist(self):
		self.session.openWithCallback(self.cb_Playlist, GEOdePlaylist, self.playList, self.playIdx, listTitle=self.listTitle)
		
class GEOdePlaylist(SimplePlaylist):

	def __init__(self, session, playList, playIdx, listTitle=None):

		SimplePlaylist.__init__(self, session, playList, playIdx, listTitle=listTitle)
		
	def playListEntry(self, entry):
		return [entry,
			(eListboxPythonMultiContent.TYPE_TEXT, 20, 0, 860, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry[0]+entry[1])
			]	 
