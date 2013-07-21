#	-*-	coding:	utf-8	-*-

from imports import *

class MTVdeLink:

	def __init__(self, session):
		print "MTVdeLink:"
		self.session = session
		self._callback = None
		self.title = ''
		self.imgurl = ''

	def getLink(self, cb_play, cb_err, title, token, imgurl):
		self._callback = cb_play
		self.title = title
		self.imgurl = imgurl

		self.artist = ''
		p = title.find(' - ')
		if p > 0:
			self.artist = title[:p].strip()
			self.title = title[p+3:].strip()

		url = "http://api.mtvnn.com/v2/mrss?uri=mgid:sensei:video:mtvnn.com:music_video-%s-DE" % token
		data = urllib.urlopen(url).read()
		rtmpURL = re.findall("<media:content.*?url='(.*?)'>", data)
		if rtmpURL:
			data = urllib.urlopen(rtmpURL[0]).read()
			rtmpLink = re.findall('<src>(rtmp.*?)</src>', data)

		self._callback(self.title, rtmpLink[-1], imgurl=self.imgurl, artist=self.artist)