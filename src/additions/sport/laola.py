from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.simpleplayer import SimplePlayer

def laolaOverviewListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 0, 0, 800, 25, 0, RT_HALIGN_CENTER | RT_VALIGN_CENTER, entry[1])
		]

def laolaSubOverviewListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 0, 0, 800, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry[0])
		]

class laolaVideosOverviewScreen(Screen):

	def __init__(self, session):
		print 'laolaVideosOverviewScreen'
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

		self.lastservice = session.nav.getCurrentlyPlayingServiceReference()
		self.playing = False
		self.keyLocked = True
		self['title'] = Label("Laola1.tv")
		self['ContentTitle'] = Label("")
		self['name'] = Label("")
		self['F1'] = Label("Exit")
		self['F2'] = Label("Land")
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
		self.genreliste.append(("Live", "http://www.laola1.tv/de-de/calendar/0.html"))
		self.chooseMenuList.setList(map(laolaSubOverviewListEntry, self.genreliste))
		self.keyLocked = False

	def keyOK(self):
		if self.keyLocked:
			return
			
		auswahl = self['genreList'].getCurrent()[0][0]
		link = self['genreList'].getCurrent()[0][1]
		print auswahl, link
		self.session.open(laolaLiveScreen, auswahl, link)

	def keyCancel(self):
		self.close()

	def dataError(self, error):
		printl(error,self,"E")

class laolaLiveScreen(Screen):

	def __init__(self, session, name, link):
		print 'laolaLiveScreen'
		self.session = session
		self.lname = name
		self.llink = link

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

		self.lastservice = session.nav.getCurrentlyPlayingServiceReference()
		self.playing = False
		self.keyLocked = True
		self['title'] = Label("Laola1.tv - Live")
		self['ContentTitle'] = Label("")
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
		print self.llink
		getPage(self.llink, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.getLiveData).addErrback(self.dataError)
		
	def getLiveData(self, data):
		live = re.findall('<img width="80" height="45" src=".*?">.*?<a href="(.*?)"><h2>.*?<span class="ititle">Sportart:</span><span class="idesc half">(.*?)</span>.*?<span class="ititle">Liga:</span><span class="idesc half">(.*?)</span>.*?<span class="ititle full">Streamstart:</span><span class="idesc full">(.*?)</span>.*?<span class="ititle full">Verf&uuml;gbar in:</span><span class="idesc full"><span style="color:#0A0;">(.*?)<', data, re.S)
		if live:
			for url,sportart,welche,time,where in live:
				print url,sportart,welche,time,where
				title = "%s - %s-%s" % (time, sportart, welche)
				self.genreliste.append((title, url))
			
			self.chooseMenuList.setList(map(laolaSubOverviewListEntry, self.genreliste))
			self.keyLocked = False

	def keyOK(self):
		if self.keyLocked:
			return
			
		self.auswahl = self['genreList'].getCurrent()[0][0]
		url = self['genreList'].getCurrent()[0][1]
		print self.auswahl, url
		
		response=self.getUrl(url)
		if 'Dieser Stream beginnt' in response:
			message = self.session.open(MessageBox, _("Event ist noch nicht gestartet."), MessageBox.TYPE_INFO, timeout=3)
		else:
			match_player=re.compile('<iframe.+?src="(.+?)"', re.DOTALL).findall(response)

			response=self.getUrl(match_player[0])
			match_m3u8=re.compile('url: "(.+?)"', re.DOTALL).findall(response)

			response=self.getUrl(match_m3u8[0].replace('/vod/','/live/'))
			match_url=re.compile('url="(.+?)"', re.DOTALL).findall(response)
			match_auth=re.compile('auth="(.+?)"', re.DOTALL).findall(response)
			res_url=match_url[0].replace('l-_a-','l-L1TV_a-l1tv')
			m3u8_url = res_url+'?hdnea='+match_auth[0]

			response=self.getUrl(m3u8_url)
			match_sec_m3u8=re.compile('#EXT-X-STREAM-INF:(.+?)http(.+?)rebase=on', re.DOTALL).findall(response)
			
			stream_url = "http%s" % match_sec_m3u8[-1][1]
			print stream_url
			self.session.open(SimplePlayer, [(self.auswahl, stream_url)], showPlaylist=False, ltype='laola1')

	def getUrl(self, url):
		req = urllib2.Request(url)
		req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
		response = urllib2.urlopen(req)
		link=response.read()
		response.close()
		return link
	
	def keyCancel(self):
		self.close()

	def dataError(self, error):
		printl(error,self,"E")