from twisted.web.client import Agent
from twisted.internet import reactor
from twisted.web.http_headers import Headers

agent_headers = {
	'User-Agent': ['Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.2.6) Gecko/20100627 Firefox/3.6.6'],
	'Accept-Charset': ['ISO-8859-1,utf-8;q=0.7,*;q=0.7'],
	'Accept': ['text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'],
	'Accept-Language': ['en-us,en;q=0.5'],
}

class GetRedirectedUrl:

	def __init__(self):
		print "GetRedirectedUrl:"
		self._cb_redir = None
		self.url = None
		self.agent = Agent(reactor)
		self.headers = Headers(agent_headers)
		
	def getRedirectedUrl(self, cb_redir, cb_err, url):
		print "getRedirectedUrl: ", url
		self._cb_redir = cb_redir
		self.url = url
		self.agent.request('HEAD', url, headers=self.headers).addCallback(self.getResponse).addErrback(cb_err)
	
	def getResponse(self, response):
		print "getResponse:"
		print "Status code: ", response.phrase
		#for header, value in response.headers.getAllRawHeaders():
		#	print header, value
			
		r = response.headers.getRawHeaders("location")
		if r:
			url = r[0]
		else:
			url = self.url
		print "Location: ", url
		
		self._cb_redir(url)
