from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.yt_url import *
from Plugins.Extensions.MediaPortal.resources.simpleplayer import SimplePlayer

def auswahlListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 20, 0, 900, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry[0])
		]

class dokuScreen(Screen):

	def __init__(self, session):
		self.session = session
		path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/%s/dokuScreen.xml" % config.mediaportal.skin.value
		if not fileExists(path):
			path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/original/dokuScreen.xml"
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
			"left" : self.keyLeft,
			"yellow" : self.keyVideoQuality
		}, -1)

		self['name'] = Label("Doku.me")
		self['title'] = Label("Dokumentation Auswahl")
		self['coverArt'] = Pixmap()
		self.keyLocked = False
		self.videoPrio = int(config.mediaportal.youtubeprio.value)
		self.videoPrioS = ['Low','Medium', 'High']
		self['name'].setText('Doku.me (Video Quality: ' + self.videoPrioS[self.videoPrio] + ')')

		self.filmliste = []

		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['genreList'] = self.chooseMenuList

		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.keyLocked = True
		url = "http://doku.me/liste-aller-dokumentationen"
		getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.allData).addErrback(self.dataError)

	def keyVideoQuality(self):
		if self.videoPrio+1 > 2:
			self.videoPrio = 0
		else:
			self.videoPrio += 1
		self['name'].setText('Doku.me (Video Quality: ' + self.videoPrioS[self.videoPrio] + ')')

	def allData(self, data):
		dkAZ = re.findall('<li><a\shref="(http://doku.me/.*?)"\s{0,2}><span\sclass="head">(.*?)</span></a></li>', data)
		if dkAZ:
			for (dkUrl,dkTitle) in dkAZ:
				if not re.match('.*?(\[|"|\(|/|//|///)', dkTitle[0]):
					self.filmliste.append((dkTitle, dkUrl))
			self.chooseMenuList.setList(map(auswahlListEntry, self.filmliste))
			self.chooseMenuList.moveToIndex(0)
			self.keyLocked = False

	def dataError(self, error):
		printl(error,self,"E")

	def keyLeft(self):
		if self.keyLocked:
			return
		self['genreList'].pageUp()

	def keyRight(self):
		if self.keyLocked:
			return
		self['genreList'].pageDown()

	def keyUp(self):
		if self.keyLocked:
			return
		self['genreList'].up()

	def keyDown(self):
		if self.keyLocked:
			return
		self['genreList'].down()

	def keyOK(self):
		if self.keyLocked:
			return
		dkLink = self['genreList'].getCurrent()[0][1]
		print dkLink
		getPage(dkLink, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.getVideoPage).addErrback(self.dataError)

	def getVideoPage(self, data):
		videoPage = re.findall('"http://www.youtube.com/(v|embed)/(.*?)"', data, re.S)
		if videoPage:
			print videoPage
			url = youtubeUrl(self.session).getVideoUrl(videoPage[0][1].replace('?rel=0',''), self.videoPrio)
			if url:
				self.play(url)
		else:
			message = self.session.open(MessageBox, _("Dieses Video ist nicht verfuegbar."), MessageBox.TYPE_INFO, timeout=5)
		self.keyLocked = False

	def play(self,file):
		xxxtitle = self['genreList'].getCurrent()[0][0]
		self.session.open(SimplePlayer, [(xxxtitle, file)], showPlaylist=False, ltype='dokume')

	def keyCancel(self):
		self.close()