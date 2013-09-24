from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.simpleplayer import SimplePlayer
from Plugins.Extensions.MediaPortal.resources.coverhelper import CoverHelper

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
		self['F2'].hide()
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
		parse = re.search('FormatGruppe:\sABC(.*?)</div>', data, re.S)
		ganze = re.findall('<a\shref="(/myspass/shows/.*?)"\sclass="showsAZName">(.*?)</a>', parse.group(1), re.S)
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
		self['ContentTitle'] = Label("Staffeln:")
		self['name'] = Label("")
		self['F1'] = Label("Exit")
		self['F2'] = Label("")
		self['F3'] = Label("")
		self['F4'] = Label("")
		self['F2'].hide()
		self['F3'].hide()
		self['F4'].hide()

		self.staffelliste = []
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['genreList'] = self.chooseMenuList

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		print "hole daten"
		getPage(self.myspassUrl, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.loadPageData).addErrback(self.dataError)

	def loadPageData(self, data):
		parse = re.search('\/\sGanze\sFolgen.*?class="episodeListSeasonList(.*?)</ul>', data, re.S)
		staffeln = re.findall('data-maxpages="(.*?)".*?data-query="(.*?season=.*?)">.*?\);">.\t{0,5}\s{0,15}(.*?)</a></span>', parse.group(1), re.S)
		if staffeln:
			self.staffelliste = []
			for (pages, link, name) in staffeln:
				link = "http://www.myspass.de/myspass/includes/php/ajax.php?v=2&ajax=true&action=%s&pageNumber=" % (link.replace('&amp;','&'))
				self.staffelliste.append((decodeHtml(name), link, pages))
			self.chooseMenuList.setList(map(myspassListEntry, self.staffelliste))
			self.keyLocked = False

	def keyOK(self):
		if self.keyLocked:
			return
		myname = self['genreList'].getCurrent()[0][0]
		myid = self['genreList'].getCurrent()[0][1]
		mypages = self['genreList'].getCurrent()[0][2]

		print myid, myname, mypages
		self.session.open(myspassFolgenListeScreen, myname, myid, mypages)

	def dataError(self, error):
		printl(error,self,"E")

	def keyCancel(self):
		self.close()

class myspassFolgenListeScreen(Screen):

	def __init__(self, session, myspassName, myspassUrl, myspassPages):
		self.session = session
		self.myspassName = myspassName
		self.myspassUrl = myspassUrl
		self.myspassPages = myspassPages

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
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft,
			"nextBouquet" : self.keyPageUp,
			"prevBouquet" : self.keyPageDown,
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
		self['F2'].hide()
		self['F3'].hide()
		self['F4'].hide()
		self['handlung'] = Label("")
		self['page'] = Label("")
		self['Page'] = Label("Page")
		self['coverArt'] = Pixmap()
		self.page = 0
		self.lastpage = 0

		self.folgenliste = []
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['liste'] = self.chooseMenuList

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		print "hole daten"
		self.folgenliste = []
		url = "%s%s" % (self.myspassUrl, str(self.page))
		getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.loadPageData).addErrback(self.dataError)

	def loadPageData(self, data):
		self.lastpage = int(self.myspassPages)
		self['page'].setText(str(self.page+1) + ' / ' + str(self.lastpage+1))
		folgen = re.findall('class="episodeListInformation">.*?location.href=.*?--\/(.*?)\/.*?img\ssrc="(.*?)"\salt="(.*?)".*?\/h5>.*?"spacer5"></div>(.*?)<div', data, re.S|re.I)
		if folgen:
			for (id, image, title, description) in folgen:
				link = "http://www.myspass.de/myspass/includes/apps/video/getvideometadataxml.php?id=%s" % (id)
				image = "http://www.myspass.de" + image
				description = description.replace('\t','').replace('\n','')
				self.folgenliste.append((decodeHtml(title), link, image, description))
			self.chooseMenuList.setList(map(myspassListEntry, self.folgenliste))
			self.keyLocked = False
			self.loadPic()
		
	def loadPic(self):
		streamTitle = self['liste'].getCurrent()[0][0]
		streamPic = self['liste'].getCurrent()[0][2]
		streamHandlung = self['liste'].getCurrent()[0][3]
		self['name'].setText(streamTitle)
		self['handlung'].setText(streamHandlung)
		CoverHelper(self['coverArt']).getCover(streamPic)

	def keyOK(self):
		if self.keyLocked:
			return
		self.myname = self['liste'].getCurrent()[0][0]
		self.mylink = self['liste'].getCurrent()[0][1]
		print self.myname, self.mylink
		getPage(self.mylink , headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.get_link).addErrback(self.dataError)

	def get_link(self, data):
		stream_url = re.search('<url_flv><.*?CDATA\[(.*?)\]\]></url_flv>', data, re.S)
		if stream_url:
			print stream_url.group(1)
			self.session.open(SimplePlayer, [(self.myname, stream_url.group(1))], showPlaylist=False, ltype='myspass')

	def dataError(self, error):
		printl(error,self,"E")

	def keyPageDown(self):
		print "PageDown"
		if self.keyLocked:
			return
		if not self.page < 1:
			self.page -= 1
			self.loadPage()

	def keyPageUp(self):
		print "PageUP"
		if self.keyLocked:
			return
		if self.page < self.lastpage:
			self.page += 1
			self.loadPage()

	def keyLeft(self):
		if self.keyLocked:
			return
		self['liste'].pageUp()
		self.loadPic()

	def keyRight(self):
		if self.keyLocked:
			return
		self['liste'].pageDown()
		self.loadPic()

	def keyUp(self):
		if self.keyLocked:
			return
		self['liste'].up()
		self.loadPic()

	def keyDown(self):
		if self.keyLocked:
			return
		self['liste'].down()
		self.loadPic()

	def keyCancel(self):
		self.close()