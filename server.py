#coding: utf-8
import socket
import json
import zlib
from irpcexceptions import *

class IRPCServer:
	
	sck = None
	methodDict = None
	host = None
	port = None

	def __init__(self, host = "127.0.0.1", port = 54123):
		self.methodDict = dict()
		self.host = host
		self.port = port
		self.sck = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.sck.bind((self.host, self.port))
		self.methodDict.update({"getProcList" : self.getProcList})

	def __getitem__(self,item):
		if self.methodDict.has_key(item):
			return self.methodDict[item]
		else:
			raise NoSuchMethod

	def __getattr__(self,name):
		if hasattr(self,name):
			return name
		else:
			raise NoSuchMethod

	def getProcList(self):
		lst = list()
		for method in self.methodDict:
			if method != "getProcList":
				lst.append(str(method))
		return lst

	def parseRequest(self,data):
		ok = True
		data = json.loads(data)
		name = data["method"]
		result = dict()
		res = None
		hasParams = False
		if data.has_key("params"):
			params = tuple(data["params"])
			hasParams = True
		if self.methodDict.has_key(name):
			if hasParams:
				res = self.methodDict[name](*params)
			else:
				res = self.methodDict[name]()
		else:
			ok = False
			res = ["NoSuchMethod"]
		result.update({"ok" : ok, "result" : res})
		result = json.dumps(result)
		return result

	def mainLoop(self):
		while True:
			data, addr = self.sck.recvfrom(65535)
			if not data:
				break
			data = zlib.decompress(data)
			res = self.parseRequest(data)
			res = zlib.compress(res)
			self.sck.sendto(res, addr)

	def registerProcedure(self, proc, name = None):
		if name is None:
			name = proc.__name__
		if not hasattr(self,name):
			dct = {name : proc}
			self.methodDict.update(dct)
			setattr(self,name,proc)
		else:
			raise MethodAlreadyExists

	def removeProcedure(self, name):
		if hasattr(self,name):
			delattr(self,name)
			try:
				self.methodDict.pop(name)
			except KeyError:
				pass
		else:
			raise NoSuchMethod