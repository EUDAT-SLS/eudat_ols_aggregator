
import resource

from memory_profiler import profile

from pympler import asizeof, summary, muppy

from operator import itemgetter

import urllib2
import logging
import json
import re
import copy
import sys
import time
import datetime
import codecs
import gc 
import code

from jsonpath_rw import parse 
from bson import json_util

import commonFuncs
import traceback

class DataContainer:

	dbrec		=	None
	fieldnames	=	None
	mandatory	=	None
	optionsrec	=	None
	outputfile	=	None

	previous=None
	oldmsg=None
	oldlvl=""
	accum=1
	
	def __init__(self, config, data, fieldnames=None, mandatory=None, optionsrec=None, dbrec=None, level=-1):
		self.config=config
		self.indata=data
		self.linecount=0
		self.parseTab=dict()
		self.level=level+1

		if fieldnames:
			DataContainer.fieldnames=fieldnames
		if mandatory:
			DataContainer.mandatory=mandatory
		if optionsrec:
			DataContainer.optionsrec=optionsrec
		if dbrec:
			DataContainer.dbrec=dbrec
		if optionsrec:
	        	if "WRITEFILE" in optionsrec:
				if not DataContainer.outputfile:
					DataContainer.outputfile=codecs.open(optionsrec["WRITEFILE"], "w", "utf-8")

	def checkReplace(self, url, data):
        	replacements=re.compile("<.*?>")
        	tokens=replacements.findall(url)
        	out_url=url
        	for t in tokens:
        	        ts=t.strip("<>")
        	        try:
        	                out_url = out_url.replace(t, data[ts])
        	        except:
        	                logging.warning("Key " + t + " not found in curRep. " + self.infostr)
        	                pass
        	return out_url

	
	def download(self, url):
		# The URL MUST return JSON
		logging.debug("Downloading " + url + " Memory usage : %s (kb)" % resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
		response=None
		
		try:
			response=json.loads(commonFuncs.urlopen_with_retry(url).read())
			logging.debug("Download complete, Memory usage : %s (kb)" % resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
		except urllib2.HTTPError, e:
	 		logging.warning(url + " FAILED with code " + str(e.code))
			return response
		except urllib2.URLError, e:
			logging.warning(url + " FAILED with args " + str(e.args))
			return response
		except ValueError, e:
			logging.warning(url + " Json Decode FAILED with args " + str(e.args))
			return response
		return response 

	def parseField(self, field, fields, response, outdata):
		if response != None:
			#we need to extract via jsonPATH, precompute path is MUCH faster

			# maintain oject dict with path lookup, parse each path exactly once per object lifetime
			path=fields[field]["path"]
			if path not in self.parseTab:
				self.parseTab[path]=parse(path)
		
			
			try:
				extract=self.parseTab[path].find(response)
				if len(extract)>0:
					outdata[field]=extract[0].value
			except:
				logging.warning("Couldn't parse field: " + field + " " +  str(sys.exc_info()[0]) + " " +  self.infostr)
	
	def getStaticValue(self, field, fields, outdata):
		# we read in static info directly
		outdata[field]=fields[field]["path"]


	def extractFields(self, fields, outdata, response=None):
		for field in fields:
			#print "Getting field " + field
			if field in outdata:
				if outdata[field]:
					logging.warning("Data field " + field + " already defined. " +  self.infostr) 
			if fields[field]["type"]=="static":#
				self.getStaticValue(field, fields, outdata)
			else:
				self.parseField(field, fields, response, outdata)


	def getExtra(self, extra, outdata):
		response=None
		if "url" not in extra:
			logging.warning("Extra without URL. " +  self.infostr )
		else:
			response = self.download(self.checkReplace(extra["url"]["path"], outdata))
		if response:
			logging.debug("Got extra info from" +  self.checkReplace(extra["url"]["path"], outdata))	
		if "fields" in extra:
			for field in extra["fields"]: 
				self.parseField(field, extra["fields"], response, outdata)
		response=None
			
	def writeObject(self, outdata):
		if DataContainer.outputfile != None:
			DataContainer.outputfile.write(json.dumps(outdata, default=json_util.default) + ",\n")
		if DataContainer.dbrec != None:
			DataContainer.dbrec.write(outdata)
		if not DataContainer.outputfile and not DataContainer.dbrec:
			logging.debug(repr(outdata))

	def missingMandatory(self, outdata, res, response):
		ret=False
		for m in DataContainer.mandatory:
			if m not in outdata:
				logging.warning("Missing mandatory field " + m + " " +  self.infostr)
				ret=True
			else:
				if not outdata[m]:
					logging.warning("Missing mandatory field " + m + " " +  self.infostr)
					ret=True
		return ret

	def skipIncludeTest(self,outdata):
		hit = False
		# SKIP/INCLUDE CHECKS
		if "SKIP" in DataContainer.optionsrec:
			for skipfield in DataContainer.optionsrec["SKIP"]:
				if skipfield in outdata:
					if outdata[skipfield]:
						if outdata[skipfield] in DataContainer.optionsrec["SKIP"][skipfield]:
							hit=True
							logging.debug("SKIP " + skipfield + " with val " + outdata[skipfield])

		if "INCLUDE" in DataContainer.optionsrec:
			for includefield in DataContainer.optionsrec["INCLUDE"]:
				if includefield in outdata:
					if outdata[includefield]:
						if outdata[includefield] not in DataContainer.optionsrec["INCLUDE"][includefield]:
							hit=True
						if hit:
							logging.debug("IGNORE " + outdata[includefield] + " because not in Include list.")
		
		return hit

	def initProcessDataContainer(self, what, outdata, level):
		#Initialize object
		obj=DataContainer(what, outdata, None, level=level)
		obj.process()
		obj=None
		gc.collect()
		logging.debug("initProcessDataContainer: Memory usage : %s (kb)" % resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
		


	def processObject(self, res, outdata, response=None):
		if "config" in res:
			self.extractFields(res["config"], outdata, response)
		if "fields" in res:
			self.extractFields(res["fields"], outdata, response)

		if self.skipIncludeTest(outdata):
			return	

		if "extra" in res:
			for ext in res["extra"]:
				self.getExtra(ext, outdata)
	
	
		if "resources" in res:
			if self.skipIncludeTest(outdata):
				return	
			self.initProcessDataContainer(res["resources"],outdata, self.level)
		else:
			#NO RESOURCES .... WE NEED TO PUEBLISH
			if not self.missingMandatory(outdata, res, response):

				#writing object, applying time
				outdata["harvestDate"]=datetime.datetime.utcnow()

				self.writeObject(outdata)
				self.linecount+=1
			#in case of really big resources, it is good to check for progress once in a while
			# arbitrary choice: every 10000th term
			if self.linecount % 10000 == 0:
				logging.info(str(self.linecount) + " terms written to DB. " + self.infostr)

				
	def iterateUrl(self, res, url):
		while url:

			myt=time.time()
			download_url=self.checkReplace(url, self.indata)
			response=self.download(download_url)
			logging.debug("Downloading took " + str(int(time.time()-myt)) + " sec ")
	
			objlist=None
			if "list" in res:
				try:
					objlist=parse(res["list"]["path"]).find(response)[0].value
				except:
					logging.warning("Couldnt parse objlist. " +  self.infostr)
			else:
				objlist=response
		
			if objlist==None:
				logging.warning("Objlist is empty. " +  self.infostr)
				return
	
			
			for obj in objlist:
				outdata=copy.deepcopy(self.indata)
				self.processObject(res, outdata, obj)
	
			if len(objlist)==0:
				logging.warning("Got empty result set for url" + "\t" + download_url +"\t" +  self.infostr)
				self.zeroResCount+=1
	
			if self.zeroResCount==5:
				logging.warning("Got " + str(self.zeroResCount) + " empty results in series, aborting." +  self.infostr)
				return
	
			url = None
			if "next" in res and not "FIRST" in DataContainer.optionsrec:
				try:
					url=parse(res["next"]["path"]).find(response)[0].value
				except:
					logging.info("No next page link found, last page likely " +  self.infostr)
			objlist=None
			response=None

		logging.debug("IterateUrl: Memory usage : %s (kb)" % resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)

	def process(self):
		#get printable version of indata
		self.infostr=""
		for t in self.indata:
			if self.indata[t]:
				self.infostr=self.infostr+"|"+t+":"+self.indata[t]
		for res in self.config:
			curt=time.time()
			self.linecount=0
			#check for URL
			if "level" in res:
				#Check IGNORE option
				if "IGNORE" in DataContainer.optionsrec:
					if res["level"]["path"] in DataContainer.optionsrec["IGNORE"]:
						logging.debug("IGNORING LEVEL " + res["level"]["path"])
						continue

				self.indata["type"]=res["level"]["path"]

				#TODO: not optimal solution: eg. type:instances appears after type:classes in logfile
				self.infostr=self.infostr+"|type:"+self.indata["type"]

				if "RESUME" in DataContainer.optionsrec:
					#check skip -> We are at the lowest level
					if not "resources" in res:
						existing=False
						if DataContainer.dbrec != None:
							reddict=dict((k,v) for k,v in self.indata.iteritems() if k in DataContainer.fieldnames and v is not None)
							logging.debug("Looking for existing resource " + repr(reddict))
							#try:
							#	key=raw_input("ENTER KEY :")
							#except:
							#	pass
							existing=DataContainer.dbrec.findOne(reddict,
											     res["level"]["path"])
						if existing:
							logging.warning("Resume option set, Skipping existing resource " + json.dumps(self.indata))
							continue

				logging.info("GETTING LEVEL " + res["level"]["path"] + " " + self.infostr)
		
			if "url" not in res:
				#No URL, we assume that there is exactly one "thing" (Here usually a Repository)
				outdata=copy.deepcopy(self.indata)
				self.processObject(res, outdata)
			else:
				#get response url
				self.zeroResCount=0	
				self.iterateUrl(res, res["url"]["path"])	

				#after iteration, do some object counting
				all_objects = muppy.get_objects(include_frames=True)
				sum1 = summary.summarize(all_objects)
				#code.interact(local=locals())
				totalmem=0
				counter=0
				for entry in sorted(sum1, key=itemgetter(2), reverse=True):
					out=""
					for data in entry:
						out=out+"\t"+str(data)
					totalmem+=entry[2]
					if counter < 15:
						logging.debug(out)
					counter+=1	

				logging.debug("TOTAL MEM : " + str(totalmem))

				logging.debug("Process: Memory usage : %s (kb)" % resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)

				

			logging.info(str(self.linecount) + " terms written to DB in " + str(int(time.time()-curt)) + " sec. " + self.infostr)

