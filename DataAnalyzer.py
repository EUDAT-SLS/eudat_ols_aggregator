import codecs
import copy
import gzip
import time
import datetime
import json

class DataAnalyzer:

	def __init__(self, dbobj):

		self.dbobj=dbobj

	def stringToList(self, indata):
		#we expect list or string
		if isinstance(indata, (list, tuple)):
			return indata
		else:
			return [indata]

	def alignTerms(self, ctid, cl, cs, cd, cr, labs, which, labtype, log, out, counter):
		for term in labs:
			query= { "$text": { "$search": "\""+term+"\"" }}

			log.write(str(counter) + ": Searching for overlaps for " + which + " query:  " + repr(query) + "\n")
			log.flush()
			#matching=termcollection.find(query)

			matchcoll=[]

			for type in ["classes", "instances"]:
				log.write("Retrieving " + type + " for not " + which + "\n")
				#matching=self.dbobj.find({ "ontoprefix" : { "$ne" : which }  }, type)
				matching=self.dbobj.find(query, type)

				#tranfer from cursor to array
				log.write("Retrieved " + str(matching.count()) + " " + type + " for query " + json.dumps(query) + "\n")
				for m in matching:
		
					matchcoll.append(m)

			#code.interact(local=locals())
			for match in matchcoll:

				mtid=""
				ml=""
				ms=[]
				md=[]
				mo=""
				mr=""


				try:
					mtid=match["termid"]
				except:
					log.write("Error getting match match termid"+"\n")
				try:
					ml=self.stringToList(match["label"])
				except:
					log.write("Error getting match match label"+"\n")
				try:
					ms=self.stringToList(match["synonyms"])
				except:
					log.write("Error getting match match synonyms"+"\n")
					pass
				try:
					md=self.stringToList(match["description"])
				except:
					log.write("Error getting match match descriptions"+"\n")
				try:
					mo=match["ontoprefix"]
				except:
					log.write("Error getting match match onto prefix"+"\n")
				try:
					mr=match["reponame"]
				except:
					log.write("Error getting match match reponame"+"\n")


				if not mtid:
					mtid=""
				if not ml:
					ml=""
				if not mo:
					mo=""
				if not mr:
					mr=""


				#skip if same
				if ctid==mtid:
					continue


				#check if search term is in result
				labelMatch=0

				matchPrefs=[]
				if ml != None:
					for pref in ml:
						try:
							matchPrefs.append(pref.strip().lower())
						except AttributeError, e:
							log.write("Error stripping ml " + repr(pref) + ", " + str(e.message) + "\n")
							pass
						except:
							log.write("Error stripping ml " + repr(pref) + "\n")
							pass
					

				matchSyns=[]
				if ms != None:
					for syn in ms:
						try:
							matchSyns.append(syn.strip().lower())
						except AttributeError, e:
							log.write("Error stripping syn " + repr(syn) + ", " + str(e.message) + "\n")
							pass
						except:
							log.write("Error stripping syn " + repr(syn) + "\n")
							pass
				

				self.checkMatchWrite(term, matchPrefs, ctid, cl, cs, cd, cr, mtid, ml, ms, md, mo, mr, (labtype<<1)+1, log, out)
				self.checkMatchWrite(term, matchSyns, ctid, cl, cs, cd, cr, mtid, ml, ms, md, mo, mr, (labtype<<1), log, out)

	def checkMatchWrite(self, term, matchlist, ctid, cl, cs, cd, cr, mtid, ml, ms, md, mo, mr, matchtype, log, out):
		tl=term.lower()
		labelMatch=0
		if tl in matchlist:
			labelMatch=1+matchtype
		outstring=ctid + "\t" + json.dumps(cl) + "\t" + \
			json.dumps(cs) + "\t" + json.dumps(cd) + "\t" + \
			cr + "\t" + \
			mtid + "\t" + json.dumps(ml) + "\t" + \
			json.dumps(ms) + "\t" + json.dumps(md) + "\t" + \
			mo + "\t" + mr + "\t" + str(labelMatch) + "\t" + str(len(tl)) + "\n"

		#try gzipped
		out.write(unicode(outstring).encode('utf-8'))
		#out.write(outstring)
		#out.flush()



		
	def alignResource(self, which):				
	
		calltime=datetime.datetime.now()

		log=codecs.open(which+"_align_all_lab."+calltime.strftime("%d%m%Y_%H:%M:%S")+".log", "w", "utf-8")#, buffering=0)

		# try gzipped
		#out=codecs.open(which+"_align_all_lab."+calltime.strftime("%d%m%Y_%H:%M:%S")+".tsv", "w", "utf-8")#, buffering=0)
		out=gzip.open(which+"_align_all_lab."+calltime.strftime("%d%m%Y_%H:%M:%S")+".tsv.gz", "wb")

		log.write("Align resource " + which + " with the others\n")
		log.flush()
		#get all concepts for the resource

		conceptcoll=[]
		start_t=time.time()
		counter=1
		numOfConcepts=0

		for type in ["classes", "instances"]:
			log.write("Retrieving " + type + " for " + which + "\n")
			concepts=self.dbobj.find({ "ontoprefix" : which  }, type)

			#tranfer from cursor to array
			for concept in concepts:
				conceptcoll.append(concept)

			numOfConcepts+=concepts.count()

		log.write("Iterating through " + str(len(conceptcoll)) + " concepts\n")
		log.flush()

		for concept in conceptcoll:
			# find matching preflabs

			#check if everything is there
			ctid=""
			cl=""
			cs=[]
			cd=[]
			cr=""

			try:
				ctid=concept["termid"]
			except:
				log.write("Error getting search concept termid")
			try:
				cl=self.stringToList(concept["label"])
			except:
				log.write("Error getting search concept label")
			try:
				cs=self.stringToList(concept["synonyms"])
			except:
				log.write("Error getting search concept synonyms")
				pass
			try:
				cd=self.stringToList(concept["description"])
			except:
				log.write("Error getting search concept descriptions")
				pass
			try:
				cr=concept["reponame"]
			except:
				log.write("Error getting search concept reponame")

			if not ctid:
				ctid=""
			if not cl:
				cl=""
			if not cr:
				mr=""

			preflab=[]
			for pl in cl:
				try:
					preflab.append(pl.strip())
				except:
					log.write("Cant strip pl " + repr(pl))
					pass

			synstrip=[]
			for syn in cs:
				try:
					synstrip.append(syn.strip())
				except:
					log.write("Cant strip syn " + repr(syn))	
					pass

			#query= {"label" : { "$in" : [ preflab ] }}
			#query= {"$or" : [ { "label": preflab } ] }
			#query= {"ontoprefix": { "$ne": which }, "$or" : [ { "label": preflab } ] }

			#labPlusSyn=synstrip[:]
			#labPlusSyn=labPlusSyn+preflab

			#add call here
			self.alignTerms(ctid, cl, cs, cd, cr, preflab[:], which, 1, log, out, counter)
			self.alignTerms(ctid, cl, cs, cd, cr, synstrip[:], which, 0, log, out, counter)

			elapsed_t=datetime.timedelta(0, time.time()-start_t)
			avg_search=elapsed_t.total_seconds()/float(counter)

			log.write("avg search " + str(avg_search) + \
				" total: " + str(elapsed_t.total_seconds()) + \
				" estimated: " + str(avg_search*float(numOfConcepts-counter))+"\n")
			log.flush()

			counter+=1
		out.close()
		log.close()
	

