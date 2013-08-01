from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.simpleplayer import SimplePlayer
from Plugins.Extensions.MediaPortal.resources.coverhelper import CoverHelper

def wissenGenreListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 50, 0, 800, 25, 0, RT_HALIGN_CENTER | RT_VALIGN_CENTER, entry[0])
		]

def wissenListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 50, 0, 800, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry[0])
		]

class wissenListeScreen(Screen):

	def __init__(self, session):
		self.session = session

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
			"red": self.keyCancel,
			"up": self.keyUp,
			"down": self.keyDown,
			"right": self.keyRight,
			"left": self.keyLeft,
			"nextBouquet" : self.keyPageUp,
			"prevBouquet" : self.keyPageDown
		}, -1)

		self.keyLocked = True
		self['title'] = Label("Wissen.de")
		self['ContentTitle'] = Label("Videos:")
		self['name'] = Label("")
		self['F1'] = Label("Exit")
		self['F2'] = Label("")
		self['F3'] = Label("")
		self['F4'] = Label("")
		self['F3'].hide()
		self['F4'].hide()
		self['handlung'] = Label("")
		self['page'] = Label("")
		self['Page'] = Label("Page")
		self['coverArt'] = Pixmap()

		self.videoliste = []
		self.page = 0
		self.lastpage = 0

		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['liste'] = self.chooseMenuList

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.keyLocked = True
		self.videoliste = []
		url = "http://www.wissen.de/medien-videos/all?page=%s" % str(self.page)
		getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.loadPageData).addErrback(self.dataError)

	def loadPageData(self, data):
		lastlast = re.search('class="pager-last\slast".*?all\?page=(.*?)"', data, re.S)
		currentlast = re.search('pager-current\slast">(.*?)</li>', data, re.S)
		if lastlast:
			lastp = int(lastlast.group(1))
		else:
			lastp = int(currentlast.group(1))-1
		if lastp:
			lastp = lastp
			print str(lastp)
			self.lastpage = lastp
		else:
			self.lastpage = 0
		self['page'].setText(str(self.page+1) + ' / ' + str(self.lastpage+1))

		videos = re.findall('<a\shref="(/video/.*?)">.*?background-image..url\(\'(.*?)\'.*?<p\sclass="teaser-h2">(.*?)</p>', data, re.S)
		if videos:
			for (url, img, title) in videos:
				url = "http://www.wissen.de%s" % url
				self.videoliste.append((decodeHtml(title), url, img))
			self.chooseMenuList.setList(map(wissenListEntry, self.videoliste))
			self.loadPic()
			self.keyLocked = False

	def loadPic(self):
		streamPic = self['liste'].getCurrent()[0][2]
		CoverHelper(self['coverArt']).getCover(streamPic)

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

	def keyOK(self):
		if self.keyLocked:
			return
		self.wissentitle = self['liste'].getCurrent()[0][0]
		url = self['liste'].getCurrent()[0][1]
		print self.wissentitle, url

		getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.get_js_link).addErrback(self.dataError)

	def get_js_link(self, data):
		js_link = re.findall('<script\stype="text/javascript"\ssrc="(http://edge-cdn.net/videojs_.*?)"></script>', data, re.S)
		if js_link:
			getPage(js_link[0], headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.get_xml).addErrback(self.dataError)

	def get_xml(self, data):
		xml_link = re.findall('"config_url",".*?,(.*?)"', data, re.S)
		if xml_link:
			url = urllib.unquote(xml_link[0])
			getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.read_xml).addErrback(self.dataError)

	def read_xml(self, data):
		streams = re.findall('<name\stype="string">(.*?)</name>.*?<url_hd\stype="string">(.*?)<', data, re.S)
		if streams:
			stream_url = streams[0][1]
			print stream_url
			self.session.open(SimplePlayer, [(self.wissentitle, stream_url)], showPlaylist=False, ltype='wissen')

	def dataError(self, error):
		printl(error,self,"E")

	def keyCancel(self):
		self.close()