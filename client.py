#coding: utf-8
import socket
import json
import zlib
from irpcexceptions import *

class IRPCClient:
	sck = None
	methodList = None
	host = None
	port = None
	timeout = None
	currentProc = None

	def __init__(self,host = "127.0.0.1", port = 54123, timeout = 2):
		self.host = host
		self.port = port
		self.timeout = timeout
		self.methodList = list()
		try:
			self.sck = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			self.sck.settimeout(self.timeout)
		except socket.error:
			print "Error creating socket"
			exit()
		self.getProcList()

	def remoteCaller(self, *args):
		arg = list(args)
		req = {"method" : self.currentProc, "params" : arg}
		result = self._sendRequest(json.dumps(req))
		res = None
		if result is not None:
			result = json.loads(result)
			if result["ok"]:
				res = result["result"]
			else:
				raise RemoteCallError
		else:
			raise RemoteCallError
		return res

	def _sendRequest(self, data):
		try:
			data = zlib.compress(data)
			self.sck.sendto(data, (self.host, self.port))
			data, conn = self.sck.recvfrom(65535)
			data = zlib.decompress(data)
		except socket.error:
			data = None
		return data

	def _placeholder(self, *args):
		pass

	def __getattr__(self,name):
		if name in self.methodList:
			self.currentProc = name
			return self.remoteCaller
		else:
			raise NoSuchMethod
			return self._placeholder

	def getProcList(self):
		lst = list()
		try:
			data = self._sendRequest('{"method" : "getProcList"}')
			try:
				self.methodList = json.loads(data)["result"]
			except (TypeError, KeyError, ValueError):
				raise ProcListError
		except socket.error:
			print "Error sending data"