#!/usr/bin/python

from DataContainer import DataContainer
from MongoConnector import MongoConnector
import sys
import json
import codecs
import logging

from optparse import OptionParser
from jsonpath_rw import parse
from pymongo import MongoClient

def processConfig(confData, mandatory, optionsrec, databaserec):
	## TODO: DETERMINE THE KEYS PRESENT IN THE FIELDS
	out=dict()
	for a in parse("$..fields").find(confData):
		for k in a.value:
			if k not in out:
				out[k]=None	
	#for k in allfields:
	#	print k
	#exit()
	res=confData["resources"]
	outfile=None
	if "WRITEFILE" in optionsrec:
		outfile=codecs.open(optionsrec["WRITEFILE"], "w", "utf-8")
	if "CALLGRAPHFILE" in optionsrec:
		callgraphfile=codecs.open(optionsrec["WRITEFILE"], "w", "utf-8")

	obj=DataContainer(res, out, mandatory, optionsrec, databaserec)
	obj.process()

#################### MAIN BLOCK #############################



parser = OptionParser()
#Done
parser.add_option("-c", "--config", dest="configfile",
                  help="Read repo config from local JSON file", metavar="FILE")

parser.add_option("-m", "--mandatory", dest="mandatoryfile",
                  help="Read mandatory fields from local JSON file", metavar="FILE")


parser.add_option("-M", "--mongodb", dest="mongodb",
                  help="Read repo and mandatory config from MONGO DB and maintain MONGO connection", metavar="DB")

#Done
parser.add_option("-w", "--writefile", dest="writefile",
                  help="Write to File", metavar="STRING")
##Done
#parser.add_option("-d", "--debug", dest="debug", help="Set debug level (logging.info,.debug,.warning,.error,.critical)", metavar="DEBUGLEVEL")

#Done
parser.add_option("-o", "--only", dest="only",
                  help="Focus on resource with specific field value supplied via -f, mutually exclusive with -s", metavar="STRING")

#Done
parser.add_option("-s", "--skip", dest="skip",
                  help="Skip resource with specific field value suppied via -f, mutually exclusive with -o", metavar="STRING")

#Done
parser.add_option("-f", "--field", dest="field",
                  help="field name for -o od -s", metavar="STRING")

parser.add_option("-i", "--ignore", dest="ignore",
                  help="Ignore specific config sections, i.e. terms, instances, etc", metavar="STRING")

#Done
parser.add_option("-F", "--first", dest="first",
                  help="Only download first page of results for each resource", action="store_true")

#Done
parser.add_option("-R", "--resume", action="store_true", dest="resume",
                  help="Only download resources not already in DB")

#Done
parser.add_option("-g", "--callgraph", dest="callgraph",
                  help="write callgraph to file", metavar="FILE")

parser.add_option("-l", "--loglevel", dest="loglevel",
                  help="Specify log level (INFO, DEBUG) default(logging.WARNING)", metavar="STRING")


(options, args) = parser.parse_args()

#print repr(options)
#print repr(args)

logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')
if options.loglevel in ["INFO", "DEBUG"]:
	logging.warning("Set loglevel to " + options.loglevel)
	for handler in logging.root.handlers[:]:
		logging.root.removeHandler(handler)
	logging.basicConfig(level=options.loglevel.upper(), format='%(asctime)s - %(levelname)s - %(message)s')

tCounter=0
if options.configfile != None or options.mongodb != None:

	optionsrec=dict()

	#Done
	FIRST=False
	if options.first:
        	optionsrec["FIRST"]=True

	### SKIP OR INCLUDE SPECIFIC THINGS ###

	# Done
        SKIP=None
        if options.skip != None:
		if options.field==None or options.only != None:
			parser.print_help()
		else:	
                	optionsrec["SKIP"]=options.skip
                	optionsrec["FIELD"]=options.field
    
	#Done 
	INCLUDE=None
        if options.only != None:
		if options.field==None or options.skip != None:
			parser.print_help()
		else:	
                	optionsrec["INCLUDE"]=options.only
                	optionsrec["FIELD"]=options.field

	# Done
	IGNORE=None
	if options.ignore != None:
		optionsrec["IGNORE"]=options.ignore

	#### WRITE TO FILE ####

	#Done 
	WRITEFILE=None
	if options.writefile != None:
		optionsrec["WRITEFILE"]=options.writefile

	#Done 
	CALLGRAPHFILE=None
	if options.callgraph != None:
		optionsrec["CALLGRAPHFILE"]=options.callgraph

	#### DB RELATED STUFF ###
        RESUME=False
        if options.resume:
                optionsrec["RESUME"]=True
	databaserec=None
        if options.mongodb != None:
		optionsrec["DBDRIVE"]=True
		mongoData=json.loads(open(options.mongodb).read())
		client = MongoClient(mongoData["host"], mongoData["port"])
		db = client[mongoData["db"]]

		

		databaserec=MongoConnector( { 	"classes"	: 	db[mongoData["classes"]],
						"classes_old"	: 	db[mongoData["classes_old"]], 
						"instances"	:	db[mongoData["instances"]],
						"instances_old"	:	db[mongoData["instances_old"]] } )

		logging.info("Read DB configuration from " + options.mongodb)

	mandatory=[]
	if options.mandatoryfile!=None:
		try:
			mandatory=json.loads(open(options.mandatoryfile).read())
		except:
			logging.warning("Failed to read file with mandatory field information.")
	
        confData=json.loads("{}")

        # Assume configfile provided via "-c" to always override DB read,
        # In that case, also do not write into db
        if options.configfile != None:
		try:
                	confData=json.loads(open(options.configfile).read())
              		logging.info("Read repo config from file " + options.configfile)
		except:
			logging.critical("Could not read repo configuration. Aborting.")
			exit(1)
        else:
		if optionsrec["DBDRIVE"]:
			collection = db[mongoData["registry"]]
			confData=collection.find()
                	logging.info("Read repo config from DB " + options.configfile)
		else:
			logging.critical("Could not read repo configuration. Aborting.")
			exit(1)
        #https://www.mongodb.com/blog/post/6-rules-of-thumb-for-mongodb-schema-design-part-1

        #print repr(confData)



        processConfig(confData, mandatory, optionsrec, databaserec)

else:
        parser.print_help()
	exit(1)

