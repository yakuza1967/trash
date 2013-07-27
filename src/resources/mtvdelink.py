#	-*-	coding:	utf-8	-*-

#from imports import *
import re
from Plugins.Extensions.MediaPortal.resources.twagenthelper import TwAgentHelper

class MTVdeLink:

	tw_agent_hlp = TwAgentHelper()

	def __init__(self, session):
		print "MTVdeLink:"
		self.session = session
		self._callback = None

	def getLink(self, cb_play, cb_err, title, artist, token, imgurl):
		self._callback = cb_play
		self._errback = cb_err
		self.title = title
		self.artist = artist
		self.imgurl = imgurl

		#data = ''
		url = "http://api.mtvnn.com/v2/mrss?uri=mgid:sensei:video:mtvnn.com:music_video-%s-DE" % token

		"""
		try:
			data = urlopen2(url).read()
		except (URLError, HTTPException, socket.error), err:
			printl(err,self,"E")
			cb_err('MTVdeLink: Cannot get link!')
		"""
		self.tw_agent_hlp.getWebPage(self._parseData, cb_err, url, False)

	def _parseData(self, data):
		print "_parseData:"
		rtmpurl = re.search("<media:content.*?url='(.*?)'>", data)
		if rtmpurl:
			"""
			try:
				data = urlopen2(rtmpurl.group(1)).read()
			except (URLError, HTTPException, socket.error), err:
				printl(err,self,"E")
			"""
			self.tw_agent_hlp.getWebPage(self._parseData2, self._errback, rtmpurl.group(1), False)
		else:
			self._errback('MTVdeLink: Cannot get link!')

	def _parseData2(self, data):
		print "_parseData2:"
		rtmplink = re.findall('<src>(rtmp.*?)</src>', data)
		if rtmplink:
			videourl = rtmplink[-1] + ' swfUrl=http://player.mtvnn.com/g2/g2player_2.1.4.swf swfVfy=1'
		else:
			#videourl = None
			self._errback('MTVdeLink: Cannot get link!')

		self._callback(self.title, videourl, imgurl=self.imgurl, artist=self.artist)