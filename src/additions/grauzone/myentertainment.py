#	-*-	coding:	utf-8	-*-
from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.simpleplayer import SimplePlayer
from Plugins.Extensions.MediaPortal.resources.coverhelper import CoverHelper
from Plugins.Extensions.MediaPortal.resources.yt_url import *
from urllib import quote, urlencode
import md5

# Check ob MediaPortal installiert ist
if fileExists('/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/plugin.pyo'):
	from Plugins.Extensions.MediaPortal.resources.simpleplayer import SimplePlayer
	MediaPortalPresent = True
else:
	MediaPortalPresent = False
	
config.entertain = ConfigSubsection()
config.entertain.userName = ConfigText(default="USERNAME", fixed_size=False)
config.entertain.userPass = ConfigText(default="PASSWORD", fixed_size=False)
	
std_headers = {
	'User-Agent': 'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.2.6) Gecko/20100627 Firefox/3.6.6',
	'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
	'Accept-Language': 'en-us,en;q=0.5',
}

ck = {}

def meListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 50, 0, 800, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry[0])
		]
		
def meGenreEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 0, 0, 800, 25, 0, RT_HALIGN_CENTER | RT_VALIGN_CENTER, entry[0])
		]

class showMEHDGenre(Screen):

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
		self['title'] = Label("my-entertainment (10gbps) - Premium Only")
		self['ContentTitle'] = Label("Try Login..")
		self['name'] = Label("")
		self['F1'] = Label("Exit")
		self['F2'] = Label("")
		self['F3'] = Label("")
		self['F4'] = Label("")
		self['F3'].hide()
		self['F4'].hide()
		
		# load username and pass
		
		self.username = config.entertain.userName.value
		self.password = config.entertain.userPass.value
		self.loginOK = False
		
		self.genreliste = []
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['genreList'] = self.chooseMenuList

		#self.onLayoutFinish.append(self.login)
		self.onFirstExecBegin.append(self.login)
		
	def login(self):
		print "Login:", self.username, self.password
		
		if self.username == "USERNAME" and self.password == "PASSWORD":
			self.session.open(meSetupScreen)
		else:		
			self.loginUrl = 'http://10gbps.org/forum/login.php?do=login'
			loginData = {'vb_login_username': self.username, 'vb_login_password': self.password, 'do': 'login'}
			getPage(self.loginUrl, method='POST', 
					postdata=urlencode(loginData), cookies=ck,
					headers={'Content-Type':'application/x-www-form-urlencoded','User-agent': 'Mozilla/4.0', 'Referer': 'http://www.hellboundhackers.org/index.php', }).addCallback(self.loginRefresh).addErrback(self.dataError)

	def loginRefresh(self, data):
		if "Danke" in str(data):
			self.loginOK = True
			cookieuser = '1'
			password_md5 = md5.md5(self.password).hexdigest()
		
			loginData = {'vb_login_username': self.username,
						 's': '',
						 'securitytoken': 'guest',
						 'do': 'login',
						 'vb_login_md5password': password_md5,
						 'vb_login_md5password_utf': password_md5,
						 'cookieuser' : cookieuser
						 }

			getPage(self.loginUrl, method="POST",
					postdata=urlencode(loginData), headers={'Content-Type': 'application/x-www-form-urlencoded'},
					followRedirect=True, timeout=30, cookies=ck).addCallback(self.loginDone).addErrback(self.dataError)
		else:
			self['ContentTitle'].setText("Login fehlgeschlagen !")

	def accountInfos(self, data):
		statusUrl = 'http://10gbps.org/forum/payments.php'
		getPage(statusUrl, method="GET",
				headers={'Content-Type': 'application/x-www-form-urlencoded'},
				followRedirect=True, timeout=30, cookies=ck).addCallback(self.accountInfosData).addErrback(self.dataError)	
			
	def accountInfosData(self, data):
		print "hole infos.."
		infos = re.findall('<dt>Startdatum</dt>.*?<dd>(.*?)</dd>.*?<dt>L.*?t aus am</dt>.*?<dd>(.*?)</dd>.*?<p class="description">(.*?)</p>', data, re.S)
		if infos:
			print infos
			(reg, bis, was) = infos[0]
			acci = "Benutzer: %s - %s: Registriert: %s -> %s" % (self.username, was, reg, bis)
			print acci
			self['ContentTitle'].setText(str(acci))
	
	def loginDone(self, data):

		getPage(self.loginUrl, method="GET",
				headers={'Content-Type': 'application/x-www-form-urlencoded'},
				followRedirect=True, timeout=30, cookies=ck).addCallback(self.accountInfos).addErrback(self.dataError)
					
		self.genreListe = []
		self.genreListe.append(("Suche", "suche"))
		#self.genreListe.append(("Sortiert nach IMDB-Bewertung", "imdb"))
		self.genreListe.append(("Neueinsteiger", "http://10gbps.org/forum/content.php?r=1969-Aktuelle-HD-Filme&page="))
		self.genreListe.append(("Aktuelle Filme", "http://10gbps.org/forum/list.php?r=category/169-Cineline&page="))
		self.genreListe.append(("3D-Charts", "http://10gbps.org/forum/content.php?r=5440-3d-charts&page="))
		self.genreListe.append(("3D", "http://10gbps.org/forum/content.php?r=4225-3d-filme&page="))
		self.genreListe.append(("HD-Charts", "http://10gbps.org/forum/content.php?r=1989-HD-Charts&page="))
		#self.genreListe.append(("HD-Serien", "http://10gbps.org/forum/content.php?r=5993-Serien&page="))
		self.genreListe.append(("Alle HD Premium Streams", "http://10gbps.org/forum/content.php?r=1669-hd-filme&page="))
		self.genreListe.append(("Abenteuer", "http://10gbps.org/forum/list.php?r=category/65-HD-Abenteuer&page="))
		self.genreListe.append(("Action", "http://10gbps.org/forum/list.php?r=category/35-HD-Action&page="))
		self.genreListe.append(("Biografie", "http://10gbps.org/forum/list.php?r=category/70-HD-Biografie&page="))
		self.genreListe.append(("Collection", "http://10gbps.org/forum/content.php?r=3501-hd-collection&page="))
		self.genreListe.append(("Doku", "http://10gbps.org/forum/list.php?r=category/64-HD-Doku&page="))
		self.genreListe.append(("Drama", "http://10gbps.org/forum/list.php?r=category/36-HD-Drama&page="))
		self.genreListe.append(("Fantasy", "http://10gbps.org/forum/list.php?r=category/37-HD-Fantasy&page="))
		self.genreListe.append(("Horror", "http://10gbps.org/forum/list.php?r=category/38-HD-Horror&page="))
		self.genreListe.append(("Komoedie", "http://10gbps.org/forum/list.php?r=category/39-HD-Kom%F6die&page="))
		self.genreListe.append(("Kriegsfilm", "http://10gbps.org/forum/list.php?r=category/66-HD-Kriegsfilm&page="))		
		self.genreListe.append(("Krimi", "http://10gbps.org/forum/list.php?r=category/56-HD-Krimi&page="))
		self.genreListe.append(("Mystery", "http://10gbps.org/forum/list.php?r=category/62-HD-Mystery&page="))
		self.genreListe.append(("Romanze", "http://10gbps.org/forum/list.php?r=category/40-HD-Romanze&page="))
		self.genreListe.append(("SciFi", "http://10gbps.org/forum/list.php?r=category/41-HD-SciFi&page="))
		self.genreListe.append(("Thriller", "http://10gbps.org/forum/list.php?r=category/42-HD-Thriller&page="))
		self.genreListe.append(("Zeichentrick", "http://10gbps.org/forum/list.php?r=category/43-HD-Zeichentrick&page="))
		self.genreListe.append(("Setup", "dump"))
		self.chooseMenuList.setList(map(meGenreEntry, self.genreListe))
		self.keyLocked = False

	def keyOK(self):
		if not self.keyLocked:
			enterAuswahlLabel = self['genreList'].getCurrent()[0][0]
			enterAuswahlLink = self['genreList'].getCurrent()[0][1]
			
			print "Select:", enterAuswahlLabel, enterAuswahlLink
			
			if enterAuswahlLabel == "Setup":
				self.session.open(meSetupScreen)
			#	print 'suche...', enterAuswahlLink
				#self.session.openWithCallback(self.mySearch, VirtualKeyBoard, title = (_("Suche.....")), text = self.searchTxt)
			#elif enterAuswahlLink == "imdb":
			#	print 'imdb....'
			#	self.session.open(enterImdbListScreen, self.opener)
			else:
				self.session.open(meMovieScreen, enterAuswahlLink, enterAuswahlLabel)
		
	def dataError(self, error):
		print error

	def keyCancel(self):
		self.close()
		
class meMovieScreen(Screen):

	def __init__(self, session, enterAuswahlLink, enterAuswahlLabel):
		self.session = session
		self.enterAuswahlLink = enterAuswahlLink
		self.enterAuswahlLabel = enterAuswahlLabel

		self.plugin_path = mp_globals.pluginPath
		self.skin_path =  mp_globals.pluginPath + "/skins"

		path = "%s/%s/m4kdefaultPageListeScreen.xml" % (self.skin_path, config.mediaportal.skin.value)
		if not fileExists(path):
			path = self.skin_path + "/original/m4kdefaultPageListeScreen.xml"

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
			"prevBouquet" : self.keyPageDown
		}, -1)

		self.keyLocked = True
		self['title'] = Label("Filme Auswahl:")
		self['name'] = Label("")
		self['handlung'] = Label("")
		self['page'] = Label("")
		self['coverArt'] = Pixmap()

		self.page = 1
		self.genreListe = []
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['filmList'] = self.chooseMenuList

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		print self.enterAuswahlLink, self.enterAuswahlLabel
		
		self.enterAuswahlLink = self.enterAuswahlLink + str(self.page)
		getPage(self.enterAuswahlLink, cookies=ck, agent=std_headers, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.loadPageData).addErrback(self.dataError)
		
	def loadPageData(self, data):
		self.genreliste = []
		print 'loadPageData', self.enterAuswahlLink
		if self.enterAuswahlLabel == "Aktuell2e Filme":
			print "Aktuelle Filme"
			totalPages = re.findall('<span class="first_last"><a href=".*?page=(.*?)"', data, re.S)
			if totalPages:
				print totalPages
				self['page'].setText("%s / %s" % (self.page, totalPages[0]))
				
			search = re.findall('<h3 class="article_preview">.*?<a href="(.*?)"><span>[AZ:]?(.*?)</span></a>.*?<div class="cms_article_section_location">.*?>IMDB(.*?)</a>.*?<img class="cms_article_preview_image" src="(.*?)" alt="Vorschau"', data,re.S)
			if search:
				for enterLink,enterName,enterImdb,enterPic in search:
					enterTitle = enterName.replace("HD:", "").strip() + ' (IMDB:' + enterImdb + ')' 
					self.genreListe.append((enterTitle, enterLink, enterPic.replace('http://my-entertainment.biz','http://10gbps.org'), enterImdb))
				self.chooseMenuList.setList(map(meListEntry, self.genreListe))
				self.keyLocked = False
				self.loadPic()
				self.loadHandlung()
				self.lastPage = 1
			else:
				print "kacke"
				
		elif self.enterAuswahlLabel == "3D-Charts":
			print "3D Charts"
			search3D = re.findall('<h3 class="article_preview">.*?<a href="(.*?)"><span>[AZ:]?(.*?)</span></a>.*?<div class="cms_article_section_location">.*?>IMDB(.*?)</a>.*?<img class="cms_article_preview_image" src="(.*?)" alt="Vorschau"', data,re.S)
			if search3D:
				for enterLink,enterName,enterImdb,enterPic in search3D:
					enterTitle = enterName.replace("HD:", "").strip() + ' (IMDB:' + enterImdb + ')' 
					self.genreListe.append((enterTitle, enterLink, enterPic.replace('http://my-entertainment.biz','http://10gbps.org')))
				self.chooseMenuList.setList(map(meListEntry, self.genreListe))
				self.keyLocked = False
				self.loadPic()
				self.loadHandlung()
				self.lastPage = 1
				
		elif self.enterAuswahlLabel == "HD-Charts":
			print "HD Charts"
			searchHD = re.findall('<h3 class="article_preview">.*?<a href="(.*?)"><span>[AZ:]?(.*?)</span></a>.*?<div class="cms_article_section_location">.*?>IMDB(.*?)</a>.*?<img class="cms_article_preview_image" src="(.*?)" alt="Vorschau"', data,re.S)
			if searchHD:
				for enterLink,enterName,enterImdb,enterPic in searchHD:
					enterTitle = enterName.replace("HD:", "").strip() + ' (IMDB:' + enterImdb + ')' 
					self.genreListe.append((enterTitle, enterLink, enterPic.replace('http://my-entertainment.biz','http://10gbps.org')))
				self.chooseMenuList.setList(map(meListEntry, self.genreListe))
				self.keyLocked = False
				self.loadPic()
				self.loadHandlung()
				self.lastPage = 1
				
		elif self.enterAuswahlLabel == "3D":
			print "3D"
			self.lastPage = 999
			movies3D = re.findall('<h3 class="article_preview">.*?<a href="(.*?)"><span>[AZ:]?(.*?)</span></a>.*?<div class="cms_article_section_location">.*?>IMDB(.*?)</a>.*?<img class="cms_article_preview_image" src="(.*?)" alt="Vorschau"', data,re.S)
			if movies3D:
				self.genreListe = []
				for enterLink,enterName,enterImdb,enterPic in movies3D:
					enterTitle = enterName.replace("HD:", "").strip() + ' (IMDB:' + enterImdb + ')' 
					self.genreListe.append((enterTitle, enterLink, enterPic.replace('http://my-entertainment.biz','http://10gbps.org')))
				self.chooseMenuList.setList(map(meListEntry, self.genreListe))
				self.keyLocked = False
				self.loadPic()
				self.loadHandlung()
			else:
				self.lastPage = self.page
				
		elif self.enterAuswahlLabel == "Alle HD Premium Streams":
			print "Alle Premium"
			self.lastPage = 999
			movies3D = re.findall('<h3 class="article_preview">.*?<a href="(.*?)"><span>[AZ:]?(.*?)</span></a>.*?<div class="cms_article_section_location">.*?>IMDB(.*?)</a>.*?<img class="cms_article_preview_image" src="(.*?)" alt="Vorschau"', data,re.S)
			if movies3D:
				self.genreListe = []
				for enterLink,enterName,enterImdb,enterPic in movies3D:
					enterTitle = enterName.replace("HD:", "").strip() + ' (IMDB:' + enterImdb + ')' 
					self.genreListe.append((enterTitle, enterLink, enterPic.replace('http://my-entertainment.biz','http://10gbps.org')))
				self.chooseMenuList.setList(map(meListEntry, self.genreListe))
				self.keyLocked = False
				self.loadPic()
				self.loadHandlung()
			else:
				self.lastPage = self.page
				
		elif self.enterAuswahlLabel == "Suche":
			print "suche"
			links = re.findall('<h3 class="searchtitle">.*?<a href="(.*?)".*?title="">(.*?)</a>', data, re.S)
			if links:
				for enterLink, enterName in links:
					self.genreListe.append((enterName, enterLink, ""))
				self.chooseMenuList.setList(map(meListEntry, self.genreListe))
				self.keyLocked = False
			else:
				self['handlung'].setText("Nichts gefunden...")
			
		elif self.enterAuswahlLabel == "HD-Serien":
			print "HD-Serien"
			result = re.findall('<h3 class="article_preview">.*?<a href="(.*?)">.*?<span>[A-Z][A-Z][:](.*?)</span>.*?<img class="cms_article_preview_image" src="(.*?)" alt="Vorschau" />', data, re.S)
			if result:
				for enterLink, enterName, enterPic in result:
					self.genreListe.append((enterName, enterLink, enterPic.replace('http://my-entertainment.biz','http://10gbps.org')))
				self.chooseMenuList.setList(map(meListEntry, self.genreListe))
				self.loadHandlung()
				self.loadPic()
				self.keyLocked = False
			else:
				self['handlung'].setText("Nichts gefunden...")
				
		else:
			print "Sonstige Genres"
			self.lastPage = 999
			totalPages = re.findall('<span class="first_last"><a href=".*?page=(.*?)"', data, re.S)
			if totalPages:
				print totalPages
				self['page'].setText("%s / %s" % (self.page, totalPages[0]))
				
			movies = re.findall('<h3 class="article_preview">.*?<a href="(.*?)"><span>[AZ:]?(.*?)</span></a>.*?<div class="cms_article_section_location">.*?>IMDB(.*?)</a>.*?<img class="cms_article_preview_image" src="(.*?)" alt="Vorschau"', data,re.S)
			if movies:
				self.genreListe = []
				for enterLink,enterName,enterImdb,enterPic in movies:
					enterTitle = enterName.replace("HD:", "").strip() + ' (IMDB:' + enterImdb + ')' 
					self.genreListe.append((enterTitle, enterLink, enterPic.replace('http://my-entertainment.biz','http://10gbps.org')))
				self.chooseMenuList.setList(map(meListEntry, self.genreListe))
				self.keyLocked = False
				self.loadPic()
				self.loadHandlung()
			else:
				self.lastPage = self.page

	def keyOK(self):
		if self.keyLocked:
			return

		streamLink = self['filmList'].getCurrent()[0][1]
		self.streamName = self['filmList'].getCurrent()[0][0]
		
		print self.streamName, streamLink
		
		getPage(streamLink, cookies=ck, agent=std_headers, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.getStream).addErrback(self.dataError)
		
	def getStream(self, data):
		findStream = re.findall('"http://10gbps.org/server/Premium.*?"', data)
		if findStream:
			print "Anzahl der Streams:", len(findStream)
			if len(findStream) == 1:
				print findStream
				getPage(findStream[0].replace('"',''), cookies=ck, agent=std_headers, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.getStreamUrl).addErrback(self.dataError)
				
	def getStreamUrl(self, data):
		print "get Stream Url.."
		stream_url = re.findall('src="(.*?)"', data, re.S)
		if stream_url:
			print stream_url
			self.session.open(SimplePlayer, [(self.streamName, stream_url[0], self.streamPic)], showPlaylist=False, ltype='ME', cover=True)

	def loadPic(self):
		streamName = self['filmList'].getCurrent()[0][0]
		self.streamPic = self['filmList'].getCurrent()[0][2]
		self['name'].setText(self.enterAuswahlLabel)
		CoverHelper(self['coverArt']).getCover(self.streamPic)
		
	def loadHandlung(self):
		streamFilmLink = self['filmList'].getCurrent()[0][1]
		print "loadHandlung...", streamFilmLink
		getPage(streamFilmLink, cookies=ck, agent=std_headers, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.setHandlung).addErrback(self.dataError)
		
	def setHandlung(self, data):
		handlung = re.findall('<div class="bbcode_quote_container"></div>(.*?)<', data, re.S)
		if handlung:
			handlung = re.sub(r"\s+", " ", handlung[0])
			self['handlung'].setText(handlung.strip())
		else:
			self['handlung'].setText("Keine infos gefunden.")

	def keyLeft(self):
		if self.keyLocked:
			return
		self['filmList'].pageUp()
		self.loadPic()
		self.loadHandlung()
		
	def keyRight(self):
		if self.keyLocked:
			return
		self['filmList'].pageDown()
		self.loadPic()
		self.loadHandlung()
		
	def keyUp(self):
		if self.keyLocked:
			return
		self['filmList'].up()
		self.loadPic()
		self.loadHandlung()
		
	def keyDown(self):
		if self.keyLocked:
			return
		self['filmList'].down()
		self.loadPic()
		self.loadHandlung()

	def keyPageDown(self):
		print "PageDown"
		if self.keyLocked:
			return
		if not self.page < 2:
			self.page -= 1
			self.loadPage()
			
	def keyPageUp(self):
		print "PageUp", self.lastPage
		print "selfpage", self.page
		if self.keyLocked:
			return
		if self.page < self.lastPage:
			self.page += 1 
			self.loadPage()
		else:
			return

	def dataError(self, error):
		print error

	def keyCancel(self):
		self.close()

class meSetupScreen(Screen, ConfigListScreen):

	skin = """
		<screen position="center,center" size="450,80" title="Premium Setup">
			<ePixmap position="15,4" size="16,16" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/images/username.png" alphatest="blend" />
			<ePixmap position="15,29" size="16,16" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/images/password.png" alphatest="blend" />
			<widget name="config" position="50,0" size="400,50" scrollbarMode="showOnDemand" />
		</screen>"""		

	def __init__(self, session):
		Screen.__init__(self, session)
		self.session = session
		
		self.list = []
		ConfigListScreen.__init__(self, self.list)
		
		self.list.append(getConfigListEntry("Username:", config.entertain.userName))
		self.list.append(getConfigListEntry("Password:", config.entertain.userPass))

		self["config"].setList(self.list)

		self["setupActions"] = ActionMap(["SetupActions"],
		{
			"ok":		self.saveConfig,
			"cancel":	self.exit
		}, -1)

	def saveConfig(self):
		print "save"
		for x in self["config"].list:
			x[1].save()
		configfile.save()
		self.close(True)
	
	def exit(self):
		self.close()
