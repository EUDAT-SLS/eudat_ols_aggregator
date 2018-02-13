from memory_profiler import profile

from pymongo import MongoClient
import hashlib
import logging
import urllib2
import sys

import string
printable = set(string.printable)

class MongoConnector:

	def __init__(self, dbDict):
		self.collections=dbDict

		
		
	#@profile
	def write(self, datarec):
		#check what we have here
		#datarec must contain "type" field

		#filter stuff
		htime=None
		outrec=dict()
		for k in datarec:
			if k not in ["apikey", "harvestDate"]:
				outrec[k]=datarec[k]
		htime=datarec["harvestDate"]
					

		#if isinstance(outrec["label"], list):
		#	outrec["label"]=list(set(outrec["label"]))
			
		#extremely bruteforce: remove all unprintable chars from termid
		datarec["termid"]=filter(lambda x: x in printable,  datarec["termid"])

		#create ID
		try:
                        t_id=str(None)
                        o_id=str(None)
                        if outrec["termid"]:
                                t_id=urllib2.quote(outrec["termid"])
                        if outrec["ontoiri"]:
                                o_id=urllib2.quote(outrec["ontoiri"])
                        term_onto_id = t_id + " " + o_id
                except:
                        logging.exception("Error quoting " + repr(outrec["termid"]) + " " + repr(outrec["ontoiri"]))
			return
                        #term_onto_id=str(outrec["termid"]) + " " + str(outrec["ontoiri"])		

		sha=hashlib.new("sha256")
                try:
                        sha.update(term_onto_id)
                except:
                        logging.exception("Exception updating sha for id " + repr(term_onto_id))
                        return

		outrec["_id"]=sha.hexdigest()

		#create a checksum over entry, not including harvest date
		sha2=hashlib.new("sha256")
		# ultra brute force
                sha2.update(repr(outrec))
		outrec["_checksum"]=sha2.hexdigest()

		# time is special, it shouldnt be included in the checksum
                outrec["harvestDate"]=htime


		# special case instances, we want to know 
		if outrec["type"]=="instances":
			outrec["classexists"]=False	
			existing=self.collections["classes"].find_one({"_id": outrec["_id"]})
			if existing:
				outrec["classexists"]=True

		try:
			self.checkInsertExisting(outrec)				
		except:
			logging.exception("Unexpected error writing MongoDB: " + str(sys.exc_info()[0]) + " " + repr(outrec))	

		#try cleanup
		htime=None
		outrec=None
		t_id=None
		o_id=None
		term_onto_id=None
		sha=None
		sha2=None
		


	def checkInsertExisting(self, outrec):
		existing=self.collections[outrec["type"]].find_one({"_id": outrec["_id"]})
		if existing:
			if outrec["_checksum"] != existing["_checksum"]:
				#new version detected, write old one to oldterms
				#redo -> maintain dictionary document with _id as key and dict as value, 
				#	 containing harvestdate:{fields} k,v pairs
				t_id_old = self.collections[outrec["type"]+"_old"].update({ "_id": existing["_id"] },{ "$push" : { "version" : dict((i,d[i]) for i in existing if i!='_id') }}, upsert=True).inserted_id
				#t_id_old = self.collections[outrec["type"]+"_old"].insert_one(existing).inserted_id
				self.collections[outrec["type"]].delete_one({"_id": existing["_id"]})
				t_id = self.collections[outrec["type"]].insert_one(outrec).inserted_id
			else:
				#just update harvest time
				self.collections[outrec["type"]].update({"_id": outrec["_id"]}, 
									{ "$set" : { "harvestDate" : outrec["harvestDate"] }}
									)
		else:
			t_id = self.collections[outrec["type"]].insert_one(outrec).inserted_id

	def findOne(self, query, type):
		existing=False
		existing=self.collections[type].find_one(query)
		return existing

	def find(self, query, type):
		return self.collections[type].find(query)

	def aggregate(self, query, type):
		return self.collections[type].aggregate(query)		

		
		
