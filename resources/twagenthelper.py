#	-*-	coding:	utf-8	-*-

import sys
if sys.version_info > (2, 6):
	from twisted.web.client import Agent, RedirectAgent
	from twisted.internet import reactor
	from twisted.web.http_headers import Headers
	from twisted.internet.protocol import Protocol
	from twisted.internet.defer import Deferred
	from twisted.web import http
	from urlparse import urlunparse
	
	agent_headers = {
		'User-Agent': ['Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.2.6) Gecko/20100627 Firefox/3.6.6'],
		'Accept-Charset': ['ISO-8859-1,utf-8;q=0.7,*;q=0.7'],
		'Accept': ['text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'],
		'Accept-Language': ['en-us,en;q=0.5'],
	}
	
	class GetResource(Protocol):
		def __init__(self, finished):
			print "GetResource:"
			self.data = ""
			self.finished = finished
		
		def dataReceived(self, data):
			print "dataReceived:"
			self.data += data
			#print data
		
		def connectionLost(self, reason):
			print "connectionLost: ", reason
			self.finished.callback(self.data)
else:
	from urllib2 import Request, urlopen, HTTPError
	

class TwAgentHelper:

	if sys.version_info > (2, 6):
	
		def __init__(self):
			print "GetRedirectedUrl:"
			self._callback = None
			self.url = None
			# can not follow rel. url redirects (location header)
			#self.agent = RedirectAgent(Agent(reactor))
			print "Twisted Agent in use"
			self.agent = Agent(reactor)
			self.headers = Headers(agent_headers)
		
		def getRedirectedUrl(self, callback, cb_err, url):
			print "getRedirectedUrl: ", url
			self._callback = callback
			self.url = url
			
			self.agent.request('HEAD', url, headers=self.headers).addCallback(self.__getResponse).addErrback(cb_err)
			
		def __getResponse(self, response):
			print "__getResponse:"
			print "Status code: ", response.phrase
			#for header, value in response.headers.getAllRawHeaders():
			#	print header, value
				
			r = response.headers.getRawHeaders("location")
			if r:
				url = r[0]
				p = self._parse(url)

				if b'http' not in p[0]:
					print "Rel. URL correction"
					scheme, host, port, path = self._parse(self.url)
					url = b'%s://%s/%s' % (scheme, host, url)
			else:
				url = self.url
			print "Location: ", url
			
			self._callback(url)

		def getWebPage(self, callback, cb_err, url):
			print "getWebPage: ", url
			d = self.agent.request('GET', url, headers=self.headers)
			d.addCallback(self.__getResource)
			d.addCallbacks(callback, cb_err)
			
		def __getResource(self, response):
			print "__getResource:"
			finished = Deferred()
			response.deliverBody(GetResource(finished))
			return finished
			
		@staticmethod
		def _parse(url, defaultPort=None):
			url = url.strip()
			parsed = http.urlparse(url)
			scheme = parsed[0]
			path = urlunparse(('', '') + parsed[2:])
		
			if defaultPort is None:
				if scheme == 'https':
					defaultPort = 443
				else:
					defaultPort = 80
		
			host, port = parsed[1], defaultPort
			if ':' in host:
				host, port = host.split(':')
				try:
					port = int(port)
				except ValueError:
					port = defaultPort
		
			if path == '':
				path = '/'
		
			return scheme, host, port, path

	else:
	
		def __init__(self):
			print "GetRedirectedUrl:"
			self._callback = None
			self.url = None
			print "Urllib2 in use"
			
		def getRedirectedUrl(self, callback, cb_err, url):
			print "getRedirectedUrl: ", url
			self._callback = callback
			self.url = url
			
			req = urllib2.Request(url)
			try:
				res = urllib2.urlopen(req)
			except urllib2.HTTPError, e:
				print e.code
				cb_err(e)
			else:
				r_url = res.geturl()
				callback(r_url)
				
		def getWebPage(self, callback, cb_err, url):
			cb_err('Twisted Agent not present')
