from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.simpleplayer import SimplePlayer

def retrotvListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 50, 0, 800, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry[0])
		]

class retrotvFilmListeScreen(Screen):

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
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft,
			"nextBouquet" : self.keyPageUp,
			"prevBouquet" : self.keyPageDown,
			"green" : self.keyPageNumber
		}, -1)

		self.keyLocked = True
		self.page = 1
		self.lastpage = 1
		self['title'] = Label("retro-tv.de")
		self['ContentTitle'] = Label("Episoden")
		self['name'] = Label("Film Auswahl")
		self['F1'] = Label("Exit")
		self['F2'] = Label("Page")
		self['F3'] = Label("")
		self['F4'] = Label("")
		self['F3'].hide()
		self['F4'].hide()
		self['coverArt'] = Pixmap()
		self['Page'] = Label("Page")
		self['page'] = Label("")
		self['handlung'] = Label("")

		self.filmliste = []
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['liste'] = self.chooseMenuList

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.keyLocked = True
		self['name'].setText('Bitte warten...')
		url = "http://www.retro-tv.de/archiv:%s" % str(self.page)
		print url
		getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.loadPageData).addErrback(self.dataError)

	def loadPageData(self, data):
		lastpparse = re.search("Gehe zu Seite:(.*?)</div>", data, re.S)
		lastp = re.findall('.*[\/|>](\d+)[\/|<]', lastpparse.group(1), re.S)
		if lastp:
			self.lastpage = int(lastp[-1])
		else:
			self.lastpage = 1
		self['page'].setText("%d/%d" % (self.page,self.lastpage))
		movies = re.findall('title="(Folge.*?)".*?href="(.*?)"><img\ssrc=".*?".*?<img\ssrc=".*?videos%2F(.*?)".*?td_description', data, re.S)
		if movies:
			self.filmliste = []
			for (title,url,image) in movies:
				image = 'http://www.retro-tv.de/image_resizer.php?width=320&height=240&image=gfx%2Fvideos%2F' + image
				url = 'http://www.retro-tv.de/' + url
				self.filmliste.append((decodeHtml(title),url,image))
			self.chooseMenuList.setList(map(retrotvListEntry, self.filmliste))
			self.chooseMenuList.moveToIndex(0)
			self.keyLocked = False
			self.loadPic()

	def dataError(self, error):
		print "dataError:"
		printl(error,self,"E")

	def loadPic(self):
		streamTitle = self['liste'].getCurrent()[0][0]
		streamUrl = self['liste'].getCurrent()[0][1]
		streamPic = self['liste'].getCurrent()[0][2]
		self['name'].setText(streamTitle)
		downloadPage(streamPic, "/tmp/Icon.jpg").addCallback(self.ShowCover)
		getPage(streamUrl, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.getDescription).addErrback(self.dataError)

	def getDescription(self, data):
		ddDescription = re.search('name="description"\scontent=".*?Heute:\s{0,2}(.*?)"', data, re.S)
		if ddDescription:
			self['handlung'].setText(decodeHtml(ddDescription.group(1)))
		else:
			self['handlung'].setText("Keine Infos gefunden.")

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

	def keyPageNumber(self):
		self.session.openWithCallback(self.callbackkeyPageNumber, VirtualKeyBoard, title = (_("Seitennummer eingeben")), text = str(self.page))

	def callbackkeyPageNumber(self, answer):
		if answer is not None:
			answer = re.findall('\d+', answer)
		else:
			return
		if answer:
			if int(answer[0]) < self.lastpage + 1:
				self.page = int(answer[0])
				self.loadPage()
			else:
				self.page = self.lastpage
				self.loadPage()

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

	def keyOK(self):
		if self.keyLocked:
			return
		streamLink = self['liste'].getCurrent()[0][1]
		if streamLink == None:
			return
		url = streamLink
		getPage(streamLink, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.getlink).addErrback(self.dataError)

	def getlink(self, data):
		parse = re.findall('file:\s"(.*?)"', data, re.S)		
		if parse:
			stream_url = 'http://infernsehen.de/xmoov.php?file=' + parse[-1] + '&start=0'
			title = self['liste'].getCurrent()[0][0]
			self.session.open(retrotvPlayer, [(title, stream_url)])

	def keyCancel(self):
		self.close()

class retrotvPlayer(SimplePlayer):

	def __init__(self, session, playList):
		print "retrotvPlayer:"
		SimplePlayer.__init__(self, session, playList, showPlaylist=False)

	def getVideo(self):
		title = self.playList[self.playIdx][0]
		url = self.playList[self.playIdx][1]
		self.playStream(title, url)