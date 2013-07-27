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
			self.session.openWithCallback(self.startPluginUpdate,MessageBox,_("An update is available for the MediaPortal Plugin!\nDo you want to download and install it now?"), MessageBox.TYPE_YESNO)
		else:
			return

	def startPluginUpdate(self, answer):
		if answer is True:
			self.container=eConsoleAppContainer()
			self.container.appClosed.append(self.finishedPluginUpdate)
			self.container.execute("opkg install --force-overwrite --force-depends " + str(self.updateurl))
		else:
			return

	def finishedPluginUpdate(self,retval):
		config.mediaportal.filter.value = "ALL"
		config.mediaportal.filter.save()
		configfile.save()
		self.session.openWithCallback(self.restartGUI, MessageBox, _("MediaPortal successfully updated!\nDo you want to restart the Enigma2 GUI now?"), MessageBox.TYPE_YESNO)

	def restartGUI(self, answer):
		if answer is True:
			self.session.open(TryQuitMainloop, 3)
		else:
			return