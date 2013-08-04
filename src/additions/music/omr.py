from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.simpleplayer import SimplePlayer

def omrGenreListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 50, 0, 800, 25, 0, RT_HALIGN_CENTER | RT_VALIGN_CENTER, entry[0])
		]

def omrListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 50, 0, 800, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry[0])
		]

kekse = {}

class showPlaylist(GUIComponent, object):
	GUI_WIDGET = eListbox
	
	def __init__(self):
		GUIComponent.__init__(self)
		self.l = eListboxPythonMultiContent()
		self.l.setFont(0, gFont('mediaportal', 23))
		self.l.setItemHeight(25)
		self.l.setBuildFunc(self.buildList)

	def buildList(self, entry):
		print entry
		width = self.l.getItemSize().width()
		res = [ None ]
		res.append((eListboxPythonMultiContent.TYPE_TEXT, 50, 0, 800, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry[0]))
		return res

	def getCurrent(self):
		cur = self.l.getCurrentSelection()
		return cur and cur[0]

	def postWidgetCreate(self, instance):
		instance.setContent(self.l)
		self.instance.setWrapAround(True)

	def preWidgetRemove(self, instance):
		instance.setContent(None)

	def setList(self, list):
		self.l.setList(list)

	def moveToIndex(self, idx):
		self.instance.moveSelectionTo(idx)
		
		
	def getSelectionIndex(self):
		return self.l.getCurrentSelectionIndex()

	def getSelectedIndex(self):
		return self.l.getCurrentSelectionIndex()

class omrGenreScreen(Screen):

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
		self.login = False
		
		self['title'] = Label("onlinemusicrecorder.com")
		self['ContentTitle'] = Label("Genre:")
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

		self.onLayoutFinish.append(self.startlogin)

	def startlogin(self):
		url = "http://www.onlinemusicrecorder.com/login.php?e=mediaportalAPI@squizzy.de&p=version470"
		getPage(url, cookies=kekse, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.read_login).addErrback(self.error)
		
	def read_login(self, data):
		if re.match('.*?You are logged in', data, re.S):
			self.login = True
			self.loadGenre()
		else:
			self.login = False
			self.loadGenre()
	
	def loadGenre(self):
		self.genreliste = [('A',"http://www.onlinemusicrecorder.com/archive/a.php"),
							('B',"http://www.onlinemusicrecorder.com/archive/b.php"),
							('C',"http://www.onlinemusicrecorder.com/archive/c.php"),
							('D',"http://www.onlinemusicrecorder.com/archive/d.php"),
							('E',"http://www.onlinemusicrecorder.com/archive/e.php"),
							('F',"http://www.onlinemusicrecorder.com/archive/f.php"),
							('G',"http://www.onlinemusicrecorder.com/archive/g.php"),
							('H',"http://www.onlinemusicrecorder.com/archive/h.php"),
							('I',"http://www.onlinemusicrecorder.com/archive/i.php"),
							('J',"http://www.onlinemusicrecorder.com/archive/j.php"),
							('K',"http://www.onlinemusicrecorder.com/archive/k.php"),
							('L',"http://www.onlinemusicrecorder.com/archive/l.php"),
							('M',"http://www.onlinemusicrecorder.com/archive/m.php"),
							('N',"http://www.onlinemusicrecorder.com/archive/n.php"),
							('O',"http://www.onlinemusicrecorder.com/archive/o.php"),
							('P',"http://www.onlinemusicrecorder.com/archive/p.php"),
							('Q',"http://www.onlinemusicrecorder.com/archive/q.php"),
							('R',"http://www.onlinemusicrecorder.com/archive/r.php"),
							('S',"http://www.onlinemusicrecorder.com/archive/s.php"),
							('T',"http://www.onlinemusicrecorder.com/archive/t.php"),
							('U',"http://www.onlinemusicrecorder.com/archive/u.php"),
							('V',"http://www.onlinemusicrecorder.com/archive/v.php"),
							('W',"http://www.onlinemusicrecorder.com/archive/w.php"),
							('X',"http://www.onlinemusicrecorder.com/archive/x.php"),
							('Y',"http://www.onlinemusicrecorder.com/archive/y.php"),
							('Z',"http://www.onlinemusicrecorder.com/archive/z.php")]
							
		self.chooseMenuList.setList(map(omrGenreListEntry, self.genreliste))
		self.keyLocked = False

	def error(self, error):
		print error
	
	def keyOK(self):
		if self.keyLocked:
			return
			
		if not self.login:
			message = self.session.open(MessageBox, _("Login ERROR."), MessageBox.TYPE_INFO, timeout=5)
			
		self.omrName = self['genreList'].getCurrent()[0][0]
		omrUrl = self['genreList'].getCurrent()[0][1]
		print self.omrName, omrUrl

		self.session.open(omrListeScreen, self.omrName, omrUrl)

	def keyCancel(self):
		self.close()

class omrListeScreen(Screen):

	def __init__(self, session, omrName, omrUrl):
		self.session = session
		self.omrName = omrName
		self.omrUrl = omrUrl

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

		self['title'] = Label("onlinemusicrecorder.com")
		self['ContentTitle'] = Label("Auswahl:")
		self['name'] = Label("")
		self['F1'] = Label("Exit")
		self['F2'] = Label("")
		self['F3'] = Label("")
		self['F4'] = Label("")
		self['F3'].hide()
		self['F4'].hide()

		self.keyLocked = True
		self.videoliste = []
		self['genreList'] = showPlaylist()
		
		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		print "hole daten"
		self.keyLocked = True
		getPage(self.omrUrl, cookies=kekse, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.loadPageData).addErrback(self.dataError)

	def loadPageData(self, data):
		self.playlist = []
		ok = re.findall("</div><div id='div_filtertable'><b><a href='javascript.*?onclick=\"x_get.'(recordings.php\?.*?)','div_content'.\">(.*?)</a></b>(.*?)</div><div id='div_filtertable'>", data, re.S)
		for each in ok:
			songs = re.findall("'(recordings.php.*?)\'.*?div_content.*?>(.*?)</a>", each[2], re.S)
			for title in songs:
				name = "%s - %s" % (each[1], title[1])
				url = "http://www.onlinemusicrecorder.com/%s" % title[0]
				self.videoliste.append(((decodeHtml(name), url),))
				self.playlist.append((decodeHtml(name), url))
				
			self['genreList'].setList(self.videoliste)
			self.keyLocked = False

	def dataError(self, error):
		printl(error,self,"E")
		
	def keyOK(self):
		if self.keyLocked:
			return

		idx = self['genreList'].getSelectedIndex()
		self.session.open(omrPlayer, self.playlist, int(idx) , True, "test")

	def keyCancel(self):
		self.close()

class omrPlayer(SimplePlayer):

	def __init__(self, session, playList, playIdx=0, playAll=True, listTitle=None):
		print "omrPlayer:"

		SimplePlayer.__init__(self, session, playList, playIdx=playIdx, playAll=playAll, listTitle=listTitle, ltype='omr')

		self.onLayoutFinish.append(self.getVideo)

	def getVideo(self):
		print self.playIdx
		print self.playList[self.playIdx][0][0]
		self.ntitle = self.playList[self.playIdx][0]
		url = self.playList[self.playIdx][1]
		print self.title, url.replace(' ', '%20')
		getPage(url.replace(' ', '%20'), cookies=kekse, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.get_link).addErrback(self.dataError)

	def get_link(self, data):
		url = re.findall("'(get_omr.php.*?)'", data, re.S)
		if url:
			url = "http://www.onlinemusicrecorder.com/%s" % url[0]
			print url
			getPage(url, cookies=kekse, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.get_stream).addErrback(self.dataError)
			
	def get_stream(self, data):
		stream_url = re.findall("<a href='(.*?)'>", data, re.S)
		if stream_url:
			print stream_url[0]
			self.playStream(self.ntitle, stream_url[0])

	def dataError(self, error):
		printl(error,self,"E")