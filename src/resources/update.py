#	-*-	coding:	utf-8	-*-
from imports import *

class checkupdate:

	def __init__(self, session):
		self.session = session

	def checkforupdate(self):
		try:
			getPage("http://master.dl.sourceforge.net/project/e2-mediaportal/version.txt").addCallback(self.gotUpdateInfo).addErrback(self.gotError)
		except Exception, error:
			print str(error)

	def gotError(self, error=""):
		return
		
	def gotUpdateInfo(self, html):
		tmp_infolines = html.splitlines()
		remoteversion = tmp_infolines[0]
		self.updateurl = tmp_infolines[1]
		if config.mediaportal.version.value < remoteversion:
			self.session.openWithCallback(self.startUpdate,MessageBox,_("An update is available for the MediaPortal Plugin!\nDo you want to download and install it now?"), MessageBox.TYPE_YESNO)
		else:
			return
			
	def startUpdate(self,answer):
		if answer is True:
			self.session.open(MPUpdateScreen,self.updateurl)
		else:
			return
		
class MPUpdateScreen(Screen):

	def __init__(self, session, updateurl):
		self.session = session
		self.updateurl = updateurl

		skin = """
		<screen name="MPUpdateScreen" position="0,0" size="1280,720" title="MediaPortal Update" backgroundColor="transparent" flags="wfNoBorder">
		<ePixmap position="215,110" size="850,500" zPosition="0" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/MP_update.png" alphatest="on" />
		<widget name="mplog" position="287,240" size="720,320" font="mediaportal;24" valign="top" halign="left" backgroundColor="#00000000" transparent="1" zPosition="1" />
		</screen>"""
		
		self.skin = skin
		
		self["mplog"] = ScrollLabel()

		Screen.__init__(self, session)

		self.onLayoutFinish.append(self.__onLayoutFinished)

	def __onLayoutFinished(self):
		sl = self["mplog"]
		sl.instance.setZPosition(1)
		self["mplog"].setText("Starting update, please wait...")
		self.startPluginUpdate()

	def startPluginUpdate(self):
		self.container=eConsoleAppContainer()
		self.container.appClosed.append(self.finishedPluginUpdate)
		self.container.stdoutAvail.append(self.mplog)
		#self.container.stderrAvail.append(self.mplog)
		#self.container.dataAvail.append(self.mplog)
		self.container.execute("opkg install --force-overwrite --force-depends " + str(self.updateurl))

	def finishedPluginUpdate(self,retval):
		config.mediaportal.filter.value = "ALL"
		config.mediaportal.filter.save()
		configfile.save()
		self.session.openWithCallback(self.restartGUI, MessageBox, _("MediaPortal successfully updated!\nDo you want to restart the Enigma2 GUI now?"), MessageBox.TYPE_YESNO)

	def restartGUI(self, answer):
		if answer is True:
			self.session.open(TryQuitMainloop, 3)
		else:
			self.close()
			
	def mplog(self,str):
		self["mplog"].setText(str)