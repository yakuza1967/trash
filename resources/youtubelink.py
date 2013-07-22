#	-*-	coding:	utf-8	-*-

from Components.config import config
from yt_url import *

class YoutubeLink:
	def __init__(self, session):
		print "YoutubeLink:"
		self.session = session
		self._callback = None
		self.title = ''
		self.videoPrio = int(config.mediaportal.youtubeprio.value)

	def getLink(self, cb_play, cb_err, title, url, imgurl):
		print "getLink:"
		print "VideoPrio: ", self.videoPrio
		self._callback = cb_play
		self.title = title
		y = youtubeUrl(self.session)
		y.addErrback(cb_err)
		link = y.getVideoUrl(url, self.videoPrio)
		self._callback(title, link, imgurl=imgurl)