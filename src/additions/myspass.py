from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.simpleplayer import SimplePlayer

def myspassGenreListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 50, 0, 800, 25, 0, RT_HALIGN_CENTER | RT_VALIGN_CENTER, entry[0])
		]

def myspassListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 50, 0, 800, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry[0])
		]

class myspassGenreScreen(Screen):

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

		self.keyLocked = True
		self['title'] = Label("MySpass.de")
		self['ContentTitle'] = Label("Sendungen A-Z:")
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
		url = "http://www.myspass.de/myspass/ganze-folgen/"
		getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.loadPageData).addErrback(self.dataError)

	def loadPageData(self, data):
		ganze = re.findall('<div class="showsAZName"><a href="(/myspass/shows/.*?)".*?>(.*?)</a></div>', data, re.S)
		if ganze:
			self.genreliste = []
			for (link, name) in ganze:
				link = "http://www.myspass.de%s" % link
				print name, link
				self.genreliste.append((decodeHtml(name), link))		
			self.chooseMenuList.setList(map(myspassListEntry, self.genreliste))
			self.keyLocked = False		

	def dataError(self, error):
		printl(error,self,"E")
		
	def keyOK(self):
		if self.keyLocked:
			return
		myspassName = self['genreList'].getCurrent()[0][0]
		myspassUrl = self['genreList'].getCurrent()[0][1]
		print myspassName, myspassUrl
		self.session.open(myspassStaffelListeScreen, myspassName, myspassUrl)

	def keyCancel(self):
		self.close()

class myspassStaffelListeScreen(Screen):

	def __init__(self, session, myspassName, myspassUrl):
		self.session = session
		self.myspassName = myspassName
		self.myspassUrl = myspassUrl

		self.plugin_path = mp_globals.pluginPath
		self.skin_path =  mp_globals.pluginPath + "/skins"

		path = "%s/%s/defaultListWideScreen.xml" % (self.skin_path, config.mediaportal.skin.value)
		if not fileExists(path):
			path = self.skin_path + "/original/defaultListWideScreen.xml"

		with open(path, "r") as f:
			self.skin = f.read()
			f.close()

		Screen.__init__(self, session)

		self["actions"]  = ActionMap(["OkCancelActions", "ShortcutActions", "WizardActions", "ColorActions", "SetupActions", "NumberActions", "MenuActions", "EPGSelectActions"], {
			"ok"    : self.keyOK,
			"cancel": self.keyCancel,
			"red": self.keyCancel
		}, -1)

		self.keyLocked = True
		self['title'] = Label("MySpass.de")
		self['ContentTitle'] = Label("Staffeln:")
		self['name'] = Label("")
		self['F1'] = Label("Exit")
		self['F2'] = Label("")
		self['F3'] = Label("")
		self['F4'] = Label("")
		self['F3'].hide()
		self['F4'].hide()
		self['handlung'] = Label("")
		self['page'] = Label("")
		self['Page'] = Label("")
		self['coverArt'] = Pixmap()

		self.staffelliste = []
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['liste'] = self.chooseMenuList

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		print "hole daten"
		getPage(self.myspassUrl, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.loadPageData).addErrback(self.dataError)

	def loadPageData(self, data):
		staffeln = re.findall('<li.*?><a.*?href="#seasonlist_full_episode.*?" onclick="ajax.*?(getEpisodeListFromSeason.*?)\'.*?>(.*?)</a></li>', data)
		if staffeln:
			self.staffelliste = []
			for (link, name) in staffeln:
				link = "http://www.myspass.de/myspass/includes/php/ajax.php?action=%s" % (link.replace('&amp;','&'))
				self.staffelliste.append((decodeHtml(name), link))		
			self.chooseMenuList.setList(map(myspassListEntry, self.staffelliste))
			self.keyLocked = False		

	def keyOK(self):
		if self.keyLocked:
			return
		myname = self['liste'].getCurrent()[0][0]
		myid = self['liste'].getCurrent()[0][1]

		print myid, myname
		self.session.open(myspassFolgenListeScreen, myname, myid)

	def dataError(self, error):
		printl(error,self,"E")

	def keyCancel(self):
		self.close()
		
class myspassFolgenListeScreen(Screen):

	def __init__(self, session, myspassName, myspassUrl):
		self.session = session
		self.myspassName = myspassName
		self.myspassUrl = myspassUrl

		self.plugin_path = mp_globals.pluginPath
		self.skin_path =  mp_globals.pluginPath + "/skins"

		path = "%s/%s/defaultListWideScreen.xml" % (self.skin_path, config.mediaportal.skin.value)
		if not fileExists(path):
			path = self.skin_path + "/original/defaultListWideScreen.xml"

		with open(path, "r") as f:
			self.skin = f.read()
			f.close()

		Screen.__init__(self, session)

		self["actions"]  = ActionMap(["OkCancelActions", "ShortcutActions", "WizardActions", "ColorActions", "SetupActions", "NumberActions", "MenuActions", "EPGSelectActions"], {
			"ok"    : self.keyOK,
			"cancel": self.keyCancel,
			"red": self.keyCancel
		}, -1)

		self.keyLocked = True
		self['title'] = Label("MySpass.de")
		self['ContentTitle'] = Label("Folgen:")
		self['name'] = Label("")
		self['F1'] = Label("Exit")
		self['F2'] = Label("")
		self['F3'] = Label("")
		self['F4'] = Label("")
		self['F3'].hide()
		self['F4'].hide()
		self['handlung'] = Label("")
		self['page'] = Label("")
		self['Page'] = Label("")
		self['coverArt'] = Pixmap()

		self.folgenliste = []
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['liste'] = self.chooseMenuList

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		print "hole daten"
		getPage(self.myspassUrl, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.loadPageData).addErrback(self.dataError)

	def loadPageData(self, data):
		folgen = re.findall('<a href="/myspass/shows/.*?/.*?/.*?/(.*?)/".*?;">(.*?)<', data)
		if folgen:
			self.folgenliste
			for (id, name) in folgen:
				link = "http://www.myspass.de/myspass/includes/apps/video/getvideometadataxml.php?id=%s" % (id)
				self.folgenliste.append((decodeHtml(name), link))		
			self.chooseMenuList.setList(map(myspassListEntry, self.folgenliste))
			self.keyLocked = False		

	def keyOK(self):
		if self.keyLocked:
			return
		self.myname = self['liste'].getCurrent()[0][0]
		self.mylink = self['liste'].getCurrent()[0][1]
		print self.myname, self.mylink 
		getPage(self.mylink , headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.get_link).addErrback(self.dataError)

	def get_link(self, data):
		stream_url = re.findall('<url_flv><.*?CDATA\[(.*?)\]\]></url_flv>', data, re.S)
		if stream_url:
			print stream_url[0]
			self.session.open(SimplePlayer, [(self.myname, stream_url[0])], showPlaylist=False, ltype='myspass')

	def dataError(self, error):
		printl(error,self,"E")

	def keyCancel(self):
		self.close()