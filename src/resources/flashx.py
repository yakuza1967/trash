import math
import re
import urllib2
from urllib import unquote
from urllib2 import urlopen, Request, HTTPError, URLError

class Flashx(object):

	headers = [
		('Accept', ('text/html,application/xhtml+xml,'
					'application/xml;q=0.9,*/*;q=0.8')),
		('User-Agent', ('Mozilla/5.0 (Windows NT 6.1; WOW64) '
						'AppleWebKit/537.36 (KHTML, like Gecko) '
						'Chrome/27.0.1453.15 Safari/537.36')),
		('Accept-Language', 'de-DE,de;q=0.8,en-US;q=0.6,en;q=0.4'),
		('Referer', 'http://play.flashx.tv')
	]

	def __init__(self):
		self.cookie = None

	def __c(self, c):
		d = ""
		for i in range(0, len(c)):
			if i % 3 == 0:
				d += '%'
			else:
				d += c[i]
		return d

	def __x(self, x, t):
		l = len(x)
		b = 1024
		i = j = p = s = w = 0
		j = math.ceil(l / b)
		r = ""
		while j > 0:
			j -= 1
			i = min(l, b)
			while i > 0:
				i -= 1
				l -= 1
				w |= t[ord(x[p]) - 48] << s
				p += 1
				if s:
					r += chr(165 ^ w & 255)
					w >>= 8
					s -= 2
				else:
					s = 6

		return r

	def __t(self, d):
		data = unquote(d)
		arr = re.findall('Array\((.*?)\)', data)
		if arr:
			t = [int(x) for x in re.findall("\d+", arr[0])]
			return t
		else:
			return []

	def __decodeX(self, c, x):
		d = self.__c(c)
		t = self.__t(d)
		html = self.__x(x, t)
		return html

	def __getData(self, url, decode=False, referer=None):
		data = None

		request = Request(url)
		for header in self.headers:
			request.add_header(*header)
		if referer:
			request.add_header('Referer', referer)
		if self.cookie:
			request.add_header('Cookie', self.cookie)
		try:
			response = urlopen(request)
			if response.headers.get('Set-Cookie'):
				self.cookie = response.headers.get('Set-Cookie')
			data = response.read()
		except HTTPError, error:
			print 'HTTPError: %s' % error
		except URLError, error:
			print 'URLError: %s' % error

		if not decode:
			return data
		if data != None:
			js = re.findall('<script language=javascript>c="(.*?)";.*?x\("(.*?)"', data)
			if js:
				c = js[0][0]
				x = js[0][1]
				html = self.__decodeX(c,x)
				newurl=resp.geturl()
				return html

		return data

	def getVidUrl(self, url):
		html = self.__getData(url, False)
		vidUrl = None
		if html:
			js = re.findall('class="auto-style6".*?<a href="(.*?)"', html, re.S)
			if js:
				html = self.__getData(js[0], False, url)
				if html:
					referer = js[0]
					js = re.findall('player.swf\?config=(.*?)"', html)
					if js:
						html = self.__getData('http://play.flashx.tv/player/soy.php', referer=referer)
						html = self.__getData(js[0], referer=referer)
						if html:
							js = re.findall('<file>(.*?)</file>', html)
							if js:
								vidUrl = js[0]

		return vidUrl