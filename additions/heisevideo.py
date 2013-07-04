#	-*-	coding:	utf-8	-*-

from ast import literal_eval
from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.simpleplayer import SimplePlayer, SimplePlaylist
from Plugins.Extensions.MediaPortal.resources.simpleplayer import SimplePlayer

HTV_Version = "heiseVIDEO v0.90"

HTV_siteEncoding = 'utf-8'

def heiseTvGenreListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 20, 0, 860, 25, 0, RT_HALIGN_CENTER | RT_VALIGN_CENTER, entry[1])
		] 
		
class HeiseTvGenreScreen(Screen):
	
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
		
		self["actions"]  = ActionMap(["OkCancelActions", "ShortcutActions", "WizardActions", "ColorActions", "SetupActions", "NumberActions", "MenuActions"], {
			"ok"    : self.keyOK,
			"cancel": self.keyCancel
		}, -1)
		
		
		self['title'] = Label(HTV_Version)
		self['ContentTitle'] = Label("M e n ü")
		self['name'] = Label("")
		self['F1'] = Label("")
		self['F2'] = Label("")
		self['F3'] = Label("")
		self['F4'] = Label("")
		
		self.keyLocked = True
		self.data_rubrikid="2523"
		self.baseUrl = 'http://www.heise.de'
		self.genreliste = []
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['genreList'] = self.chooseMenuList
		
		self.onLayoutFinish.append(self.layoutFinished)
		
	def layoutFinished(self):
		self.genreliste.append((0, 'Bitte warten...', ''))
		self.chooseMenuList.setList(map(heiseTvGenreListEntry, self.genreliste))
		getPage(self.baseUrl+'/video', headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.buildMenu).addErrback(self.dataError)

	def buildMenu(self, data):
		self.genreliste = []
		self.genreliste.append((1, 'Neue Videos', '/video'))
		
		m = re.findall('<section class="kasten video.*?<h3><span></span>(.*?)</h3>', data, re.S)
		if m:
			for x in m:
				self.genreliste.append((3, x, '/video'))
					
		m = re.search('<section id="cttv_archiv">(.*?)</section>', data, re.S)
		if m:
			list = re.findall('data-jahr="(.*?)"', m.group(1), re.S)
			if list:
				for j in list:
					url = '/video/includes/cttv_archiv_json.pl?jahr=%s&rubrik=%s' % (j, self.data_rubrikid)
					self.genreliste.append((2, "c't-TV Archiv %s" % j, url))
				
		self.chooseMenuList.setList(map(heiseTvGenreListEntry, self.genreliste))
		self.keyLocked = False
	
	def dataError(self, failure):
		print "dataError: ", failure
	
	def keyOK(self):
		if self.keyLocked:
			return
			
		genreID = self['genreList'].getCurrent()[0][0]
		genre = self['genreList'].getCurrent()[0][1]
		stvLink = self['genreList'].getCurrent()[0][2]
		self.session.open(HeiseTvListScreen, self.baseUrl, genreID, stvLink, genre)

	def keyCancel(self):
		self.close()

def heiseTvListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 20, 0, 860, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry[0])
		] 
		
class HeiseTvListScreen(Screen):
	
	def __init__(self, session, baseUrl, genreID, stvLink, stvGenre):
		self.session = session
		self.genreID = genreID
		self.stvLink = stvLink
		self.genreName = stvGenre
		self.baseUrl = baseUrl
		
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
			"yellow"	: self.keyYellow,
			"right" : self.keyRight,
			"left" : self.keyLeft
		}, -1)

		self['title'] = Label(HTV_Version)
		self['ContentTitle'] = Label(self.genreName)
		self['name'] = Label("")
		self['handlung'] = ScrollLabel("")
		self['coverArt'] = Pixmap()
		self['page'] = Label("")
		self['F1'] = Label("Text-")
		self['F2'] = Label("")
		self['F3'] = Label("VidPrio")
		self['F4'] = Label("Text+")
		self['Page'] = Label("")
		self['VideoPrio'] = Label("VideoPrio")
		self['vPrio'] = Label("")
		
		
		self.videoPrio = int(config.mediaportal.youtubeprio.value) - 1
		self.videoPrioS = ['L','M','H']
		self.setVideoPrio()
		self.keyLocked = True
		self.filmliste = []
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['liste'] = self.chooseMenuList
		
		self.onLayoutFinish.append(self.layoutFinished)
		
	def layoutFinished(self):
		self.filmliste.append(('Bitte warten...','','',''))
		self.chooseMenuList.setList(map(heiseTvListEntry, self.filmliste))
		url = self.baseUrl+self.stvLink
		print "getPage: ", url
		getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.genreData).addErrback(self.dataError)
	
	def genreData(self, data):
		print "genreData:"
		self.filmliste = []
		if self.genreID == 1:
			stvDaten = re.findall('class="rahmen">.*?<img src="(.*?)".*?<h3><a href="(.*?)">(.*?)</a>.*?<p>(.*?)<a href="', data, re.S)
			if stvDaten:
				print "Videos found"
				for (img,href,title,desc) in stvDaten:
					title = decodeHtml(title)
					title = title.strip()
					self.filmliste.append((title,href,img,desc))
					
		elif self.genreID == 2:
			infos = literal_eval(data)
			try:
				for i in range(len(infos)):
					title = infos[i]['titel'].strip()
					title = decodeHtml(title)
					self.filmliste.append((title,infos[i]['url'],infos[i]['anrissbild']['src'],infos[i]['anrisstext']))
			except KeyError, e:
				print 'Video infos key error: ', e
			else:
				print "Videos found"
			
		elif self.genreID == 3:
			patt = '<section class="kasten video.*?<h3><span></span>%s</h3>(.*?)</section>' % self.genreName
			m = re.search(patt, data, re.S)
			if m:
				print m.group(1)
				stvDaten = re.findall('<img.*?src="(.*?)".*?<h4><a href="(.*?)">(.*?)</a></h4>', m.group(1), re.S)
				if stvDaten:
					print "Videos found"
					for (img,href,title) in stvDaten:
						title = decodeHtml(title)
						title = title.strip()
						self.filmliste.append((title,href,img,''))
		else:
			print "Wrong genre"

		if len(self.filmliste) == 0:
			self.filmliste.append(('Keine Videos gefunden !','','',''))
			self.chooseMenuList.setList(map(heiseTvListEntry, self.filmliste))
		else:
			self.keyLocked = False
			self.chooseMenuList.setList(map(heiseTvListEntry, self.filmliste))
			self.showInfos()
			
		
	def dataError(self, error):
		print "dataError: ",error

	def showInfos(self):
		stvTitle = self['liste'].getCurrent()[0][0]
		stvImage = self.baseUrl + self['liste'].getCurrent()[0][2]
		desc = self['liste'].getCurrent()[0][3]
		print stvImage
		self['name'].setText(stvTitle)
		self['handlung'].setText(desc)
		if stvImage:
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
	
	def getVid(self, data):
		print "getVid:"
		try:
			m = re.search('json_url: "(.*?)&callback=', data)
			url = m.group(1)
		except AttributeError, e:
			print "AttributeError: ", e
		else:
			print "getPage: ", url
			getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.getVidInfos).addErrback(self.dataError)
			
	def getVidInfos(self, data):
		print "getVidInfos:"
		try:
			infos = literal_eval(data)
			if self.videoPrio == 2:
				url = infos['url']
			elif self.videoPrio == 1:
				url = infos['formats']['mp4']['360']['url']
			else:
				url = infos['formats']['mp4']['270']['url']
				
			#title = infos['title']
		except KeyError, e:
			print "KeyError: ", e
			self.session.open(MessageBox, _("Fehler in Video URL"), MessageBox.TYPE_INFO, timeout=5)
		else:
			title = self['liste'].getCurrent()[0][0]
			#sref = eServiceReference(0x1001, 0, url)
			#sref.setName(title)
			#self.session.open(MoviePlayer, sref)
			self.session.open(HeiseTvPlayer, [(title, url, '')])
			
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
		
	def setVideoPrio(self):
		if self.videoPrio+1 > 2:
			self.videoPrio = 0
		else:
			self.videoPrio += 1
		self['vPrio'].setText(self.videoPrioS[self.videoPrio])
		
	def keyYellow(self):
		self.setVideoPrio()
		
	def keyOK(self):
		print "keyOK:"
		if self.keyLocked:
			return
		url = self.baseUrl + self['liste'].getCurrent()[0][1]
		print "getPage: ", url
		getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.getVid).addErrback(self.dataError)
			
	def keyCancel(self):
		self.close()

class HeiseTvPlayer(SimplePlayer):

	def __init__(self, session, playList, showCover=False):
		print "HeiseTvPlayer:"

		SimplePlayer.__init__(self, session, playList, showPlaylist=False, ltype='heisetv', cover=showCover)

	def getVideo(self):
		title = self.playList[self.playIdx][0]
		url = self.playList[self.playIdx][1]
		iurl = self.playList[self.playIdx][2]
		self.playStream(title, url, imgurl=iurl)		