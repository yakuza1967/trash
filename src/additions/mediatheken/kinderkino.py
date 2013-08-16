from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.simpleplayer import SimplePlayer
from Plugins.Extensions.MediaPortal.resources.playrtmpmovie import PlayRtmpMovie
from Plugins.Extensions.MediaPortal.resources.coverhelper import CoverHelper

def kinderKinoListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 20, 0, 900, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry[0])
		]

class kinderKinoScreen(Screen):

	def __init__(self, session):
		self.session = session
		path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/%s/kinderKinoScreen.xml" % config.mediaportal.skin.value
		if not fileExists(path):
			path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/original/kinderKinoScreen.xml"
		print path
		with open(path, "r") as f:
			self.skin = f.read()
			f.close()

		Screen.__init__(self, session)

		self["actions"]  = ActionMap(["OkCancelActions", "ShortcutActions", "WizardActions", "ColorActions", "SetupActions", "NumberActions", "MenuActions", "EPGSelectActions"], {
			"ok"    : self.keyOK,
			"cancel": self.keyCancel,
			"up"    : self.keyUp,
			"down"  : self.keyDown,
			"left"  : self.keyLeft,
			"right" : self.keyRight,
			"nextBouquet" : self.keyPageUp,
			"prevBouquet" : self.keyPageDown
		}, -1)

		self.keyLocked = True
		self.page = 1
		self['title'] = Label("KinderKino.de")
		self['Pic'] = Pixmap()
		self['name'] = Label("")
		self['page'] = Label("1")
		self.kkListe = []
		self.maxPages = ''
		self.loadPageNo = 1
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['List'] = self.chooseMenuList
		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.keyLocked = True
		url = "http://kostenlos-dyn.kinderkino.de/api/get_category_posts/?id=3&page=%s&count=50&order_by=date&thumbnail_size=full&include=title,slug,thumbnail,content,categories,custom_fields,comments&custom_fields=Streaming,FSK,Jahr,IMDb-Bewertung,Stars,mobileCover,Highlight,Highlight-Bottom,Regisseur,Wikipedia,IMDb-Link,IPTV,Video,Youtube,Duration"  % (self.loadPageNo)
		getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.parsePageData).addErrback(self.dataError)

	def parsePageData(self, data):
		self.kkListe = []
		# In json Format laden
		json_data = json.loads(data)
		# Gesamtanzahl der Seiten
		self.maxPages = json_data['pages']
		# Alle Videos extrahieren
		kkVideos = json_data['posts']
		# Alle Filmtitel einer Seite
		for kkVideo in kkVideos:
			kkTitle = str(kkVideo['title']).replace('&#8211;', '-')
			kkLinkPart = kkVideo['custom_fields']['Streaming']
			kkPic = str(kkVideo['thumbnail'])
			self.kkListe.append((kkTitle,kkLinkPart[0],kkPic))
		self.chooseMenuList.setList(map(kinderKinoListEntry, self.kkListe))
		self.keyLocked = False
		self.showPic()

	def dataError(self, error):
		printl(error,self,"E")

	def showPic(self):
		kkTitle = self['List'].getCurrent()[0][0]
		kkPicLink = self['List'].getCurrent()[0][2]
		self['name'].setText(kkTitle)
		self['page'].setText(str(self.page))
		CoverHelper(self['Pic']).getCover(kkPicLink)

	def keyPageDown(self):
		print "PageDown"
		if self.keyLocked:
			return
		if not self.page < 2:
			self.page -= 1
			self.loadPageNo = self.page
			self.loadPage()

	def keyPageUp(self):
		print "PageUP"
		if self.keyLocked:
			return
		if not self.page > self.maxPages:
			self.page += 1
			self.loadPageNo = self.page
			self.loadPage()

	def keyLeft(self):
		if self.keyLocked:
			return
		self['List'].pageUp()
		self.showPic()

	def keyRight(self):
		if self.keyLocked:
			return
		self['List'].pageDown()
		self.showPic()

	def keyUp(self):
		if self.keyLocked:
			return
		self['List'].up()
		self.showPic()

	def keyDown(self):
		if self.keyLocked:
			return
		self['List'].down()
		self.showPic()

	def keyOK(self):
		if self.keyLocked:
			return
		kkTitle = str(self['List'].getCurrent()[0][0])
		kkUrlPart = str(self['List'].getCurrent()[0][1])
		if config.mediaportal.useRtmpDump.value:
			kkRtmpLink = "rtmp://fms.edge.newmedia.nacamar.net/loadtv_vod/' --playpath=mp4:kinderkino-kostenlos/%s --app=loadtv_vod/ --pageUrl=http://kostenlos.kinderkino.de/ --swfUrl=http://kinderkinokostenlos-www.azurewebsites.net/asset'" % (kkUrlPart)
			movieinfo = [kkRtmpLink,kkTitle]
			self.session.open(PlayRtmpMovie, movieinfo, kkTitle)
		else:
			kkRtmpLink = "rtmp://fms.edge.newmedia.nacamar.net/loadtv_vod/' playpath=mp4:kinderkino-kostenlos/%s pageUrl=http://kostenlos.kinderkino.de/ swfUrl=http://kinderkinokostenlos-www.azurewebsites.net/asset'" % (kkUrlPart)
			self.session.open(SimplePlayer, [(kkTitle, kkRtmpLink)], showPlaylist=False, ltype='kinderkino')

	def keyCancel(self):
		self.close()