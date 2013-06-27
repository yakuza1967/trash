from twisted.web.client import Agent, RedirectAgent
from twisted.internet import reactor
from twisted.web.http_headers import Headers
from twisted.internet.protocol import Protocol
from twisted.internet.defer import Deferred

agent_headers = {
	'User-Agent': ['Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.2.6) Gecko/20100627 Firefox/3.6.6'],
	'Accept-Charset': ['ISO-8859-1,utf-8;q=0.7,*;q=0.7'],
	'Accept': ['text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'],
	'Accept-Language': ['en-us,en;q=0.5'],
}

class TwAgentHelper:

	def __init__(self):
		print "GetRedirectedUrl:"
		self._callback = None
		self.url = None
		# can not follow rel. url redirects (location header)
		#self.agent = RedirectAgent(Agent(reactor))
		self.agent = Agent(reactor)
		self.headers = Headers(agent_headers)
		
	def getRedirectedUrl(self, callback, cb_err, url):
		print "getRedirectedUrl: ", url
		self._callback = callback
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
		
		self._callback(url)

	def getWebPage(self, callback, cb_err, url):
		print "getWebPage: ", url
		d = self.agent.request('GET', url, headers=self.headers)
		d.addCallback(self.getResource)
		d.addCallbacks(callback, cb_err)
		
	def getResource(self, response):
		print "getResource:"
		finished = Deferred()
		response.deliverBody(GetResource(finished))
		return finished
		
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
